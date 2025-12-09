"""Tests for PDF extraction service"""

import io
from pathlib import Path
from unittest.mock import MagicMock, patch

import fitz
import pytest

from app.services.pdf_service import PDFService
from app.schemas.pdf import Block, Coordinates, PDFExtractionResult


@pytest.fixture
def sample_pdf_path(tmp_path):
    """Create a simple PDF file for testing"""
    # Create a minimal PDF with PyMuPDF
    pdf_path = tmp_path / "test.pdf"
    doc = fitz.open()
    
    # Add a page with some text
    page = doc.new_page(width=612, height=792)  # Letter size
    
    # Insert text at different positions
    page.insert_text((72, 100), "Hello World", fontsize=12)
    page.insert_text((72, 150), "This is a test PDF", fontsize=14, fontname="helv")
    page.insert_text((72, 200), "Multiple lines", fontsize=10)
    
    # Save PDF
    doc.save(str(pdf_path))
    doc.close()
    
    return str(pdf_path)


@pytest.fixture
def multi_page_pdf_path(tmp_path):
    """Create a multi-page PDF for testing"""
    pdf_path = tmp_path / "multi_page.pdf"
    doc = fitz.open()
    
    # Add 10 pages
    for i in range(10):
        page = doc.new_page(width=612, height=792)
        page.insert_text((72, 100), f"Page {i + 1}", fontsize=16)
        page.insert_text((72, 150), f"This is page {i + 1} content", fontsize=12)
    
    doc.save(str(pdf_path))
    doc.close()
    
    return str(pdf_path)


@pytest.fixture
def scanned_pdf_path(tmp_path):
    """Create a PDF with an image (simulating scanned PDF)"""
    pdf_path = tmp_path / "scanned.pdf"
    doc = fitz.open()
    
    # Add a page with just an image block (no text)
    page = doc.new_page(width=612, height=792)
    # Note: We're not inserting text, simulating a scanned document
    
    doc.save(str(pdf_path))
    doc.close()
    
    return str(pdf_path)


class TestPDFService:
    """Test suite for PDF extraction service"""

    def test_extract_text_with_layout(self, sample_pdf_path):
        """Test basic PDF text extraction with layout"""
        result = PDFService.extract_text_with_layout(sample_pdf_path)
        
        # Verify result structure
        assert isinstance(result, PDFExtractionResult)
        assert result.page_count == 1
        assert len(result.blocks) > 0
        assert result.total_characters > 0
        assert result.extraction_time_ms > 0
        assert result.is_scanned is False
        
        # Verify at least one block has expected text
        texts = [block.text for block in result.blocks]
        assert any("Hello World" in text for text in texts)

    def test_extract_blocks_with_coordinates(self, sample_pdf_path):
        """Test that blocks have normalized coordinates"""
        result = PDFService.extract_text_with_layout(sample_pdf_path)
        
        for block in result.blocks:
            # Verify block structure
            assert isinstance(block, Block)
            assert isinstance(block.coordinates, Coordinates)
            
            # Verify normalized coordinates (0-100%)
            assert 0 <= block.coordinates.x <= 100
            assert 0 <= block.coordinates.y <= 100
            assert 0 < block.coordinates.width <= 100
            assert 0 < block.coordinates.height <= 100
            
            # Verify page and block IDs
            assert block.page >= 0
            assert block.block_id >= 0
            
            # Verify text is not empty
            assert len(block.text.strip()) > 0

    def test_extract_font_information(self, sample_pdf_path):
        """Test that font information is preserved"""
        result = PDFService.extract_text_with_layout(sample_pdf_path)
        
        for block in result.blocks:
            # Verify font properties
            assert isinstance(block.font_size, (int, float))
            assert block.font_size > 0
            assert isinstance(block.font_name, str)
            assert len(block.font_name) > 0
            assert isinstance(block.is_bold, bool)
            assert isinstance(block.is_italic, bool)
            assert isinstance(block.rotation, (int, float))

    def test_extract_multi_page_pdf(self, multi_page_pdf_path):
        """Test extraction from multi-page PDF"""
        result = PDFService.extract_text_with_layout(multi_page_pdf_path)
        
        assert result.page_count == 10
        assert len(result.blocks) >= 10  # At least one block per page
        
        # Verify blocks span multiple pages
        pages = set(block.page for block in result.blocks)
        assert len(pages) == 10

    def test_detect_scanned_pdf(self, scanned_pdf_path):
        """Test detection of scanned PDFs"""
        result = PDFService.extract_text_with_layout(scanned_pdf_path)
        
        # Scanned PDF should be detected
        assert result.is_scanned is True
        assert result.total_characters < 10

    def test_detect_scanned_pdf_method(self, scanned_pdf_path, sample_pdf_path):
        """Test standalone scanned PDF detection"""
        # Scanned PDF
        assert PDFService.detect_scanned_pdf(scanned_pdf_path) is True
        
        # Normal PDF with text
        assert PDFService.detect_scanned_pdf(sample_pdf_path) is False

    def test_get_page_count(self, sample_pdf_path, multi_page_pdf_path):
        """Test page count retrieval"""
        assert PDFService.get_page_count(sample_pdf_path) == 1
        assert PDFService.get_page_count(multi_page_pdf_path) == 10

    def test_file_not_found(self):
        """Test error handling for missing file"""
        with pytest.raises(FileNotFoundError):
            PDFService.extract_text_with_layout("/nonexistent/file.pdf")

    def test_empty_pdf(self, tmp_path):
        """Test handling of empty PDF"""
        # Create empty PDF
        pdf_path = tmp_path / "empty.pdf"
        doc = fitz.open()
        doc.save(str(pdf_path))
        doc.close()
        
        result = PDFService.extract_text_with_layout(str(pdf_path))
        
        # Should extract successfully but with no blocks
        assert result.page_count == 0
        assert len(result.blocks) == 0

    def test_pdf_with_rotation(self, tmp_path):
        """Test extraction of rotated text"""
        pdf_path = tmp_path / "rotated.pdf"
        doc = fitz.open()
        
        page = doc.new_page(width=612, height=792)
        # Insert rotated text (90 degrees)
        page.insert_text((300, 400), "Rotated Text", rotate=90, fontsize=14)
        
        doc.save(str(pdf_path))
        doc.close()
        
        result = PDFService.extract_text_with_layout(str(pdf_path))
        
        # Should extract with rotation info
        assert len(result.blocks) > 0
        # Note: rotation detection depends on PyMuPDF's block metadata

    def test_performance_10_page_pdf(self, multi_page_pdf_path):
        """Test extraction performance on 10-page PDF"""
        result = PDFService.extract_text_with_layout(multi_page_pdf_path)
        
        # Should complete in < 1 second (per AC 2.2.3)
        assert result.extraction_time_ms < 1000, f"Took {result.extraction_time_ms}ms (expected <1000ms)"

    def test_large_pdf_performance(self, tmp_path):
        """Test extraction performance on larger PDF (100 pages)"""
        pdf_path = tmp_path / "large.pdf"
        doc = fitz.open()
        
        # Create 100-page PDF
        for i in range(100):
            page = doc.new_page(width=612, height=792)
            page.insert_text((72, 100), f"Page {i + 1}", fontsize=12)
            # Add more text to simulate real content
            for j in range(10):
                page.insert_text((72, 150 + j * 20), f"Line {j + 1} on page {i + 1}", fontsize=10)
        
        doc.save(str(pdf_path))
        doc.close()
        
        result = PDFService.extract_text_with_layout(str(pdf_path))
        
        # Should complete in < 5 seconds (per AC 2.2.3)
        assert result.extraction_time_ms < 5000, f"Took {result.extraction_time_ms}ms (expected <5000ms)"
        assert result.page_count == 100

    def test_corrupted_pdf(self, tmp_path):
        """Test handling of corrupted PDF"""
        pdf_path = tmp_path / "corrupted.pdf"
        
        # Write invalid PDF content
        with open(pdf_path, "wb") as f:
            f.write(b"Not a valid PDF")
        
        # Should raise an error
        with pytest.raises(Exception):
            PDFService.extract_text_with_layout(str(pdf_path))

    def test_unicode_text(self, tmp_path):
        """Test extraction of Unicode/international text"""
        pdf_path = tmp_path / "unicode.pdf"
        doc = fitz.open()
        
        page = doc.new_page(width=612, height=792)
        # Insert text with various Unicode characters
        page.insert_text((72, 100), "Hello 世界", fontsize=12)
        page.insert_text((72, 150), "Привет мир", fontsize=12)
        page.insert_text((72, 200), "مرحبا العالم", fontsize=12)
        
        doc.save(str(pdf_path))
        doc.close()
        
        result = PDFService.extract_text_with_layout(str(pdf_path))
        
        # Should extract Unicode text correctly
        assert len(result.blocks) > 0
        # Check that some international characters are present
        all_text = " ".join(block.text for block in result.blocks)
        assert any(char in all_text for char in ["世", "界", "П", "и"])

    def test_multi_column_detection(self, tmp_path):
        """Test extraction from multi-column layout"""
        pdf_path = tmp_path / "multi_column.pdf"
        doc = fitz.open()
        
        page = doc.new_page(width=612, height=792)
        
        # Left column
        page.insert_text((50, 100), "Left Column Header", fontsize=14)
        page.insert_text((50, 130), "Left column text", fontsize=10)
        
        # Right column
        page.insert_text((350, 100), "Right Column Header", fontsize=14)
        page.insert_text((350, 130), "Right column text", fontsize=10)
        
        doc.save(str(pdf_path))
        doc.close()
        
        result = PDFService.extract_text_with_layout(str(pdf_path))
        
        # Should extract blocks from both columns
        assert len(result.blocks) >= 2
        
        # Verify blocks have different x coordinates
        x_coords = [block.coordinates.x for block in result.blocks]
        assert len(set(x_coords)) > 1  # Multiple distinct x positions

    def test_block_ordering(self, tmp_path):
        """Test that blocks are ordered by position"""
        pdf_path = tmp_path / "ordered.pdf"
        doc = fitz.open()
        
        page = doc.new_page(width=612, height=792)
        
        # Insert text at different positions (top to bottom)
        page.insert_text((72, 100), "First block", fontsize=12)
        page.insert_text((72, 200), "Second block", fontsize=12)
        page.insert_text((72, 300), "Third block", fontsize=12)
        
        doc.save(str(pdf_path))
        doc.close()
        
        result = PDFService.extract_text_with_layout(str(pdf_path))
        
        # Blocks should be in sequential order
        assert len(result.blocks) >= 3
        for i, block in enumerate(result.blocks):
            assert block.block_id == i

    def test_extraction_with_images(self, tmp_path):
        """Test that images are skipped during text extraction"""
        pdf_path = tmp_path / "with_images.pdf"
        doc = fitz.open()
        
        page = doc.new_page(width=612, height=792)
        
        # Add text
        page.insert_text((72, 100), "Text before image", fontsize=12)
        
        # Note: We're testing that the service skips image blocks
        # PyMuPDF's get_text("dict") returns both text and image blocks
        # Our service should only process text blocks (type 0)
        
        page.insert_text((72, 400), "Text after image", fontsize=12)
        
        doc.save(str(pdf_path))
        doc.close()
        
        result = PDFService.extract_text_with_layout(str(pdf_path))
        
        # Should only extract text blocks
        assert all(isinstance(block.text, str) for block in result.blocks)
        assert all(len(block.text.strip()) > 0 for block in result.blocks)
