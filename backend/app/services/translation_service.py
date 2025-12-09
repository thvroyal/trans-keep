"""Translation service using DeepL API"""

import time
from dataclasses import dataclass
from typing import List, Optional

import deepl
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.config import get_settings
from app.logger import error as log_error, info, warning
from app.schemas.pdf import Block


@dataclass
class TranslatedBlock:
    """
    A translated text block with metadata.
    
    Contains the original block, translated text, and language information.
    """
    original: Block  # Original block from PDF extraction
    translated_text: str  # Translated text content
    source_lang: str  # Detected/specified source language
    target_lang: str  # Target language code
    billed_characters: int  # Characters billed by DeepL


class TranslationService:
    """
    Service for translating text blocks using DeepL API.
    
    Features:
    - Batch processing (10 blocks per request) for cost optimization
    - Retry logic with exponential backoff for rate limiting
    - Cost tracking for billing
    - Support for multiple language pairs (EN→JA, EN→VI, EN→ZH, etc.)
    """

    # Batch size for API calls (balance between cost and latency)
    BATCH_SIZE = 10

    # DeepL character pricing (Pro tier)
    COST_PER_CHARACTER = 0.00002  # $20 per 1M characters

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize DeepL translation client.
        
        Args:
            api_key: DeepL API key (defaults to config)
        """
        settings = get_settings()
        self.api_key = api_key or settings.deepl_api_key
        
        if not self.api_key:
            raise ValueError("DeepL API key not configured")
        
        # Initialize DeepL translator
        self.translator = deepl.Translator(self.api_key)
        
        info("Translation service initialized", api_key_length=len(self.api_key))

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(deepl.exceptions.TooManyRequestsException),
    )
    async def translate_text(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
    ) -> tuple[str, int]:
        """
        Translate a single text string.
        
        Args:
            text: Text to translate
            source_lang: Source language code (or "auto" for detection)
            target_lang: Target language code (e.g., "JA", "VI", "ZH")
            
        Returns:
            Tuple of (translated_text, billed_characters)
            
        Raises:
            deepl.DeepLException: If translation fails
        """
        if not text or not text.strip():
            return "", 0
        
        try:
            # Prepare source language (None for auto-detect)
            source = None if source_lang.lower() == "auto" else source_lang.upper()
            
            # Call DeepL API
            result = self.translator.translate_text(
                text,
                source_lang=source,
                target_lang=target_lang.upper(),
            )
            
            # Extract translated text and billing info
            translated = result.text
            billed = len(text)  # DeepL bills by source characters
            
            info(
                "Text translated",
                source_lang=source or "auto",
                target_lang=target_lang,
                source_chars=len(text),
                billed_chars=billed,
            )
            
            return translated, billed
            
        except deepl.exceptions.QuotaExceededException as e:
            log_error("DeepL quota exceeded", exc=e)
            raise
        except deepl.exceptions.TooManyRequestsException as e:
            warning("DeepL rate limit hit, retrying...", exc=e)
            raise  # Will be retried by @retry decorator
        except Exception as e:
            log_error("Translation failed", exc=e, text_length=len(text))
            raise

    async def batch_translate(
        self,
        blocks: List[Block],
        source_lang: str,
        target_lang: str,
    ) -> tuple[List[TranslatedBlock], float]:
        """
        Translate multiple text blocks in batches.
        
        Groups blocks into batches of BATCH_SIZE to optimize API calls
        and reduce costs. Each batch is sent as a single API request.
        
        Args:
            blocks: List of text blocks from PDF extraction
            source_lang: Source language code (or "auto")
            target_lang: Target language code
            
        Returns:
            Tuple of (translated_blocks, total_cost_usd)
        """
        if not blocks:
            return [], 0.0
        
        start_time = time.time()
        translated_blocks: List[TranslatedBlock] = []
        total_billed_chars = 0
        
        # Group blocks into batches
        batches = [
            blocks[i:i + self.BATCH_SIZE]
            for i in range(0, len(blocks), self.BATCH_SIZE)
        ]
        
        info(
            "Starting batch translation",
            total_blocks=len(blocks),
            num_batches=len(batches),
            batch_size=self.BATCH_SIZE,
        )
        
        # Process each batch
        for batch_idx, batch in enumerate(batches):
            # Extract texts from blocks (skip empty blocks)
            texts = [block.text for block in batch if block.text.strip()]
            
            if not texts:
                continue
            
            try:
                # Prepare source language
                source = None if source_lang.lower() == "auto" else source_lang.upper()
                
                # Translate entire batch in one API call
                results = self.translator.translate_text(
                    texts,
                    source_lang=source,
                    target_lang=target_lang.upper(),
                )
                
                # Handle single result (when batch has 1 item)
                if not isinstance(results, list):
                    results = [results]
                
                # Create TranslatedBlock objects
                for block, result in zip(batch, results):
                    billed_chars = len(block.text)
                    total_billed_chars += billed_chars
                    
                    translated_block = TranslatedBlock(
                        original=block,
                        translated_text=result.text,
                        source_lang=result.detected_source_lang or source_lang,
                        target_lang=target_lang,
                        billed_characters=billed_chars,
                    )
                    translated_blocks.append(translated_block)
                
                info(
                    "Batch translated",
                    batch_idx=batch_idx + 1,
                    batch_size=len(batch),
                    billed_chars=sum(len(t) for t in texts),
                )
                
            except deepl.exceptions.QuotaExceededException as e:
                log_error("DeepL quota exceeded during batch", exc=e, batch_idx=batch_idx)
                raise
            except deepl.exceptions.TooManyRequestsException as e:
                warning(
                    "DeepL rate limit hit during batch, retrying...",
                    exc=e,
                    batch_idx=batch_idx,
                )
                # Wait and retry (exponential backoff handled by @retry decorator)
                raise
            except Exception as e:
                log_error(
                    "Batch translation failed",
                    exc=e,
                    batch_idx=batch_idx,
                    batch_size=len(batch),
                )
                raise
        
        # Calculate total cost
        total_cost = total_billed_chars * self.COST_PER_CHARACTER
        elapsed_ms = int((time.time() - start_time) * 1000)
        
        info(
            "Batch translation complete",
            total_blocks=len(translated_blocks),
            total_chars=total_billed_chars,
            cost_usd=f"${total_cost:.4f}",
            time_ms=elapsed_ms,
        )
        
        return translated_blocks, total_cost

    def get_usage(self) -> dict:
        """
        Get current DeepL API usage statistics.
        
        Returns:
            Dict with character count and limit
        """
        try:
            usage = self.translator.get_usage()
            
            return {
                "character_count": usage.character.count,
                "character_limit": usage.character.limit,
                "character_remaining": usage.character.limit - usage.character.count if usage.character.limit else None,
            }
        except Exception as e:
            log_error("Failed to get DeepL usage", exc=e)
            return {
                "character_count": None,
                "character_limit": None,
                "character_remaining": None,
            }

    def get_supported_languages(self) -> dict:
        """
        Get list of supported source and target languages.
        
        Returns:
            Dict with source and target language lists
        """
        try:
            source_langs = self.translator.get_source_languages()
            target_langs = self.translator.get_target_languages()
            
            return {
                "source": [{"code": lang.code, "name": lang.name} for lang in source_langs],
                "target": [{"code": lang.code, "name": lang.name} for lang in target_langs],
            }
        except Exception as e:
            log_error("Failed to get supported languages", exc=e)
            return {"source": [], "target": []}
