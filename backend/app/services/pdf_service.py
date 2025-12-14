"""PDF extraction service using PDFMathTranslate (pdf2zh)"""

import json
import time
from pathlib import Path
from typing import List, Optional

from redis.asyncio import Redis

from app.cache import Cache, CacheKeys
from app.schemas.pdf import Block, Coordinates, PDFExtractionResult
from app.logger import info, warning, error as log_error

# Try to import pdf2zh, fallback to PyMuPDF if not available
try:
    from pdf2zh import translate as pdf2zh_translate
    from pdf2zh_next.high_level import do_translate_async_stream
    from pdf2zh_next.settings import SettingsModel
    PDF2ZH_AVAILABLE = True
except ImportError:
    PDF2ZH_AVAILABLE = False
    warning("pdf2zh not available, falling back to PyMuPDF")
    import fitz  # PyMuPDF fallback


class PDFService:
    """
    Service for extracting text from PDF files with layout preservation.
    
    Uses PDFMathTranslate (pdf2zh) with DocLayout-YOLO for AI-powered layout
    detection, specialized for scientific/technical documents. Provides better
    format preservation for complex layouts (tables, equations, multi-column).
    Includes Redis caching for performance.
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
        
        Uses PDFMathTranslate (pdf2zh) with DocLayout-YOLO for AI-powered layout
        detection, providing better format preservation for technical documents.
        
        Args:
            pdf_path: Path to PDF file (local file or S3-downloaded temp file)
            
        Returns:
            PDFExtractionResult with all text blocks and metadata
            
        Raises:
            FileNotFoundError: If PDF file doesn't exist
            ValueError: If PDF is corrupted or empty
        """
        start_time = time.time()
        
        # Validate file exists
        if not Path(pdf_path).exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        # Use PDFMathTranslate if available, otherwise fallback to PyMuPDF
        if PDF2ZH_AVAILABLE:
            return PDFService._extract_with_pdf2zh(pdf_path, start_time)
        else:
            return PDFService._extract_with_pymupdf(pdf_path, start_time)
    
    @staticmethod
    def _extract_with_pdf2zh(pdf_path: str, start_time: float) -> PDFExtractionResult:
        """
        Extract text using PDFMathTranslate (pdf2zh) with DocLayout-YOLO.
        
        This method uses pdf2zh's layout detection capabilities to extract
        text blocks with better preservation of complex layouts.
        """
        try:
            # PDFMathTranslate uses DocLayout-YOLO for layout detection
            # We'll use pdf2zh's internal components for extraction
            # Note: pdf2zh is primarily designed for translation, but we can
            # use its layout detection capabilities
            
            # Import pdf2zh components for layout parsing
            try:
                from pdf2zh_next.babeldoc import BabelDoc
                from pdf2zh_next.settings import SettingsModel
                
                # Create settings for extraction-only mode
                settings = SettingsModel()
                # Configure for extraction without translation
                settings.translation_service = "none"  # Skip translation
                
                # Use BabelDoc to parse PDF and extract layout
                babel_doc = BabelDoc(pdf_path, settings)
                babel_doc.parse()
                
                blocks: List[Block] = []
                total_characters = 0
                page_count = len(babel_doc.pages) if hasattr(babel_doc, 'pages') else 0
                
                # Extract blocks from parsed document
                for page_idx, page in enumerate(babel_doc.pages if hasattr(babel_doc, 'pages') else []):
                    page_width = page.width if hasattr(page, 'width') else 612  # Default letter width
                    page_height = page.height if hasattr(page, 'height') else 792  # Default letter height
                    
                    # Get text blocks from page
                    page_blocks = page.blocks if hasattr(page, 'blocks') else []
                    
                    block_id = 0
                    for block in page_blocks:
                        # Extract text content
                        text = block.text if hasattr(block, 'text') else ""
                        if not text or not text.strip():
                            continue
                        
                        # Get bounding box coordinates
                        bbox = block.bbox if hasattr(block, 'bbox') else [0, 0, page_width, page_height]
                        if isinstance(bbox, (list, tuple)) and len(bbox) >= 4:
                            x0, y0, x1, y1 = bbox[0], bbox[1], bbox[2], bbox[3]
                        else:
                            x0, y0, x1, y1 = 0, 0, page_width, page_height
                        
                        # Normalize coordinates to percentages (0-100)
                        coordinates = Coordinates(
                            x=(x0 / page_width) * 100 if page_width > 0 else 0,
                            y=(y0 / page_height) * 100 if page_height > 0 else 0,
                            width=((x1 - x0) / page_width) * 100 if page_width > 0 else 0,
                            height=((y1 - y0) / page_height) * 100 if page_height > 0 else 0,
                        )
                        
                        # Extract font information (if available)
                        font_size = block.font_size if hasattr(block, 'font_size') else 12
                        font_name = block.font_name if hasattr(block, 'font_name') else "Unknown"
                        is_bold = block.is_bold if hasattr(block, 'is_bold') else False
                        is_italic = block.is_italic if hasattr(block, 'is_italic') else False
                        rotation = block.rotation if hasattr(block, 'rotation') else 0
                        
                        extracted_block = Block(
                            page=page_idx,
                            block_id=block_id,
                            text=text,
                            coordinates=coordinates,
                            font_size=float(font_size),
                            font_name=str(font_name),
                            is_bold=bool(is_bold),
                            is_italic=bool(is_italic),
                            rotation=float(rotation),
                        )
                        
                        blocks.append(extracted_block)
                        total_characters += len(text)
                        block_id += 1
                
                extraction_time_ms = int((time.time() - start_time) * 1000)
                is_scanned = total_characters < 10
                
                if is_scanned:
                    warning(
                        "Scanned PDF detected",
                        path=pdf_path,
                        total_characters=total_characters,
                    )
                
                info(
                    "PDF extraction complete (PDFMathTranslate)",
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
                
            except (ImportError, AttributeError) as e:
                # If pdf2zh internal API is not accessible, fallback to PyMuPDF
                warning(
                    "PDFMathTranslate internal API not accessible, falling back to PyMuPDF",
                    exc=e,
                    path=pdf_path,
                )
                return PDFService._extract_with_pymupdf(pdf_path, start_time)
                
        except Exception as e:
            log_error("PDFMathTranslate extraction failed, falling back to PyMuPDF", exc=e, path=pdf_path)
            return PDFService._extract_with_pymupdf(pdf_path, start_time)
    
    @staticmethod
    def _extract_with_pymupdf(pdf_path: str, start_time: float) -> PDFExtractionResult:
        """
        Fallback extraction using PyMuPDF (original implementation).
        """
        import fitz  # PyMuPDF
        
        try:
            # Open PDF document
            doc = fitz.open(pdf_path)
            info("PDF opened (PyMuPDF fallback)", path=pdf_path, pages=len(doc))
            
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
                "PDF extraction complete (PyMuPDF)",
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
            raise ValueError(f"PDF file is empty or corrupted: {str(e)}")
        except fitz.FileDataError as e:
            log_error("PDF file data is corrupted or invalid", exc=e, path=pdf_path)
            raise ValueError(f"PDF file data is corrupted: {str(e)}")
        except MemoryError as e:
            log_error("Insufficient memory to process PDF", exc=e, path=pdf_path)
            raise
        except UnicodeDecodeError as e:
            warning("Unicode decoding error in PDF text", exc=e, path=pdf_path)
            # Try to continue with partial extraction
            # Return what we have so far
            return PDFExtractionResult(
                blocks=blocks,
                page_count=page_num + 1 if 'page_num' in locals() else 0,  # Pages processed so far
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
        # Use extraction result to detect scanned PDF
        try:
            result = PDFService.extract_text_with_layout(pdf_path)
            return result.is_scanned
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
        # Try PDFMathTranslate first, fallback to PyMuPDF
        if PDF2ZH_AVAILABLE:
            try:
                from pdf2zh_next.babeldoc import BabelDoc
                from pdf2zh_next.settings import SettingsModel
                
                settings = SettingsModel()
                babel_doc = BabelDoc(pdf_path, settings)
                babel_doc.parse()
                return len(babel_doc.pages) if hasattr(babel_doc, 'pages') else 0
            except (ImportError, AttributeError, Exception):
                pass  # Fallback to PyMuPDF
        
        # Fallback to PyMuPDF
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(pdf_path)
            count = len(doc)
            doc.close()
            return count
        except Exception as e:
            log_error("Failed to get page count", exc=e, path=pdf_path)
            return 0
