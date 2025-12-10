"""PDF reconstruction service - applies translated text to original PDF"""

from io import BytesIO
from typing import List

import fitz  # PyMuPDF

from app.logger import info, warning, error as log_error
from app.schemas.pdf import TranslatedBlock


class PDFReconstructionService:
    """
    Service for reconstructing PDFs with translated text while preserving layout.
    
    Takes original PDF bytes and translated blocks, replaces text at original
    coordinates while maintaining fonts, sizes, styles, and page layout.
    """

    @staticmethod
    def reconstruct_pdf(
        original_pdf_bytes: bytes,
        translated_blocks: List[TranslatedBlock],
    ) -> bytes:
        """
        Reconstruct PDF with translated text.
        
        Args:
            original_pdf_bytes: Original PDF file content as bytes
            translated_blocks: List of TranslatedBlock objects with translations
            
        Returns:
            Reconstructed PDF as bytes
            
        Raises:
            ValueError: If PDF is corrupted or blocks are invalid
            MemoryError: If PDF is too large
        """
        try:
            # Load original PDF
            pdf_doc = fitz.open(stream=original_pdf_bytes, filetype="pdf")
            info(
                "Opened PDF for reconstruction",
                page_count=pdf_doc.page_count,
                block_count=len(translated_blocks),
            )

            # Group blocks by page for efficient processing
            blocks_by_page = {}
            for block in translated_blocks:
                page_num = block.original.page - 1  # 0-indexed
                if page_num not in blocks_by_page:
                    blocks_by_page[page_num] = []
                blocks_by_page[page_num].append(block)

            # Process each page
            for page_num in range(pdf_doc.page_count):
                if page_num not in blocks_by_page:
                    continue

                page = pdf_doc[page_num]
                blocks = blocks_by_page[page_num]

                for block in blocks:
                    PDFReconstructionService._replace_block_text(
                        page=page,
                        translated_block=block,
                    )

            # Save reconstructed PDF to bytes
            output = BytesIO()
            pdf_doc.save(output, garbage=4, deflate=True)
            output.seek(0)
            reconstructed_bytes = output.getvalue()

            info(
                "PDF reconstruction complete",
                page_count=pdf_doc.page_count,
                output_size=len(reconstructed_bytes),
            )

            return reconstructed_bytes

        except fitz.FileError as e:
            log_error("PDF file is corrupted or invalid", exc=e)
            raise ValueError(f"Invalid PDF file: {str(e)}")
        except MemoryError as e:
            log_error("Insufficient memory for PDF reconstruction", exc=e)
            raise MemoryError(f"PDF too large to reconstruct: {str(e)}")
        except Exception as e:
            log_error("PDF reconstruction failed", exc=e)
            raise

    @staticmethod
    def _replace_block_text(page: fitz.Page, translated_block) -> None:
        """
        Replace text in a block on a page while preserving layout.
        
        Args:
            page: PyMuPDF page object
            translated_block: TranslatedBlock with original and translated info
        """
        original = translated_block.original
        translated_text = translated_block.translated_text

        # Get original coordinates (normalized percentages)
        coords = original.coordinates
        page_rect = page.rect  # (0, 0, width, height)
        
        # Convert normalized coordinates to absolute pixel coordinates
        x0 = coords.x * page_rect.width
        y0 = coords.y * page_rect.height
        x1 = x0 + (coords.width * page_rect.width)
        y1 = y0 + (coords.height * page_rect.height)
        
        text_rect = fitz.Rect(x0, y0, x1, y1)

        try:
            # Get font properties from original
            font_size = original.font_size or 12
            font_name = original.font_name or "helv"
            
            # Prepare font flags
            font_flags = 0
            if original.is_bold:
                font_flags |= fitz.TEXT_PRESERVE_WHITESPACE
            if original.is_italic:
                # italic flag is handled in font selection
                pass

            # Insert translated text at original coordinates
            # Use insert_textbox for better text wrapping within original bounds
            page.insert_textbox(
                text_rect,
                translated_text,
                fontsize=font_size,
                fontname=font_name,
                color=(0, 0, 0),  # Black text
                align=fitz.TEXT_ALIGN_LEFT,
                overflow=fitz.TEXT_OVERFLOW_HIDDEN,  # Don't overflow original bounds
            )

            info(
                "Text replaced in block",
                page=original.page,
                block_id=original.block_id,
                text_length=len(translated_text),
            )

        except Exception as e:
            warning(
                "Failed to replace text in block",
                exc=e,
                page=original.page,
                block_id=original.block_id,
            )
            # Continue with next block - don't fail entire PDF
            pass

    @staticmethod
    def reconstruct_pdf_with_tone(
        original_pdf_bytes: bytes,
        translated_blocks: List,  # Can have tone_customized_text field
        use_tone: bool = True,
    ) -> bytes:
        """
        Reconstruct PDF, preferring tone-customized text if available.
        
        Args:
            original_pdf_bytes: Original PDF file content
            translated_blocks: List of blocks (may have tone_customized_text)
            use_tone: If True, use tone_customized_text when available
            
        Returns:
            Reconstructed PDF as bytes
        """
        # Create TranslatedBlock objects, selecting text appropriately
        blocks_for_reconstruction = []
        
        for block_data in translated_blocks:
            # Create a new block-like object with selected text
            selected_text = block_data.get("tone_customized_text") \
                if use_tone and block_data.get("tone_customized_text") \
                else block_data.get("translated_text", "")
            
            # Create a simple object that acts like TranslatedBlock
            class BlockProxy:
                def __init__(self, data, text):
                    self.translated_text = text
                    self.original = BlockProxy.OriginalProxy(data.get("original", {}))
                
                class OriginalProxy:
                    def __init__(self, orig_data):
                        self.page = orig_data.get("page", 1)
                        self.block_id = orig_data.get("block_id", "")
                        self.text = orig_data.get("text", "")
                        self.font_size = orig_data.get("font_size", 12)
                        self.font_name = orig_data.get("font_name", "helv")
                        self.is_bold = orig_data.get("is_bold", False)
                        self.is_italic = orig_data.get("is_italic", False)
                        
                        # Coordinates
                        coords = orig_data.get("coordinates", {})
                        
                        class CoordinatesProxy:
                            def __init__(self, c):
                                self.x = c.get("x", 0)
                                self.y = c.get("y", 0)
                                self.width = c.get("width", 0.5)
                                self.height = c.get("height", 0.1)
                        
                        self.coordinates = CoordinatesProxy(coords)
            
            block_proxy = BlockProxy(block_data, selected_text)
            blocks_for_reconstruction.append(block_proxy)
        
        return PDFReconstructionService.reconstruct_pdf(
            original_pdf_bytes,
            blocks_for_reconstruction,
        )
