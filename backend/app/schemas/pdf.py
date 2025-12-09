"""PDF extraction schemas"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Coordinates:
    """
    Coordinates for a text block, normalized as percentages (0-100).
    
    This allows for resolution-independent positioning when reconstructing
    the translated PDF.
    """
    x: float  # Left position as percentage of page width
    y: float  # Top position as percentage of page height
    width: float  # Block width as percentage of page width
    height: float  # Block height as percentage of page height


@dataclass
class Block:
    """
    A text block extracted from a PDF page.
    
    Contains the text content, position, and formatting information
    needed to reconstruct the translated document with preserved layout.
    """
    page: int  # Zero-indexed page number
    block_id: int  # Block index within the page
    text: str  # Extracted text content
    coordinates: Coordinates  # Normalized position (0-100%)
    font_size: float  # Font size in points
    font_name: str  # Font family name
    is_bold: bool  # Text is bold
    is_italic: bool  # Text is italic
    rotation: float  # Text rotation in degrees (0, 90, 180, 270)


@dataclass
class PDFExtractionResult:
    """
    Complete result of PDF text extraction.
    
    Contains all text blocks from all pages, plus metadata
    about the extraction process.
    """
    blocks: List[Block]  # All extracted text blocks
    page_count: int  # Total number of pages
    is_scanned: bool  # True if PDF appears to be scanned (no text)
    total_characters: int  # Total character count across all blocks
    extraction_time_ms: int  # Time taken to extract (milliseconds)
