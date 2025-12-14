"""PDF reconstruction service - applies translated text to original PDF using PDFMathTranslate"""

from io import BytesIO
from typing import List

from app.logger import info, warning, error as log_error
from app.schemas.pdf import TranslatedBlock

# Try to import pdf2zh, fallback to PyMuPDF if not available
try:
    from pdf2zh_next.babeldoc import BabelDoc
    from pdf2zh_next.settings import SettingsModel
    PDF2ZH_AVAILABLE = True
except ImportError:
    PDF2ZH_AVAILABLE = False
    warning("pdf2zh not available for reconstruction, falling back to PyMuPDF")
    import fitz  # PyMuPDF fallback


PYMUPDF_BUILTIN_FONTS = {
    "helv", "heit", "cour", "coit", "tiro", "tiit", "tibo", "tibi",
    "symb", "zadb", "Helvetica", "Helvetica-Bold", "Helvetica-Oblique",
    "Helvetica-BoldOblique", "Courier", "Courier-Bold", "Courier-Oblique",
    "Courier-BoldOblique", "Times-Roman", "Times-Bold", "Times-Italic",
    "Times-BoldItalic", "Symbol", "ZapfDingbats",
}


class PDFReconstructionService:
    """
    Service for reconstructing PDFs with translated text while preserving layout.
    
    Uses PDFMathTranslate (pdf2zh) for better format preservation of complex
    layouts (tables, equations, multi-column). Takes original PDF bytes and
    translated blocks, replaces text at original coordinates while maintaining
    fonts, sizes, styles, and page layout.
    """
    
    @staticmethod
    def _get_safe_font(font_name: str | None) -> str:
        """Return a valid PyMuPDF font, falling back to helv if unknown."""
        if not font_name:
            return "helv"
        if font_name in PYMUPDF_BUILTIN_FONTS:
            return font_name
        lower = font_name.lower()
        if "bold" in lower and "italic" in lower:
            return "Helvetica-BoldOblique"
        if "bold" in lower:
            return "Helvetica-Bold"
        if "italic" in lower or "oblique" in lower:
            return "Helvetica-Oblique"
        return "helv"

    @staticmethod
    def reconstruct_pdf(
        original_pdf_bytes: bytes,
        translated_blocks: List[TranslatedBlock],
    ) -> bytes:
        """
        Reconstruct PDF with translated text using PDFMathTranslate.
        
        Args:
            original_pdf_bytes: Original PDF file content as bytes
            translated_blocks: List of TranslatedBlock objects with translations
            
        Returns:
            Reconstructed PDF as bytes
            
        Raises:
            ValueError: If PDF is corrupted or blocks are invalid
            MemoryError: If PDF is too large
        """
        # Use PDFMathTranslate if available, otherwise fallback to PyMuPDF
        if PDF2ZH_AVAILABLE:
            return PDFReconstructionService._reconstruct_with_pdf2zh(
                original_pdf_bytes, translated_blocks
            )
        else:
            return PDFReconstructionService._reconstruct_with_pymupdf(
                original_pdf_bytes, translated_blocks
            )
    
    @staticmethod
    def _reconstruct_with_pdf2zh(
        original_pdf_bytes: bytes,
        translated_blocks: List[TranslatedBlock],
    ) -> bytes:
        """
        Reconstruct PDF using PDFMathTranslate (pdf2zh).
        
        Uses PDFMathTranslate's reconstruction capabilities for better
        format preservation of complex layouts.
        """
        try:
            import tempfile
            from pathlib import Path
            
            # Save original PDF to temp file for pdf2zh processing
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_input:
                tmp_input.write(original_pdf_bytes)
                tmp_input_path = tmp_input.name
            
            try:
                # Use PDFMathTranslate for reconstruction
                # Note: pdf2zh is designed for translation, but we can use it
                # for reconstruction by providing translated blocks
                
                from pdf2zh_next.babeldoc import BabelDoc
                from pdf2zh_next.settings import SettingsModel
                
                # Create settings
                settings = SettingsModel()
                
                # Load and parse original PDF
                babel_doc = BabelDoc(tmp_input_path, settings)
                babel_doc.parse()
                
                # Apply translated blocks to the document
                # Map translated blocks to document blocks
                blocks_by_page = {}
                for block in translated_blocks:
                    page_num = block.original.page
                    if page_num not in blocks_by_page:
                        blocks_by_page[page_num] = []
                    blocks_by_page[page_num].append(block)
                
                # Update document with translated text
                for page_idx, page in enumerate(babel_doc.pages if hasattr(babel_doc, 'pages') else []):
                    if (page_idx + 1) in blocks_by_page:
                        page_blocks = page.blocks if hasattr(page, 'blocks') else []
                        translated_page_blocks = blocks_by_page[page_idx + 1]
                        
                        # Match and update blocks
                        for translated_block in translated_page_blocks:
                            # Find matching block in page
                            block_id = translated_block.original.block_id
                            if block_id < len(page_blocks):
                                page_blocks[block_id].text = translated_block.translated_text
                
                # Reconstruct PDF
                output_path = tmp_input_path.replace(".pdf", "_reconstructed.pdf")
                babel_doc.save(output_path)
                
                # Read reconstructed PDF
                with open(output_path, "rb") as f:
                    reconstructed_bytes = f.read()
                
                # Clean up temp files
                Path(output_path).unlink(missing_ok=True)
                
                info(
                    "PDF reconstruction complete (PDFMathTranslate)",
                    output_size=len(reconstructed_bytes),
                    block_count=len(translated_blocks),
                )
                
                return reconstructed_bytes
                
            except (ImportError, AttributeError) as e:
                # If pdf2zh internal API is not accessible, fallback to PyMuPDF
                warning(
                    "PDFMathTranslate reconstruction API not accessible, falling back to PyMuPDF",
                    exc=e,
                )
                return PDFReconstructionService._reconstruct_with_pymupdf(
                    original_pdf_bytes, translated_blocks
                )
            finally:
                # Clean up input temp file
                Path(tmp_input_path).unlink(missing_ok=True)
                
        except Exception as e:
            log_error("PDFMathTranslate reconstruction failed, falling back to PyMuPDF", exc=e)
            return PDFReconstructionService._reconstruct_with_pymupdf(
                original_pdf_bytes, translated_blocks
            )
    
    @staticmethod
    def _reconstruct_with_pymupdf(
        original_pdf_bytes: bytes,
        translated_blocks: List[TranslatedBlock],
    ) -> bytes:
        """
        Fallback reconstruction using PyMuPDF (original implementation).
        """
        import fitz  # PyMuPDF
        
        try:
            # Load original PDF
            pdf_doc = fitz.open(stream=original_pdf_bytes, filetype="pdf")
            info(
                "Opened PDF for reconstruction (PyMuPDF fallback)",
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

                # First, add redaction annotations for all blocks on this page
                # This marks all original text areas for removal
                for block in blocks:
                    PDFReconstructionService._add_redaction_for_block(
                        page=page,
                        translated_block=block,
                    )
                
                # Apply all redactions at once (more efficient than one-by-one)
                page.apply_redactions()
                
                # Additional step: Draw white rectangles to ensure original text is covered
                # This is a fallback in case redaction doesn't fully remove text
                for block in blocks:
                    PDFReconstructionService._cover_block_area(
                        page=page,
                        translated_block=block,
                    )
                
                # Now insert all translated text
                for block in blocks:
                    PDFReconstructionService._insert_translated_text(
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

        except Exception as e:
            if hasattr(fitz, 'FileError') and isinstance(e, fitz.FileError):
                log_error("PDF file is corrupted or invalid", exc=e)
                raise ValueError(f"Invalid PDF file: {str(e)}")
            elif isinstance(e, MemoryError):
                log_error("Insufficient memory for PDF reconstruction", exc=e)
                raise MemoryError(f"PDF too large to reconstruct: {str(e)}")
            else:
                log_error("PDF reconstruction failed", exc=e)
                raise

    @staticmethod
    def _add_redaction_for_block(page, translated_block) -> None:
        """
        Add redaction annotation to mark original text for removal.
        
        Uses both coordinate-based redaction and text search to ensure
        the original text is properly removed.
        
        Args:
            page: PyMuPDF page object (or PDFMathTranslate page object)
            translated_block: TranslatedBlock with original coordinates
        """
        import fitz  # PyMuPDF
        
        original = translated_block.original

        # Get original coordinates (normalized percentages)
        coords = original.coordinates
        page_rect = page.rect  # (0, 0, width, height)
        
        # Convert normalized coordinates to absolute pixel coordinates
        x0 = (coords.x / 100) * page_rect.width
        y0 = (coords.y / 100) * page_rect.height
        x1 = x0 + ((coords.width / 100) * page_rect.width)
        y1 = y0 + ((coords.height / 100) * page_rect.height)
        
        text_rect = fitz.Rect(x0, y0, x1, y1)

        try:
            # First, try to find and redact the actual text instances
            # Search for the original text on the page
            original_text = original.text.strip()
            if original_text:
                # Search for text instances that overlap with our coordinates
                text_instances = page.search_for(
                    original_text,
                    flags=fitz.TEXT_DEHYPHENATE,
                )
                
                # Redact text instances that are within our block area
                for inst in text_instances:
                    # Check if this text instance overlaps with our block area
                    if text_rect.intersects(inst):
                        page.add_redact_annot(inst, fill=(1, 1, 1))
            
            # Also add redaction for the coordinate area as fallback
            # This ensures we cover the area even if text search doesn't find it
            page.add_redact_annot(text_rect, fill=(1, 1, 1))
            
        except Exception as e:
            warning(
                "Failed to add redaction for block",
                exc=e,
                page=original.page,
                block_id=original.block_id,
            )

    @staticmethod
    def _cover_block_area(page, translated_block) -> None:
        """
        Draw a white rectangle over the block area to ensure original text is covered.
        This is a fallback after redaction to ensure text is completely hidden.
        
        Args:
            page: PyMuPDF page object (or PDFMathTranslate page object)
            translated_block: TranslatedBlock with original coordinates
        """
        import fitz  # PyMuPDF
        
        original = translated_block.original

        # Get original coordinates (normalized percentages)
        coords = original.coordinates
        page_rect = page.rect
        
        # Convert normalized coordinates to absolute pixel coordinates
        x0 = (coords.x / 100) * page_rect.width
        y0 = (coords.y / 100) * page_rect.height
        x1 = x0 + ((coords.width / 100) * page_rect.width)
        y1 = y0 + ((coords.height / 100) * page_rect.height)
        
        text_rect = fitz.Rect(x0, y0, x1, y1)

        try:
            # Draw a white rectangle to cover the area
            shape = page.new_shape()
            shape.draw_rect(text_rect)
            shape.finish(fill=(1, 1, 1), color=(1, 1, 1))  # White fill and stroke
            shape.commit()
        except Exception as e:
            warning(
                "Failed to cover block area",
                exc=e,
                page=original.page,
                block_id=original.block_id,
            )

    @staticmethod
    def _insert_translated_text(page, translated_block) -> None:
        """
        Insert translated text at the original block coordinates.
        
        Args:
            page: PyMuPDF page object (or PDFMathTranslate page object)
            translated_block: TranslatedBlock with original and translated info
        """
        import fitz  # PyMuPDF
        
        original = translated_block.original
        translated_text = translated_block.translated_text

        # Validate that we have translated text
        if not translated_text or not translated_text.strip():
            warning(
                "No translated text available for block",
                page=original.page,
                block_id=original.block_id,
                original_text=original.text[:50] if original.text else "",
            )
            return

        # Get original coordinates (normalized percentages)
        coords = original.coordinates
        page_rect = page.rect  # (0, 0, width, height)
        
        # Convert normalized coordinates to absolute pixel coordinates
        x0 = (coords.x / 100) * page_rect.width
        y0 = (coords.y / 100) * page_rect.height
        x1 = x0 + ((coords.width / 100) * page_rect.width)
        y1 = y0 + ((coords.height / 100) * page_rect.height)
        
        text_rect = fitz.Rect(x0, y0, x1, y1)

        try:
            # Get font properties from original, with safe fallback
            font_size = original.font_size or 12
            font_name = PDFReconstructionService._get_safe_font(original.font_name)
            
            # Insert translated text at original coordinates
            # Use insert_textbox for better text wrapping within original bounds
            # Note: insert_textbox automatically handles overflow by not displaying text that doesn't fit
            result = page.insert_textbox(
                text_rect,
                translated_text,
                fontsize=font_size,
                fontname=font_name,
                color=(0, 0, 0),  # Black text
                align=fitz.TEXT_ALIGN_LEFT,
            )

            if result < 0:
                # insert_textbox returns negative if text doesn't fit
                warning(
                    "Text did not fit in block, trying alternative insertion",
                    page=original.page,
                    block_id=original.block_id,
                    text_length=len(translated_text),
                )
                # Try inserting without overflow constraint
                page.insert_text(
                    (x0, y0),
                    translated_text,
                    fontsize=font_size,
                    fontname=font_name,
                    color=(0, 0, 0),
                )

            info(
                "Text replaced in block",
                page=original.page,
                block_id=original.block_id,
                text_length=len(translated_text),
                original_preview=original.text[:30] if original.text else "",
                translated_preview=translated_text[:30],
            )

        except Exception as e:
            warning(
                "Failed to insert translated text in block",
                error=str(e),
                error_type=type(e).__name__,
                page=original.page,
                block_id=original.block_id,
                translated_text_preview=translated_text[:50] if translated_text else "",
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
            
            # Log if translated_text is missing or empty
            if not selected_text or not selected_text.strip():
                warning(
                    "Block missing translated text",
                    block_id=block_data.get("original", {}).get("block_id", "unknown"),
                    has_tone=bool(block_data.get("tone_customized_text")),
                    has_translated=bool(block_data.get("translated_text")),
                )
            
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
