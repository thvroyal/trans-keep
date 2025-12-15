"""Tests for tone customization service"""

from unittest.mock import AsyncMock, MagicMock, patch

import anthropic
import pytest

from app.schemas.pdf import Block, Coordinates
from app.services.tone_service import ToneService
from app.services.translation_service import TranslatedBlock


@pytest.fixture
def mock_claude_client():
    """Create a mock Claude API client"""
    client = MagicMock()
    
    # Mock message response
    message = MagicMock()
    message.content = [MagicMock(text="Professional version of the text")]
    message.usage = MagicMock()
    message.usage.input_tokens = 100
    message.usage.output_tokens = 50
    
    client.messages.create.return_value = message
    
    return client


@pytest.fixture
def sample_translated_blocks():
    """Create sample translated blocks for testing"""
    original_block = Block(
        page=0,
        block_id=0,
        text="Hello World",
        coordinates=Coordinates(x=10, y=20, width=80, height=5),
        font_size=12,
        font_name="Arial",
        is_bold=False,
        is_italic=False,
        rotation=0,
    )
    
    return [
        TranslatedBlock(
            original=original_block,
            translated_text="こんにちは世界",
            source_lang="en",
            target_lang="ja",
            billed_characters=11,
        ),
        TranslatedBlock(
            original=Block(
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
            translated_text="これはテストです",
            source_lang="en",
            target_lang="ja",
            billed_characters=14,
        ),
    ]


class TestToneService:
    """Test suite for tone service"""

    def test_init_with_api_key(self):
        """Test initialization with API key"""
        with patch("app.services.tone_service.anthropic.Anthropic") as mock_anthropic:
            with patch("app.config.get_settings") as mock_settings:
                mock_settings.return_value.claude_api_key = "test_key"
                service = ToneService(api_key="test_key")
                assert service.api_key == "test_key"
                mock_anthropic.assert_called_once_with(api_key="test_key")

    def test_init_without_api_key_raises(self):
        """Test initialization without API key raises error"""
        with patch("app.config.get_settings") as mock_settings:
            mock_settings.return_value.claude_api_key = ""
            with pytest.raises(ValueError, match="Claude API key not configured"):
                ToneService()

    def test_get_tone_prompt_professional(self):
        """Test professional tone prompt generation"""
        with patch("app.services.tone_service.anthropic.Anthropic"):
            with patch("app.config.get_settings") as mock_settings:
                mock_settings.return_value.claude_api_key = "test_key"
                service = ToneService(api_key="test_key")
                prompt = service._get_tone_prompt("professional")
                assert "formal" in prompt.lower()
                assert "professional" in prompt.lower()
                assert "business" in prompt.lower()

    def test_get_tone_prompt_casual(self):
        """Test casual tone prompt generation"""
        with patch("app.services.tone_service.anthropic.Anthropic"):
            with patch("app.config.get_settings") as mock_settings:
                mock_settings.return_value.claude_api_key = "test_key"
                service = ToneService(api_key="test_key")
                prompt = service._get_tone_prompt("casual")
                assert "friendly" in prompt.lower()
                assert "conversational" in prompt.lower()
                assert "casual" in prompt.lower()

    def test_get_tone_prompt_technical(self):
        """Test technical tone prompt generation"""
        with patch("app.services.tone_service.anthropic.Anthropic"):
            with patch("app.config.get_settings") as mock_settings:
                mock_settings.return_value.claude_api_key = "test_key"
                service = ToneService(api_key="test_key")
                prompt = service._get_tone_prompt("technical")
                assert "technical" in prompt.lower()
                assert "terminology" in prompt.lower()

    def test_get_tone_prompt_creative(self):
        """Test creative tone prompt generation"""
        with patch("app.services.tone_service.anthropic.Anthropic"):
            with patch("app.config.get_settings") as mock_settings:
                mock_settings.return_value.claude_api_key = "test_key"
                service = ToneService(api_key="test_key")
                prompt = service._get_tone_prompt("creative")
                assert "creative" in prompt.lower()
                assert "marketing" in prompt.lower()
                assert "compelling" in prompt.lower()

    def test_get_tone_prompt_custom(self):
        """Test custom tone prompt generation"""
        with patch("app.services.tone_service.anthropic.Anthropic"):
            with patch("app.config.get_settings") as mock_settings:
                mock_settings.return_value.claude_api_key = "test_key"
                service = ToneService(api_key="test_key")
                custom_tone = "Friendly but professional"
                prompt = service._get_tone_prompt(custom_tone)
                assert custom_tone in prompt
                assert "Rewrite this text" in prompt

    @pytest.mark.asyncio
    async def test_apply_tone_success(self, mock_claude_client):
        """Test successful tone application"""
        with patch("app.services.tone_service.anthropic.Anthropic", return_value=mock_claude_client):
            with patch("app.config.get_settings") as mock_settings:
                mock_settings.return_value.claude_api_key = "test_key"
                service = ToneService(api_key="test_key")
                
                result_text, cost = await service.apply_tone(
                    text="Hello World",
                    tone="professional",
                )
                
                assert result_text == "Professional version of the text"
                assert cost > 0
                mock_claude_client.messages.create.assert_called_once()
                
                # Verify API call arguments
                call_args = mock_claude_client.messages.create.call_args
                assert call_args.kwargs["model"] == "claude-3-5-haiku-20241022"
                assert "professional" in call_args.kwargs["messages"][0]["content"].lower()

    @pytest.mark.asyncio
    async def test_apply_tone_empty_text(self):
        """Test tone application with empty text"""
        with patch("app.services.tone_service.anthropic.Anthropic"):
            with patch("app.config.get_settings") as mock_settings:
                mock_settings.return_value.claude_api_key = "test_key"
                service = ToneService(api_key="test_key")
                
                result_text, cost = await service.apply_tone(
                    text="",
                    tone="professional",
                )
                
                assert result_text == ""
                assert cost == 0.0

    @pytest.mark.asyncio
    async def test_apply_tone_whitespace_only(self):
        """Test tone application with whitespace-only text"""
        with patch("app.services.tone_service.anthropic.Anthropic"):
            with patch("app.config.get_settings") as mock_settings:
                mock_settings.return_value.claude_api_key = "test_key"
                service = ToneService(api_key="test_key")
                
                result_text, cost = await service.apply_tone(
                    text="   \n\t  ",
                    tone="professional",
                )
                
                assert result_text == ""
                assert cost == 0.0

    @pytest.mark.asyncio
    async def test_apply_tone_cost_calculation(self, mock_claude_client):
        """Test cost calculation is accurate"""
        with patch("app.services.tone_service.anthropic.Anthropic", return_value=mock_claude_client):
            with patch("app.config.get_settings") as mock_settings:
                mock_settings.return_value.claude_api_key = "test_key"
                service = ToneService(api_key="test_key")
                
                # Set specific token counts
                mock_claude_client.messages.create.return_value.usage.input_tokens = 200
                mock_claude_client.messages.create.return_value.usage.output_tokens = 100
                
                _, cost = await service.apply_tone(
                    text="Test text",
                    tone="professional",
                )
                
                # Expected cost: (200 * 0.80/1M) + (100 * 4/1M) = 0.00016 + 0.0004 = 0.00056
                expected_cost = (200 * 0.80 / 1_000_000) + (100 * 4.00 / 1_000_000)
                assert abs(cost - expected_cost) < 0.000001

    @pytest.mark.asyncio
    async def test_batch_apply_tone_success(self, mock_claude_client, sample_translated_blocks):
        """Test batch tone application"""
        with patch("app.services.tone_service.anthropic.Anthropic", return_value=mock_claude_client):
            with patch("app.config.get_settings") as mock_settings:
                mock_settings.return_value.claude_api_key = "test_key"
                service = ToneService(api_key="test_key")
                
                customized_blocks, total_cost = await service.batch_apply_tone(
                    blocks=sample_translated_blocks,
                    tone="professional",
                )
                
                assert len(customized_blocks) == len(sample_translated_blocks)
                assert total_cost > 0
                assert mock_claude_client.messages.create.call_count == len(sample_translated_blocks)
                
                # Verify blocks have customized text
                for block in customized_blocks:
                    assert block.translated_text == "Professional version of the text"
                    assert block.original == sample_translated_blocks[0].original or \
                           block.original == sample_translated_blocks[1].original

    @pytest.mark.asyncio
    async def test_batch_apply_tone_empty_list(self):
        """Test batch tone application with empty list"""
        with patch("app.services.tone_service.anthropic.Anthropic"):
            with patch("app.config.get_settings") as mock_settings:
                mock_settings.return_value.claude_api_key = "test_key"
                service = ToneService(api_key="test_key")
                
                customized_blocks, total_cost = await service.batch_apply_tone(
                    blocks=[],
                    tone="professional",
                )
                
                assert len(customized_blocks) == 0
                assert total_cost == 0.0

    @pytest.mark.asyncio
    async def test_batch_apply_tone_partial_failure(self, mock_claude_client, sample_translated_blocks):
        """Test batch tone application with partial failures"""
        with patch("app.services.tone_service.anthropic.Anthropic", return_value=mock_claude_client):
            with patch("app.config.get_settings") as mock_settings:
                mock_settings.return_value.claude_api_key = "test_key"
                service = ToneService(api_key="test_key")
                
                # Make second call fail
                def side_effect(*args, **kwargs):
                    if mock_claude_client.messages.create.call_count == 2:
                        raise Exception("API Error")
                    return mock_claude_client.messages.create.return_value
                
                mock_claude_client.messages.create.side_effect = side_effect
                
                customized_blocks, total_cost = await service.batch_apply_tone(
                    blocks=sample_translated_blocks,
                    tone="professional",
                )
                
                # Should still return all blocks, with original text for failed one
                assert len(customized_blocks) == len(sample_translated_blocks)
                # First block should be customized, second should be original
                assert customized_blocks[0].translated_text == "Professional version of the text"
                assert customized_blocks[1].translated_text == sample_translated_blocks[1].translated_text

    @pytest.mark.asyncio
    async def test_apply_tone_rate_limit_retry(self, mock_claude_client):
        """Test rate limit retry logic"""
        with patch("app.services.tone_service.anthropic.Anthropic", return_value=mock_claude_client):
            with patch("app.config.get_settings") as mock_settings:
                mock_settings.return_value.claude_api_key = "test_key"
                service = ToneService(api_key="test_key")
                
                # First call raises rate limit, second succeeds
                mock_claude_client.messages.create.side_effect = [
                    anthropic.RateLimitError("Rate limit", response=None, body=None),
                    mock_claude_client.messages.create.return_value,
                ]
                
                result_text, cost = await service.apply_tone(
                    text="Test",
                    tone="professional",
                )
                
                assert result_text == "Professional version of the text"
                assert mock_claude_client.messages.create.call_count == 2

    def test_get_cost_estimate(self):
        """Test cost estimation"""
        with patch("app.services.tone_service.anthropic.Anthropic"):
            with patch("app.config.get_settings") as mock_settings:
                mock_settings.return_value.claude_api_key = "test_key"
                service = ToneService(api_key="test_key")
                
                # Estimate for 1000 characters
                estimate = service.get_cost_estimate(1000)
                
                # Should be a positive number
                assert estimate > 0
                # Rough check: 1000 chars ≈ 250 tokens, so cost should be around 0.0001-0.001
                assert 0.0001 < estimate < 0.01

    def test_get_cost_estimate_zero(self):
        """Test cost estimation with zero characters"""
        with patch("app.services.tone_service.anthropic.Anthropic"):
            with patch("app.config.get_settings") as mock_settings:
                mock_settings.return_value.claude_api_key = "test_key"
                service = ToneService(api_key="test_key")
                
                estimate = service.get_cost_estimate(0)
                assert estimate == 0.0
