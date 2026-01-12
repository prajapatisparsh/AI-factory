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
        retry=retry_if_exception_type((RateLimitError, ConnectionError)),
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
                    raise APIError(f"Daily token limit exceeded. Wait {wait_time} or upgrade tier: {e}")
                
                logger.error(f"⚠️ RATE LIMIT EXCEEDED: {e}")
                logger.error(f"Llama 3.3 70B limits: 30 requests/min, 12K tokens/min, 1K requests/day, 100K tokens/day")
                raise RateLimitError(f"Rate limit exceeded: {e}")
            
            # Check for connection errors
            if 'connection' in error_str or 'timeout' in error_str:
                logger.warning(f"Connection error: {e}")
                raise ConnectionError(f"Connection failed: {e}")
            
            # Other API errors
            logger.error(f"API error: {e}")
            raise APIError(f"LLM call failed: {e}")
    
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
        # DON'T include full schema - it confuses the LLM into returning schema definitions
        # Just remind to return pure JSON
        json_system = f"""{system_prompt}

CRITICAL: Respond ONLY with a valid JSON object.
- Start your response with {{ and end with }}
- Do NOT include markdown code blocks (no ```)
- Do NOT include schema definitions or $defs
- Return actual data values, not type definitions
- Do NOT include any explanatory text before or after the JSON"""

        try:
            response = self.call_llm(json_system, user_prompt, temperature, max_tokens)
            
            # Clean common LLM mistakes
            response = self._clean_json_response(response)
            
            success, obj, error = safe_parse_llm_json(response, schema_class)
            
            if success:
                return True, obj, ""
            else:
                logger.warning(f"JSON parsing failed: {error}")
                # Try fallback extraction
                return self._extract_json_fallback(response, schema_class, error)
                
        except AgentError as e:
            return False, None, str(e)
    
    def _clean_json_response(self, response: str) -> str:
        """Clean common JSON formatting issues from LLM response."""
        import re
        
        # Remove markdown code blocks
        response = re.sub(r'```json\s*', '', response)
        response = re.sub(r'```\s*', '', response)
        
        # Remove leading/trailing text to get just the JSON
        json_start = response.find('{')
        json_end = response.rfind('}') + 1
        if json_start != -1 and json_end > json_start:
            response = response[json_start:json_end]
        
        return response.strip()
    
    def _extract_json_fallback(self, response: str, schema_class: Type[T], original_error: str) -> tuple[bool, Optional[T], str]:
        """Fallback JSON extraction with manual field parsing for PMEvaluation."""
        import re
        
        try:
            # Special handling for PMEvaluation (the most problematic schema)
            if schema_class.__name__ == 'PMEvaluation':
                from src.schemas import PMEvaluation, ScoreBreakdown, EvaluationStatus
                
                # Try to extract key fields manually
                score_match = re.search(r'"score"\s*:\s*(\d+)', response)
                status_match = re.search(r'"status"\s*:\s*"(APPROVED|REJECTED)"', response, re.IGNORECASE)
                
                if score_match:
                    score = int(score_match.group(1))
                    # Determine status from score if not found
                    if status_match:
                        status_str = status_match.group(1).upper()
                        status = EvaluationStatus.APPROVED if status_str == "APPROVED" else EvaluationStatus.REJECTED
                    else:
                        status = EvaluationStatus.APPROVED if score >= 90 else EvaluationStatus.REJECTED
                    
                    # Extract issues if available
                    issues = []
                    issues_match = re.search(r'"issues"\s*:\s*\[(.*?)\]', response, re.DOTALL)
                    if issues_match:
                        issues_str = issues_match.group(1)
                        issues = re.findall(r'"([^"]+)"', issues_str)
                    
                    # Extract scolding if available
                    scolding = ""
                    scolding_match = re.search(r'"scolding"\s*:\s*"([^"]*(?:\\.[^"]*)*)"', response, re.DOTALL)
                    if scolding_match:
                        scolding = scolding_match.group(1).replace('\\n', '\n').replace('\\"', '"')
                    
                    # Create evaluation object
                    evaluation = PMEvaluation(
                        score=score,
                        status=status,
                        breakdown=ScoreBreakdown(
                            requirements=min(30, score // 3),
                            architecture=min(25, score // 4),
                            completeness=min(20, score // 5),
                            qa_compliance=min(15, score // 7),
                            security=min(10, score // 10)
                        ),
                        strengths=["Extracted from response"],
                        issues=issues if issues else (["Needs improvement"] if status == EvaluationStatus.REJECTED else []),
                        scolding=scolding if scolding else ("Please review and improve specifications." if status == EvaluationStatus.REJECTED else "")
                    )
                    logger.info(f"Fallback extraction succeeded: score={score}, status={status.value}")
                    return True, evaluation, ""
        except Exception as e:
            logger.warning(f"Fallback extraction failed: {e}")
        
        return False, None, original_error
    
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
    
    # ===== Multi-Agent Communication Methods =====
    
    def receive_message(self, message: 'DiscussionMessage') -> Optional[str]:
        """
        Process an incoming message from another agent.
        
        Args:
            message: The message received
            
        Returns:
            Response content or None
        """
        from src.discussion.protocol import DiscussionMessage, MessageType
        
        self.log(f"Received {message.message_type.value} from {message.sender}")
        
        system_prompt = f"""You are {self.get_agent_name()} receiving a message in a team discussion.

Message type: {message.message_type.value}
From: {message.sender}
Content: {message.content}

Respond appropriately based on your expertise. Be concise (2-3 sentences)."""

        try:
            response = self.call_llm(
                system_prompt,
                f"How do you respond to this as {self.get_agent_name()}?",
                temperature=0.5,
                max_tokens=300
            )
            return response.strip()
        except Exception as e:
            self.log(f"Failed to process message: {e}", "ERROR")
            return None
    
    def respond_to(
        self,
        message: 'DiscussionMessage',
        response_type: 'MessageType'
    ) -> 'DiscussionMessage':
        """
        Generate a response to another agent's message.
        
        Args:
            message: The message being responded to
            response_type: Type of response (AGREEMENT, DISAGREEMENT, etc.)
            
        Returns:
            New DiscussionMessage with the response
        """
        from src.discussion.protocol import DiscussionMessage, MessageType
        
        content = self.receive_message(message)
        
        return DiscussionMessage(
            sender=self.get_agent_name(),
            recipient=message.sender,
            message_type=response_type,
            content=content or "Acknowledged.",
            topic_id=message.topic_id,
            references=[message.id]
        )
    
    def ask_question(
        self,
        recipient: str,
        question: str,
        topic_id: str,
        context: str = ""
    ) -> 'DiscussionMessage':
        """
        Send a question to another agent.
        
        Args:
            recipient: Name of the agent to ask
            question: The question to ask
            topic_id: ID of the discussion topic
            context: Additional context for the question
            
        Returns:
            DiscussionMessage with the question
        """
        from src.discussion.protocol import DiscussionMessage, MessageType
        
        self.log(f"Asking {recipient}: {question[:50]}...")
        
        return DiscussionMessage(
            sender=self.get_agent_name(),
            recipient=recipient,
            message_type=MessageType.QUESTION,
            content=question,
            topic_id=topic_id,
            metadata={'context': context}
        )
    
    def vote(
        self,
        topic_id: str,
        choice: str,
        rationale: str
    ) -> 'DiscussionMessage':
        """
        Cast a vote on a decision.
        
        Args:
            topic_id: ID of the topic being voted on
            choice: The choice being voted for
            rationale: Why this choice is preferred
            
        Returns:
            DiscussionMessage with the vote
        """
        from src.discussion.protocol import DiscussionMessage, MessageType
        
        self.log(f"Voting for: {choice}")
        
        return DiscussionMessage(
            sender=self.get_agent_name(),
            recipient="all",
            message_type=MessageType.AGREEMENT,
            content=f"I vote for: {choice}. Rationale: {rationale}",
            topic_id=topic_id,
            metadata={'vote': choice, 'rationale': rationale}
        )


class GroqClientSingleton:
    """
    Singleton wrapper for Groq client to prevent multiple initializations.
    """
    _instance: Optional[Groq] = None
    
    @classmethod
    def get_client(cls) -> Groq:
        if cls._instance is None:
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise AgentError("GROQ_API_KEY not found")
            
            # Use custom httpx client to avoid proxy-related compatibility issues
            import httpx
            http_client = httpx.Client(timeout=120.0)
            cls._instance = Groq(api_key=api_key, http_client=http_client)
        return cls._instance
    
    @classmethod
    def reset(cls) -> None:
        """Reset the singleton (useful for testing)."""
        cls._instance = None
