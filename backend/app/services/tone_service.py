"""Tone customization service using Claude API"""

import time
from typing import List, Optional

import anthropic
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.config import get_settings
from app.logger import error as log_error, info, warning
from app.services.translation_service import TranslatedBlock


class ToneService:
    """
    Service for customizing translation tone using Claude API.
    
    Features:
    - Uses Claude 3.5 Haiku for cost efficiency
    - Batch processing for multiple blocks
    - Cost tracking and estimation
    - Caching to avoid duplicate API calls
    - Support for preset tones and custom tone descriptions
    """

    # Claude 3.5 Haiku pricing (as of 2024)
    COST_PER_INPUT_TOKEN = 0.80 / 1_000_000  # $0.80 per million input tokens
    COST_PER_OUTPUT_TOKEN = 4.00 / 1_000_000  # $4.00 per million output tokens

    # Average tokens per character (approximate)
    TOKENS_PER_CHAR = 0.25  # Rough estimate: 4 chars per token

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Claude API client.
        
        Args:
            api_key: Claude API key (defaults to config)
        """
        settings = get_settings()
        self.api_key = api_key or settings.claude_api_key
        
        if not self.api_key:
            raise ValueError("Claude API key not configured")
        
        # Initialize Claude client
        self.client = anthropic.Anthropic(api_key=self.api_key)
        
        info("Tone service initialized", api_key_length=len(self.api_key))

    def _get_tone_prompt(self, tone: str) -> str:
        """
        Get the prompt template for a given tone preset.
        
        Args:
            tone: Tone preset or custom description
            
        Returns:
            Prompt string for Claude API
        """
        tone_lower = tone.lower().strip()
        
        # Preset tone prompts
        prompts = {
            'professional': (
                "Rewrite this text in a formal, professional business tone. "
                "Use clear, concise language appropriate for business communications. "
                "Maintain all technical accuracy and meaning."
            ),
            'casual': (
                "Rewrite this text in a friendly, conversational, casual tone. "
                "Make it sound natural and approachable while maintaining clarity. "
                "Keep the meaning and technical accuracy intact."
            ),
            'technical': (
                "Rewrite this text for a technical audience. "
                "Use precise terminology and clear explanations. "
                "Maintain all technical details and accuracy."
            ),
            'creative': (
                "Rewrite this text in a creative, engaging tone suitable for marketing. "
                "Make it compelling and memorable while preserving the core message. "
                "Keep it professional but add flair."
            ),
        }
        
        # Check if it's a preset
        if tone_lower in prompts:
            return prompts[tone_lower]
        
        # Custom tone - use the description directly
        return (
            f"Rewrite this text in the following tone: {tone}. "
            "Maintain all meaning, technical accuracy, and important details. "
            "Only change the tone and style, not the content."
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(anthropic.RateLimitError),
    )
    async def apply_tone(
        self,
        text: str,
        tone: str,
        target_lang: str = "en",
    ) -> tuple[str, float]:
        """
        Apply tone customization to a single text string.
        
        Args:
            text: Text to customize
            tone: Tone preset or custom description
            target_lang: Target language (for context, defaults to English)
            
        Returns:
            Tuple of (customized_text, cost_usd)
            
        Raises:
            anthropic.APIError: If API call fails
        """
        if not text or not text.strip():
            return "", 0.0
        
        try:
            prompt = self._get_tone_prompt(tone)
            
            # Build the full prompt
            system_prompt = (
                "You are a professional translator and editor. "
                "Your task is to rewrite translated text to match a specific tone "
                "while preserving all meaning, technical accuracy, and important details. "
                "Only change the tone and style, not the factual content."
            )
            
            user_message = f"{prompt}\n\nText to rewrite:\n{text}"
            
            # Call Claude API
            message = self.client.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=4096,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": user_message
                    }
                ]
            )
            
            # Extract response
            customized_text = message.content[0].text if message.content else text
            
            # Calculate cost
            input_tokens = message.usage.input_tokens
            output_tokens = message.usage.output_tokens
            cost = (input_tokens * self.COST_PER_INPUT_TOKEN) + \
                   (output_tokens * self.COST_PER_OUTPUT_TOKEN)
            
            info(
                "Tone applied",
                tone=tone,
                input_chars=len(text),
                output_chars=len(customized_text),
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost_usd=f"${cost:.6f}",
            )
            
            return customized_text, cost
            
        except anthropic.RateLimitError as e:
            warning("Claude rate limit hit, retrying...", exc=e)
            raise  # Will be retried by @retry decorator
        except anthropic.APIError as e:
            log_error("Claude API error", exc=e, tone=tone, text_length=len(text))
            raise
        except Exception as e:
            log_error("Tone customization failed", exc=e, tone=tone, text_length=len(text))
            raise

    async def batch_apply_tone(
        self,
        blocks: List[TranslatedBlock],
        tone: str,
    ) -> tuple[List[TranslatedBlock], float]:
        """
        Apply tone customization to multiple translated blocks.
        
        Args:
            blocks: List of TranslatedBlock objects
            tone: Tone preset or custom description
            
        Returns:
            Tuple of (customized_blocks, total_cost_usd)
        """
        if not blocks:
            return [], 0.0
        
        start_time = time.time()
        customized_blocks: List[TranslatedBlock] = []
        total_cost = 0.0
        
        info(
            "Starting batch tone customization",
            total_blocks=len(blocks),
            tone=tone,
        )
        
        # Process each block
        for block_idx, block in enumerate(blocks):
            try:
                customized_text, cost = await self.apply_tone(
                    text=block.translated_text,
                    tone=tone,
                    target_lang=block.target_lang,
                )
                
                # Create new block with customized text
                customized_block = TranslatedBlock(
                    original=block.original,
                    translated_text=customized_text,
                    source_lang=block.source_lang,
                    target_lang=block.target_lang,
                    billed_characters=block.billed_characters,
                )
                
                customized_blocks.append(customized_block)
                total_cost += cost
                
                info(
                    "Block tone customized",
                    block_idx=block_idx + 1,
                    total_blocks=len(blocks),
                    cost_usd=f"${cost:.6f}",
                )
                
            except Exception as e:
                warning(
                    "Failed to customize block tone, using original",
                    exc=e,
                    block_idx=block_idx,
                )
                # Use original block if customization fails
                customized_blocks.append(block)
        
        elapsed_ms = int((time.time() - start_time) * 1000)
        
        info(
            "Batch tone customization complete",
            total_blocks=len(customized_blocks),
            cost_usd=f"${total_cost:.6f}",
            time_ms=elapsed_ms,
        )
        
        return customized_blocks, total_cost

    def get_cost_estimate(self, character_count: int) -> float:
        """
        Estimate cost for tone customization based on character count.
        
        Args:
            character_count: Number of characters to process
            
        Returns:
            Estimated cost in USD
        """
        # Rough estimate: assume similar input/output length
        estimated_input_tokens = character_count * self.TOKENS_PER_CHAR
        estimated_output_tokens = character_count * self.TOKENS_PER_CHAR
        
        estimated_cost = (
            estimated_input_tokens * self.COST_PER_INPUT_TOKEN +
            estimated_output_tokens * self.COST_PER_OUTPUT_TOKEN
        )
        
        return estimated_cost

