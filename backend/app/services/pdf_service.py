"""PDF extraction service using PyMuPDF"""

import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List, Optional

import fitz  # PyMuPDF
from redis.asyncio import Redis

from app.cache import Cache, CacheKeys
from app.schemas.pdf import Block, Coordinates, PDFExtractionResult
from app.logger import info, warning, error as log_error


class PDFService:
    """
    Service for extracting text from PDF files with layout preservation.
    
    Uses PyMuPDF (fitz) to extract text blocks with coordinates, font info,
    and formatting. Supports multi-column detection and handles edge cases
    like scanned PDFs and rotated text. Includes Redis caching for performance.
    """

    # Cache expiration: 24 hours
    CACHE_EXPIRATION_SECONDS = 24 * 60 * 60

    @staticmethod
    async def extract_text_with_layout_cached(
        pdf_path: str,
        translation_id: str,
        redis: Redis,
        force_refresh: bool = False,
    ) -> PDFExtractionResult:
        """
        Extract text from PDF with caching support.
        
        Args:
            pdf_path: Path to PDF file
            translation_id: Translation job ID for cache key
            redis: Redis client for caching
            force_refresh: If True, bypass cache and re-extract
            
        Returns:
            PDFExtractionResult (from cache or fresh extraction)
        """
        cache = Cache(redis)
        cache_key = CacheKeys.blocks(translation_id)
        
        # Try to get from cache first (unless force refresh)
        if not force_refresh:
            cached_data = await cache.get_json(cache_key)
            if cached_data:
                info("PDF extraction result loaded from cache", translation_id=translation_id)
                return PDFService._deserialize_extraction_result(cached_data)
        
        # Extract from PDF
        result = PDFService.extract_text_with_layout(pdf_path)
        
        # Cache the result
        try:
            serialized = PDFService._serialize_extraction_result(result)
            await cache.set_json(cache_key, serialized, PDFService.CACHE_EXPIRATION_SECONDS)
            info("PDF extraction result cached", translation_id=translation_id, cache_ttl=PDFService.CACHE_EXPIRATION_SECONDS)
        except Exception as e:
            warning("Failed to cache PDF extraction result", exc=e, translation_id=translation_id)
        
        return result

    @staticmethod
    def _serialize_extraction_result(result: PDFExtractionResult) -> dict:
        """Serialize PDFExtractionResult to JSON-compatible dict"""
        return {
            "blocks": [
                {
                    "page": block.page,
                    "block_id": block.block_id,
                    "text": block.text,
                    "coordinates": {
                        "x": block.coordinates.x,
                        "y": block.coordinates.y,
                        "width": block.coordinates.width,
                        "height": block.coordinates.height,
                    },
                    "font_size": block.font_size,
                    "font_name": block.font_name,
                    "is_bold": block.is_bold,
                    "is_italic": block.is_italic,
                    "rotation": block.rotation,
                }
                for block in result.blocks
            ],
            "page_count": result.page_count,
            "is_scanned": result.is_scanned,
            "total_characters": result.total_characters,
            "extraction_time_ms": result.extraction_time_ms,
        }

    @staticmethod
    def _deserialize_extraction_result(data: dict) -> PDFExtractionResult:
        """Deserialize dict to PDFExtractionResult"""
        blocks = [
            Block(
                page=b["page"],
                block_id=b["block_id"],
                text=b["text"],
                coordinates=Coordinates(**b["coordinates"]),
                font_size=b["font_size"],
                font_name=b["font_name"],
                is_bold=b["is_bold"],
                is_italic=b["is_italic"],
                rotation=b["rotation"],
            )
            for b in data["blocks"]
        ]
        
        return PDFExtractionResult(
            blocks=blocks,
            page_count=data["page_count"],
            is_scanned=data["is_scanned"],
            total_characters=data["total_characters"],
            extraction_time_ms=data["extraction_time_ms"],
        )

    @staticmethod
    async def update_extraction_progress(
        redis: Redis,
        job_id: str,
        current_page: int,
        total_pages: int,
    ) -> None:
        """
        Update extraction progress in Redis for status polling.
        
        Args:
            redis: Redis client
            job_id: Translation job ID
            current_page: Current page being processed
            total_pages: Total number of pages
        """
        cache = Cache(redis)
        progress_key = CacheKeys.job_progress(job_id)
        
        progress_data = {
            "stage": "extraction",
            "current_page": current_page,
            "total_pages": total_pages,
            "progress_percent": int((current_page / total_pages) * 100) if total_pages > 0 else 0,
        }
        
        await cache.set_json(progress_key, progress_data, expire_seconds=3600)  # 1 hour

    @staticmethod
    def extract_text_with_layout(pdf_path: str) -> PDFExtractionResult:
        """
        Extract text from PDF with full layout and formatting information.
        
        Args:
            pdf_path: Path to PDF file (local file or S3-downloaded temp file)
            
        Returns:
            PDFExtractionResult with all text blocks and metadata
            
        Raises:
            FileNotFoundError: If PDF file doesn't exist
            fitz.EmptyFileError: If PDF is corrupted or empty
        """
        start_time = time.time()
        
        # Validate file exists
        if not Path(pdf_path).exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        try:
            # Open PDF document
            doc = fitz.open(pdf_path)
            info("PDF opened", path=pdf_path, pages=len(doc))
            
            blocks: List[Block] = []
            total_characters = 0
            
            # Extract text from each page
            for page_num in range(len(doc)):
                page = doc[page_num]
                page_width = page.rect.width
                page_height = page.rect.height
                
                # Get text with detailed layout information
                text_dict = page.get_text("dict")
                
                # Process each block on the page
                block_id = 0
                for block in text_dict.get("blocks", []):
                    # Only process text blocks (type 0), skip images (type 1)
                    if block.get("type") != 0:
                        continue
                    
                    # Extract text from lines within the block
                    text_lines = []
                    font_info = None
                    
                    for line in block.get("lines", []):
                        line_text = ""
                        for span in line.get("spans", []):
                            line_text += span.get("text", "")
                            # Capture font info from first span
                            if not font_info:
                                font_info = {
                                    "size": span.get("size", 12),
                                    "font": span.get("font", "Unknown"),
                                    "flags": span.get("flags", 0),
                                }
                        text_lines.append(line_text)
                    
                    text = "\n".join(text_lines).strip()
                    
                    # Skip empty blocks
                    if not text:
                        continue
                    
                    # Get block coordinates (bbox = bounding box)
                    bbox = block.get("bbox", [0, 0, page_width, page_height])
                    x0, y0, x1, y1 = bbox
                    
                    # Normalize coordinates to percentages (0-100)
                    coordinates = Coordinates(
                        x=(x0 / page_width) * 100,
                        y=(y0 / page_height) * 100,
                        width=((x1 - x0) / page_width) * 100,
                        height=((y1 - y0) / page_height) * 100,
                    )
                    
                    # Extract font information
                    font_size = font_info["size"] if font_info else 12
                    font_name = font_info["font"] if font_info else "Unknown"
                    font_flags = font_info["flags"] if font_info else 0
                    
                    # Decode font flags (bitwise)
                    # Bit 0: superscript, Bit 1: italic, Bit 2: serifed, Bit 4: monospaced, Bit 5: bold
                    is_bold = bool(font_flags & (1 << 5))  # Bit 5
                    is_italic = bool(font_flags & (1 << 1))  # Bit 1
                    
                    # Get text rotation (if any)
                    rotation = block.get("rotation", 0)
                    
                    # Create block object
                    extracted_block = Block(
                        page=page_num,
                        block_id=block_id,
                        text=text,
                        coordinates=coordinates,
                        font_size=font_size,
                        font_name=font_name,
                        is_bold=is_bold,
                        is_italic=is_italic,
                        rotation=rotation,
                    )
                    
                    blocks.append(extracted_block)
                    total_characters += len(text)
                    block_id += 1
            
            # Calculate extraction time
            extraction_time_ms = int((time.time() - start_time) * 1000)
            
            # Get actual page count before closing
            page_count = len(doc)
            
            # Close document
            doc.close()
            
            # Detect if PDF is scanned (no extractable text)
            is_scanned = total_characters < 10  # Very low character count
            
            if is_scanned:
                warning(
                    "Scanned PDF detected",
                    path=pdf_path,
                    total_characters=total_characters,
                )
            
            info(
                "PDF extraction complete",
                path=pdf_path,
                blocks=len(blocks),
                characters=total_characters,
                time_ms=extraction_time_ms,
            )
            
            return PDFExtractionResult(
                blocks=blocks,
                page_count=page_count,
                is_scanned=is_scanned,
                total_characters=total_characters,
                extraction_time_ms=extraction_time_ms,
            )
            
        except fitz.EmptyFileError as e:
            log_error("PDF file is empty or corrupted", exc=e, path=pdf_path)
            raise
        except fitz.FileDataError as e:
            log_error("PDF file data is corrupted or invalid", exc=e, path=pdf_path)
            raise
        except MemoryError as e:
            log_error("Insufficient memory to process PDF", exc=e, path=pdf_path)
            raise
        except UnicodeDecodeError as e:
            warning("Unicode decoding error in PDF text", exc=e, path=pdf_path)
            # Try to continue with partial extraction
            # Return what we have so far
            return PDFExtractionResult(
                blocks=blocks,
                page_count=page_num + 1,  # Pages processed so far
                is_scanned=False,
                total_characters=total_characters,
                extraction_time_ms=int((time.time() - start_time) * 1000),
            )
        except Exception as e:
            log_error("PDF extraction failed", exc=e, path=pdf_path)
            raise

    @staticmethod
    def detect_scanned_pdf(pdf_path: str) -> bool:
        """
        Detect if a PDF is scanned (image-based) with no extractable text.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            True if PDF appears to be scanned
        """
        try:
            doc = fitz.open(pdf_path)
            
            # Sample first 3 pages (or all pages if less than 3)
            sample_pages = min(3, len(doc))
            total_text = ""
            
            for page_num in range(sample_pages):
                page = doc[page_num]
                total_text += page.get_text()
            
            doc.close()
            
            # If very few characters extracted, likely scanned
            return len(total_text.strip()) < 50
            
        except Exception as e:
            log_error("Failed to detect scanned PDF", exc=e, path=pdf_path)
            return False

    @staticmethod
    def get_page_count(pdf_path: str) -> int:
        """
        Get the number of pages in a PDF.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Number of pages
        """
        try:
            doc = fitz.open(pdf_path)
            count = len(doc)
            doc.close()
            return count
        except Exception as e:
            log_error("Failed to get page count", exc=e, path=pdf_path)
            return 0
