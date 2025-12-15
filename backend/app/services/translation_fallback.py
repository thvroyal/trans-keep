"""Translation service with fallback to Google Translate"""

from typing import Optional
import deepl
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.config import get_settings
from app.logger import error as log_error, info, warning
from app.services.translation_service import TranslationService, TranslatedBlock
from app.schemas.pdf import Block


class GoogleTranslateFallback:
    """
    Fallback translation service using Google Translate API.
    
    This is a simplified implementation. In production, you would use
    google-cloud-translate library. For now, we'll use a placeholder
    that logs the fallback attempt.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Google Translate fallback.
        
        Args:
            api_key: Google Translate API key (optional, can use environment)
        """
        settings = get_settings()
        self.api_key = api_key or getattr(settings, 'google_translate_api_key', None)
        
        if not self.api_key:
            warning("Google Translate API key not configured - fallback will not work")
        
        info("Google Translate fallback initialized", has_api_key=bool(self.api_key))
    
    async def translate_text(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
    ) -> tuple[str, int]:
        """
        Translate text using Google Translate API.
        
        Args:
            text: Text to translate
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            Tuple of (translated_text, billed_characters)
            
        Note:
            This is a placeholder. In production, implement using google-cloud-translate.
        """
        if not self.api_key:
            raise ValueError("Google Translate API key not configured")
        
        # TODO: Implement actual Google Translate API call
        # For now, return original text with a warning
        warning(
            "Google Translate fallback called but not fully implemented",
            text_length=len(text),
            source_lang=source_lang,
            target_lang=target_lang,
        )
        
        # Placeholder: return original text (in production, call Google Translate API)
        return text, len(text)


class TranslationServiceWithFallback:
    """
    Translation service with automatic fallback to Google Translate.
    
    Attempts to use DeepL first, falls back to Google Translate if DeepL fails.
    """
    
    def __init__(
        self,
        deepl_api_key: Optional[str] = None,
        google_api_key: Optional[str] = None,
    ):
        """
        Initialize translation service with fallback.
        
        Args:
            deepl_api_key: DeepL API key
            google_api_key: Google Translate API key (optional)
        """
        self.primary = TranslationService(api_key=deepl_api_key)
        self.fallback = GoogleTranslateFallback(api_key=google_api_key)
        self.fallback_enabled = bool(google_api_key)
        
        info(
            "Translation service with fallback initialized",
            fallback_enabled=self.fallback_enabled,
        )
    
    async def translate_text(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
    ) -> tuple[str, int]:
        """
        Translate text with automatic fallback.
        
        Args:
            text: Text to translate
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            Tuple of (translated_text, billed_characters)
        """
        try:
            # Try primary service (DeepL)
            return await self.primary.translate_text(text, source_lang, target_lang)
        except (deepl.exceptions.DeepLException, Exception) as e:
            # Check if fallback is enabled
            if not self.fallback_enabled:
                log_error("DeepL failed and fallback disabled", exc=e)
                raise
            
            # Log the fallback
            warning(
                "DeepL translation failed, using Google Translate fallback",
                exc=e,
                source_lang=source_lang,
                target_lang=target_lang,
            )
            
            try:
                # Use fallback
                return await self.fallback.translate_text(text, source_lang, target_lang)
            except Exception as fallback_error:
                log_error(
                    "Both DeepL and Google Translate failed",
                    primary_error=str(e),
                    fallback_error=str(fallback_error),
                )
                raise fallback_error
    
    async def batch_translate(
        self,
        blocks: List[Block],
        source_lang: str,
        target_lang: str,
    ) -> tuple[List[TranslatedBlock], float]:
        """
        Translate multiple blocks with automatic fallback.
        
        Args:
            blocks: List of text blocks
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            Tuple of (translated_blocks, total_cost_usd)
        """
        try:
            # Try primary service
            return await self.primary.batch_translate(blocks, source_lang, target_lang)
        except (deepl.exceptions.DeepLException, Exception) as e:
            if not self.fallback_enabled:
                log_error("DeepL batch translation failed and fallback disabled", exc=e)
                raise
            
            warning(
                "DeepL batch translation failed, using Google Translate fallback",
                exc=e,
                num_blocks=len(blocks),
            )
            
            # Fallback: translate blocks one by one (slower but more reliable)
            translated_blocks: List[TranslatedBlock] = []
            total_cost = 0.0
            
            for block in blocks:
                try:
                    translated_text, _ = await self.fallback.translate_text(
                        block.text,
                        source_lang,
                        target_lang,
                    )
                    
                    translated_block = TranslatedBlock(
                        original=block,
                        translated_text=translated_text,
                        source_lang=source_lang,
                        target_lang=target_lang,
                        billed_characters=len(block.text),
                    )
                    translated_blocks.append(translated_block)
                except Exception as block_error:
                    warning(
                        "Failed to translate block with fallback",
                        exc=block_error,
                        block_text_preview=block.text[:50],
                    )
                    # Skip this block or use original text
                    continue
            
            return translated_blocks, total_cost
