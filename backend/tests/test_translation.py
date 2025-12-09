"""Tests for translation service"""

from unittest.mock import AsyncMock, MagicMock, patch

import deepl
import pytest

from app.schemas.pdf import Block, Coordinates
from app.services.translation_service import TranslatedBlock, TranslationService


@pytest.fixture
def sample_blocks():
    """Create sample text blocks for testing"""
    return [
        Block(
            page=0,
            block_id=0,
            text="Hello World",
            coordinates=Coordinates(x=10, y=20, width=80, height=5),
            font_size=12,
            font_name="Arial",
            is_bold=False,
            is_italic=False,
            rotation=0,
        ),
        Block(
            page=0,
            block_id=1,
            text="This is a test",
            coordinates=Coordinates(x=10, y=30, width=80, height=5),
            font_size=12,
            font_name="Arial",
            is_bold=False,
            is_italic=False,
            rotation=0,
        ),
        Block(
            page=1,
            block_id=0,
            text="Second page content",
            coordinates=Coordinates(x=10, y=20, width=80, height=5),
            font_size=12,
            font_name="Arial",
            is_bold=False,
            is_italic=False,
            rotation=0,
        ),
    ]


@pytest.fixture
def mock_deepl_translator():
    """Create a mock DeepL translator"""
    translator = MagicMock()
    
    # Mock translate_text for single translation
    def mock_translate(text, source_lang=None, target_lang="JA"):
        result = MagicMock()
        result.text = f"[{target_lang}] {text}"  # Simple mock translation
        result.detected_source_lang = "EN"
        return result
    
    translator.translate_text.side_effect = mock_translate
    
    # Mock usage
    usage = MagicMock()
    usage.character.count = 10000
    usage.character.limit = 500000
    translator.get_usage.return_value = usage
    
    # Mock languages
    source_lang = MagicMock()
    source_lang.code = "EN"
    source_lang.name = "English"
    
    target_lang = MagicMock()
    target_lang.code = "JA"
    target_lang.name = "Japanese"
    
    translator.get_source_languages.return_value = [source_lang]
    translator.get_target_languages.return_value = [target_lang]
    
    return translator


class TestTranslationService:
    """Test suite for translation service"""

    def test_init_with_api_key(self):
        """Test initialization with API key"""
        with patch("app.services.translation_service.deepl.Translator") as mock_trans:
            service = TranslationService(api_key="test_key")
            assert service.api_key == "test_key"
            mock_trans.assert_called_once_with("test_key")

    def test_init_without_api_key_raises(self):
        """Test initialization without API key raises error"""
        with patch("app.config.get_settings") as mock_settings:
            mock_settings.return_value.deepl_api_key = ""
            with pytest.raises(ValueError, match="DeepL API key not configured"):
                TranslationService()

    @pytest.mark.asyncio
    async def test_translate_text_basic(self, mock_deepl_translator):
        """Test basic text translation"""
        with patch("app.services.translation_service.deepl.Translator", return_value=mock_deepl_translator):
            service = TranslationService(api_key="test_key")
            
            translated, billed = await service.translate_text(
                text="Hello World",
                source_lang="EN",
                target_lang="JA",
            )
            
            assert translated == "[JA] Hello World"
            assert billed == len("Hello World")

    @pytest.mark.asyncio
    async def test_translate_text_auto_detect(self, mock_deepl_translator):
        """Test translation with auto-detect source language"""
        with patch("app.services.translation_service.deepl.Translator", return_value=mock_deepl_translator):
            service = TranslationService(api_key="test_key")
            
            translated, billed = await service.translate_text(
                text="Hello World",
                source_lang="auto",
                target_lang="JA",
            )
            
            assert "[JA]" in translated
            assert billed > 0

    @pytest.mark.asyncio
    async def test_translate_empty_text(self, mock_deepl_translator):
        """Test translation of empty text"""
        with patch("app.services.translation_service.deepl.Translator", return_value=mock_deepl_translator):
            service = TranslationService(api_key="test_key")
            
            translated, billed = await service.translate_text(
                text="",
                source_lang="EN",
                target_lang="JA",
            )
            
            assert translated == ""
            assert billed == 0

    @pytest.mark.asyncio
    async def test_batch_translate(self, sample_blocks, mock_deepl_translator):
        """Test batch translation of blocks"""
        # Mock batch translation
        def mock_batch_translate(texts, source_lang=None, target_lang="JA"):
            results = []
            for text in texts:
                result = MagicMock()
                result.text = f"[{target_lang}] {text}"
                result.detected_source_lang = "EN"
                results.append(result)
            return results
        
        mock_deepl_translator.translate_text.side_effect = mock_batch_translate
        
        with patch("app.services.translation_service.deepl.Translator", return_value=mock_deepl_translator):
            service = TranslationService(api_key="test_key")
            
            translated_blocks, cost = await service.batch_translate(
                blocks=sample_blocks,
                source_lang="EN",
                target_lang="JA",
            )
            
            # Verify results
            assert len(translated_blocks) == len(sample_blocks)
            assert all(isinstance(tb, TranslatedBlock) for tb in translated_blocks)
            assert all("[JA]" in tb.translated_text for tb in translated_blocks)
            assert cost > 0  # Should have some cost

    @pytest.mark.asyncio
    async def test_batch_translate_batching(self, mock_deepl_translator):
        """Test that batch translation groups blocks correctly"""
        # Create 25 blocks (should be split into 3 batches: 10, 10, 5)
        blocks = [
            Block(
                page=i,
                block_id=0,
                text=f"Block {i}",
                coordinates=Coordinates(x=10, y=20, width=80, height=5),
                font_size=12,
                font_name="Arial",
                is_bold=False,
                is_italic=False,
                rotation=0,
            )
            for i in range(25)
        ]
        
        call_count = 0
        
        def mock_batch_translate(texts, source_lang=None, target_lang="JA"):
            nonlocal call_count
            call_count += 1
            
            # Verify batch size
            assert len(texts) <= TranslationService.BATCH_SIZE
            
            results = []
            for text in texts:
                result = MagicMock()
                result.text = f"[{target_lang}] {text}"
                result.detected_source_lang = "EN"
                results.append(result)
            return results
        
        mock_deepl_translator.translate_text.side_effect = mock_batch_translate
        
        with patch("app.services.translation_service.deepl.Translator", return_value=mock_deepl_translator):
            service = TranslationService(api_key="test_key")
            
            translated_blocks, cost = await service.batch_translate(
                blocks=blocks,
                source_lang="EN",
                target_lang="JA",
            )
            
            # Should have made 3 API calls (25 blocks / 10 batch size)
            assert call_count == 3
            assert len(translated_blocks) == 25

    @pytest.mark.asyncio
    async def test_batch_translate_empty_list(self, mock_deepl_translator):
        """Test batch translation with empty block list"""
        with patch("app.services.translation_service.deepl.Translator", return_value=mock_deepl_translator):
            service = TranslationService(api_key="test_key")
            
            translated_blocks, cost = await service.batch_translate(
                blocks=[],
                source_lang="EN",
                target_lang="JA",
            )
            
            assert len(translated_blocks) == 0
            assert cost == 0.0

    @pytest.mark.asyncio
    async def test_translate_quota_exceeded(self, mock_deepl_translator):
        """Test handling of quota exceeded error"""
        mock_deepl_translator.translate_text.side_effect = deepl.exceptions.QuotaExceededException(
            "Quota exceeded"
        )
        
        with patch("app.services.translation_service.deepl.Translator", return_value=mock_deepl_translator):
            service = TranslationService(api_key="test_key")
            
            with pytest.raises(deepl.exceptions.QuotaExceededException):
                await service.translate_text(
                    text="Hello World",
                    source_lang="EN",
                    target_lang="JA",
                )

    @pytest.mark.asyncio
    async def test_translate_rate_limit_retry(self, mock_deepl_translator):
        """Test retry logic for rate limiting"""
        # First call fails, second succeeds
        call_count = 0
        
        def mock_translate_with_retry(text, source_lang=None, target_lang="JA"):
            nonlocal call_count
            call_count += 1
            
            if call_count == 1:
                raise deepl.exceptions.TooManyRequestsException("Rate limit")
            
            result = MagicMock()
            result.text = f"[{target_lang}] {text}"
            result.detected_source_lang = "EN"
            return result
        
        mock_deepl_translator.translate_text.side_effect = mock_translate_with_retry
        
        with patch("app.services.translation_service.deepl.Translator", return_value=mock_deepl_translator):
            service = TranslationService(api_key="test_key")
            
            # Should retry and succeed
            translated, billed = await service.translate_text(
                text="Hello World",
                source_lang="EN",
                target_lang="JA",
            )
            
            assert call_count == 2  # First failed, second succeeded
            assert "[JA]" in translated

    @pytest.mark.asyncio
    async def test_batch_translate_cost_calculation(self, sample_blocks, mock_deepl_translator):
        """Test cost calculation in batch translation"""
        def mock_batch_translate(texts, source_lang=None, target_lang="JA"):
            results = []
            for text in texts:
                result = MagicMock()
                result.text = f"[{target_lang}] {text}"
                result.detected_source_lang = "EN"
                results.append(result)
            return results
        
        mock_deepl_translator.translate_text.side_effect = mock_batch_translate
        
        with patch("app.services.translation_service.deepl.Translator", return_value=mock_deepl_translator):
            service = TranslationService(api_key="test_key")
            
            translated_blocks, cost = await service.batch_translate(
                blocks=sample_blocks,
                source_lang="EN",
                target_lang="JA",
            )
            
            # Calculate expected cost
            total_chars = sum(len(block.text) for block in sample_blocks)
            expected_cost = total_chars * TranslationService.COST_PER_CHARACTER
            
            assert abs(cost - expected_cost) < 0.0001  # Float comparison

    def test_get_usage(self, mock_deepl_translator):
        """Test getting DeepL usage statistics"""
        with patch("app.services.translation_service.deepl.Translator", return_value=mock_deepl_translator):
            service = TranslationService(api_key="test_key")
            
            usage = service.get_usage()
            
            assert usage["character_count"] == 10000
            assert usage["character_limit"] == 500000
            assert usage["character_remaining"] == 490000

    def test_get_supported_languages(self, mock_deepl_translator):
        """Test getting supported languages"""
        with patch("app.services.translation_service.deepl.Translator", return_value=mock_deepl_translator):
            service = TranslationService(api_key="test_key")
            
            languages = service.get_supported_languages()
            
            assert "source" in languages
            assert "target" in languages
            assert len(languages["source"]) > 0
            assert len(languages["target"]) > 0

    @pytest.mark.asyncio
    async def test_translate_multiple_languages(self, sample_blocks, mock_deepl_translator):
        """Test translation to different target languages"""
        def mock_batch_translate(texts, source_lang=None, target_lang="JA"):
            results = []
            for text in texts:
                result = MagicMock()
                result.text = f"[{target_lang}] {text}"
                result.detected_source_lang = "EN"
                results.append(result)
            return results
        
        mock_deepl_translator.translate_text.side_effect = mock_batch_translate
        
        with patch("app.services.translation_service.deepl.Translator", return_value=mock_deepl_translator):
            service = TranslationService(api_key="test_key")
            
            # Test JA
            translated_ja, _ = await service.batch_translate(
                blocks=sample_blocks[:1],
                source_lang="EN",
                target_lang="JA",
            )
            assert "[JA]" in translated_ja[0].translated_text
            
            # Test VI
            translated_vi, _ = await service.batch_translate(
                blocks=sample_blocks[:1],
                source_lang="EN",
                target_lang="VI",
            )
            assert "[VI]" in translated_vi[0].translated_text
            
            # Test ZH
            translated_zh, _ = await service.batch_translate(
                blocks=sample_blocks[:1],
                source_lang="EN",
                target_lang="ZH",
            )
            assert "[ZH]" in translated_zh[0].translated_text

    @pytest.mark.asyncio
    async def test_translated_block_structure(self, sample_blocks, mock_deepl_translator):
        """Test that TranslatedBlock contains all required fields"""
        def mock_batch_translate(texts, source_lang=None, target_lang="JA"):
            results = []
            for text in texts:
                result = MagicMock()
                result.text = f"[{target_lang}] {text}"
                result.detected_source_lang = "EN"
                results.append(result)
            return results
        
        mock_deepl_translator.translate_text.side_effect = mock_batch_translate
        
        with patch("app.services.translation_service.deepl.Translator", return_value=mock_deepl_translator):
            service = TranslationService(api_key="test_key")
            
            translated_blocks, _ = await service.batch_translate(
                blocks=sample_blocks[:1],
                source_lang="EN",
                target_lang="JA",
            )
            
            tb = translated_blocks[0]
            
            # Verify structure
            assert isinstance(tb, TranslatedBlock)
            assert isinstance(tb.original, Block)
            assert isinstance(tb.translated_text, str)
            assert isinstance(tb.source_lang, str)
            assert isinstance(tb.target_lang, str)
            assert isinstance(tb.billed_characters, int)
            assert tb.billed_characters > 0
