"""Service for generating alternative translations using Claude API"""

from typing import List, Optional

import anthropic
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.config import get_settings
from app.logger import error as log_error, info, warning


class AlternativesService:
    """
    Service for generating alternative translations using Claude API.
    
    Features:
    - Uses Claude 3.5 Haiku for cost efficiency
    - Generates 2-5 alternative translations
    - Cost tracking
    """

    # Claude 3.5 Haiku pricing (as of 2024)
    COST_PER_INPUT_TOKEN = 0.80 / 1_000_000  # $0.80 per million input tokens
    COST_PER_OUTPUT_TOKEN = 4.00 / 1_000_000  # $4.00 per million output tokens

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
        
        info("Alternatives service initialized", api_key_length=len(self.api_key))

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(anthropic.RateLimitError),
    )
    async def generate_alternatives(
        self,
        text: str,
        target_lang: str,
        count: int = 3,
    ) -> tuple[List[str], float]:
        """
        Generate alternative translations for a given text.
        
        Args:
            text: Text to generate alternatives for
            target_lang: Target language code (e.g., "JA", "ZH", "VI")
            count: Number of alternatives to generate (1-5)
            
        Returns:
            Tuple of (alternatives_list, cost_usd)
            
        Raises:
            anthropic.APIError: If API call fails
        """
        if not text or not text.strip():
            return [], 0.0
        
        if count < 1 or count > 5:
            count = 3  # Default to 3
        
        try:
            # Build prompt for generating alternatives
            system_prompt = (
                "You are a professional translator. "
                "Generate alternative translations that are natural, accurate, and varied in style. "
                "Each alternative should be a valid translation with slightly different phrasing or tone."
            )
            
            lang_names = {
                "JA": "Japanese",
                "ZH": "Chinese",
                "VI": "Vietnamese",
                "KO": "Korean",
                "ES": "Spanish",
                "FR": "French",
                "DE": "German",
                "IT": "Italian",
                "PT": "Portuguese",
                "RU": "Russian",
            }
            
            target_lang_name = lang_names.get(target_lang.upper(), target_lang)
            
            user_message = (
                f"Generate exactly {count} alternative translations of the following text into {target_lang_name}.\n\n"
                f"Text to translate:\n{text}\n\n"
                f"Provide {count} different translations, each on a new line. "
                "Each translation should be natural and accurate, but with different phrasing or style. "
                "Number each alternative (1., 2., 3., etc.)."
            )
            
            # Call Claude API
            message = self.client.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=2048,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": user_message
                    }
                ]
            )
            
            # Extract response and parse alternatives
            response_text = message.content[0].text if message.content else ""
            
            # Parse alternatives from response
            alternatives = []
            lines = response_text.strip().split('\n')
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Remove numbering (1., 2., etc.) and quotes
                line = line.lstrip('0123456789. ').strip()
                line = line.strip('"\'')
                
                if line:
                    alternatives.append(line)
            
            # If we got fewer alternatives than requested, pad with empty strings
            # If we got more, take only the requested count
            while len(alternatives) < count:
                alternatives.append("")
            alternatives = alternatives[:count]
            
            # Calculate cost
            input_tokens = message.usage.input_tokens
            output_tokens = message.usage.output_tokens
            cost = (input_tokens * self.COST_PER_INPUT_TOKEN) + \
                   (output_tokens * self.COST_PER_OUTPUT_TOKEN)
            
            info(
                "Alternatives generated",
                input_chars=len(text),
                alternatives_count=len([a for a in alternatives if a]),
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost_usd=f"${cost:.6f}",
            )
            
            return alternatives, cost
            
        except anthropic.RateLimitError as e:
            warning("Claude rate limit hit, retrying...", exc=e)
            raise  # Will be retried by @retry decorator
        except anthropic.APIError as e:
            log_error("Claude API error", exc=e, text_length=len(text))
            raise
        except Exception as e:
            log_error("Alternatives generation failed", exc=e, text_length=len(text))
            raise
