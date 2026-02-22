"""
Base Agent class with Groq integration and retry logic.
All agents inherit from this class for consistent behavior.
"""

import os
import json
from abc import ABC, abstractmethod
from typing import Any, Optional, Type, TypeVar
from dotenv import load_dotenv
from groq import Groq
from pydantic import BaseModel
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)
import logging

from src.utils.files import load_playbook
from src.schemas import safe_parse_llm_json

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Type variable for Pydantic models
T = TypeVar('T', bound=BaseModel)


class AgentError(Exception):
    """Base exception for agent errors."""
    pass


class NetworkError(AgentError):
    """Raised when a network or connection error occurs."""
    pass


class RateLimitError(AgentError):
    """Raised when rate limit is hit."""
    pass


class APIError(AgentError):
    """Raised when API call fails."""
    pass


class ValidationError(AgentError):
    """Raised when output validation fails."""
    pass


class BaseAgent(ABC):
    """
    Abstract base class for all AI agents.
    Provides common functionality for LLM calls, playbook loading, and retry logic.
    """
    
    # Llama 3.1 8B Instant - MUCH faster and cheaper than 70B
    # Daily limits: 14,400 req/day, 1M tokens/day (10x more than 70B!)
    MODEL = "llama-3.1-8b-instant"
    
    def __init__(self, playbook_name: Optional[str] = None):
        """
        Initialize the base agent.
        
        Args:
            playbook_name: Name of the playbook to load (e.g., 'pm', 'tech_lead')
        """
        self.playbook_name = playbook_name
        self._client: Optional[Groq] = None
        self._playbook_content: Optional[str] = None
    
    @property
    def client(self) -> Groq:
        """Lazy-load Groq client."""
        if self._client is None:
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise AgentError("GROQ_API_KEY not found in environment variables")
            
            # Use custom httpx client to avoid proxy-related compatibility issues
            # with different Groq library versions
            import httpx
            http_client = httpx.Client(timeout=120.0)
            self._client = Groq(api_key=api_key, http_client=http_client)
        return self._client
    
    @property
    def playbook(self) -> str:
        """Load and cache playbook content."""
        if self._playbook_content is None and self.playbook_name:
            self._playbook_content = load_playbook(self.playbook_name)
        return self._playbook_content or ""
    
    def reload_playbook(self) -> str:
        """Force reload playbook from disk."""
        self._playbook_content = None
        return self.playbook
    
    def build_system_prompt(self, base_prompt: str) -> str:
        """
        Build system prompt with playbook rules appended.
        
        Args:
            base_prompt: The base system prompt for this agent
        
        Returns:
            Complete system prompt with playbook rules
        """
        if self.playbook and self.playbook.strip():
            return f"""{base_prompt}

CRITICAL: Follow these learned rules from your playbook:

{self.playbook}

These rules are based on past failures and must be followed strictly."""
        return base_prompt
    
    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=retry_if_exception_type((RateLimitError, NetworkError)),
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )
    def call_llm(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 8192
    ) -> str:
        """
        Call the Groq LLM with retry logic and exponential backoff.
        
        Args:
            system_prompt: System message for the LLM
            user_prompt: User message/query
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens in response (default: 8192 for complete outputs)
        
        Returns:
            LLM response text
        
        Raises:
            RateLimitError: If rate limit persists after retries
            APIError: If API call fails for other reasons
        """
        try:
            logger.info(f"Calling {self.MODEL} with max_tokens={max_tokens}")
            response = self.client.chat.completions.create(
                model=self.MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                stream=False
            )
            
            content = response.choices[0].message.content
            if content is None:
                raise APIError("Empty response from LLM")
            
            # Check if response was truncated
            finish_reason = response.choices[0].finish_reason
            if finish_reason == "length":
                logger.warning(f"⚠️ TRUNCATION DETECTED! Output exceeded {max_tokens} tokens")
                content += "\n\n[⚠️ OUTPUT TRUNCATED - Response exceeded token limit]"
            
            logger.info(f"✅ LLM response: finish_reason={finish_reason}, tokens={response.usage.total_tokens}")
            return content.strip()
            
        except Exception as e:
            error_str = str(e).lower()
            
            # Check for rate limit errors
            if 'rate' in error_str and 'limit' in error_str:
                # Check if it's a DAILY token limit (TPD - Tokens Per Day)
                if 'tokens per day' in error_str or 'tpd' in error_str:
                    # Extract wait time if available
                    import re
                    wait_match = re.search(r'try again in ([\d\.]+)([hms])', str(e))
                    wait_time = "unknown time"
                    if wait_match:
                        value, unit = wait_match.groups()
                        wait_time = f"{value}{unit}"
                    
                    logger.error(f"❌ DAILY TOKEN LIMIT EXCEEDED - STOPPING RETRIES")
                    logger.error(f"⏳ Daily limit: 100K tokens. Wait required: {wait_time}")
                    logger.error(f"💡 Solution: Wait until limit resets OR upgrade to Dev Tier at https://console.groq.com/settings/billing")
                    
                    # Don't retry on daily limit - it won't help!
                    raise APIError(f"Daily token limit exceeded. Wait {wait_time} or upgrade tier: {e}") from e
            
            logger.error(f"⚠️ RATE LIMIT EXCEEDED: {e}")
            logger.error(f"Llama 3.3 70B limits: 30 requests/min, 12K tokens/min, 1K requests/day, 100K tokens/day")
            raise RateLimitError(f"Rate limit exceeded: {e}") from e
            
        # Check for connection errors
        if 'connection' in error_str or 'timeout' in error_str:
            logger.warning(f"Connection error: {e}")
            raise NetworkError(f"Connection failed: {e}") from e
        
        # Other API errors
        logger.error(f"API error: {e}")
        raise APIError(f"LLM call failed: {e}") from e
    
    def call_llm_json(
        self,
        system_prompt: str,
        user_prompt: str,
        schema_class: Type[T],
        temperature: float = 0.3,  # Lower temp for structured output
        max_tokens: int = 8192
    ) -> tuple[bool, Optional[T], str]:
        """
        Call LLM and parse response as JSON matching a Pydantic schema.
        
        Args:
            system_prompt: System message (should request JSON output)
            user_prompt: User message
            schema_class: Pydantic model class for validation
            temperature: Sampling temperature
            max_tokens: Max response tokens
        
        Returns:
            Tuple of (success, parsed_object_or_none, error_message)
        """
        # Enhance system prompt to request JSON
        json_system = f"""{system_prompt}

IMPORTANT: You must respond with valid JSON that matches this schema:
{schema_class.model_json_schema()}

Do not include any text before or after the JSON. Start with {{ and end with }}."""

        try:
            response = self.call_llm(json_system, user_prompt, temperature, max_tokens)
            success, obj, error = safe_parse_llm_json(response, schema_class)
            
            if success:
                return True, obj, ""
            else:
                logger.warning(f"JSON parsing failed: {error}")
                return False, None, error
                
        except AgentError as e:
            return False, None, str(e)
    
    def validate_output(self, response: str, schema_class: Type[T]) -> tuple[bool, Optional[T], str]:
        """
        Validate a response string against a Pydantic schema.
        
        Args:
            response: Raw response text (may contain JSON)
            schema_class: Pydantic model class
        
        Returns:
            Tuple of (success, validated_object_or_none, error_message)
        """
        return safe_parse_llm_json(response, schema_class)
    
    @abstractmethod
    def get_agent_name(self) -> str:
        """Return the name of this agent for logging."""
        pass
    
    def log(self, message: str, level: str = "INFO") -> None:
        """Log a message with agent context."""
        from src.utils.state import log_message
        log_message(f"[{self.get_agent_name()}] {message}", level)
