"""
Model Provider - Unified interface for multiple LLM providers.
Supports Groq, Gemini, OpenAI, Anthropic, and Ollama.
"""

import os
import yaml
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum


class ProviderType(Enum):
    GROQ = "groq"
    GEMINI = "gemini"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"


@dataclass
class ModelInfo:
    """Information about a specific model."""
    id: str
    name: str
    provider: ProviderType
    context_window: int
    cost_per_1k_input: float
    cost_per_1k_output: float
    recommended_for: List[str]


class ModelProvider:
    """
    Unified interface for multiple LLM providers.
    
    Usage:
        provider = ModelProvider()
        response = provider.generate("You are helpful", "Hello!", model="gpt-4o")
    """
    
    def __init__(self):
        self.config = self._load_config()
        self._clients: Dict[str, Any] = {}
        self._default_provider = self.config.get("default_provider", "groq")
        self._default_model = self.config.get("default_model", "llama-3.1-70b-versatile")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load model configuration from YAML."""
        config_path = Path(__file__).parent.parent.parent / "config" / "models.yaml"
        
        if config_path.exists():
            with open(config_path, "r") as f:
                return yaml.safe_load(f)
        
        return {"default_provider": "groq", "default_model": "llama-3.1-70b-versatile"}
    
    def _get_provider_for_model(self, model_id: str) -> Optional[ProviderType]:
        """Find which provider a model belongs to."""
        providers = self.config.get("providers", {})
        
        for provider_name, provider_config in providers.items():
            models = provider_config.get("models", [])
            for model in models:
                if model.get("id") == model_id:
                    return ProviderType(provider_name)
        
        return None
    
    def _get_client(self, provider: ProviderType):
        """Get or create client for a provider."""
        if provider.value in self._clients:
            return self._clients[provider.value]
        
        client = None
        
        if provider == ProviderType.GROQ:
            try:
                from groq import Groq
                api_key = os.getenv("GROQ_API_KEY")
                if api_key:
                    client = Groq(api_key=api_key)
            except ImportError:
                pass
        
        elif provider == ProviderType.GEMINI:
            try:
                import google.generativeai as genai
                api_key = os.getenv("GOOGLE_API_KEY")
                if api_key:
                    genai.configure(api_key=api_key)
                    client = genai
            except ImportError:
                pass
        
        elif provider == ProviderType.OPENAI:
            try:
                from openai import OpenAI
                api_key = os.getenv("OPENAI_API_KEY")
                if api_key:
                    client = OpenAI(api_key=api_key)
            except ImportError:
                pass
        
        elif provider == ProviderType.ANTHROPIC:
            try:
                from anthropic import Anthropic
                api_key = os.getenv("ANTHROPIC_API_KEY")
                if api_key:
                    client = Anthropic(api_key=api_key)
            except ImportError:
                pass
        
        elif provider == ProviderType.OLLAMA:
            # Ollama uses HTTP requests, no special client needed
            client = "ollama"
        
        self._clients[provider.value] = client
        return client
    
    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000
    ) -> str:
        """
        Generate response using specified model.
        
        Args:
            system_prompt: System prompt
            user_prompt: User prompt
            model: Model ID (e.g., "gpt-4o", "llama-3.1-70b-versatile")
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
        
        Returns:
            Generated text response
        """
        if model is None:
            model = self._default_model
        
        provider = self._get_provider_for_model(model)
        if provider is None:
            # Default to groq if model not found
            provider = ProviderType.GROQ
            model = self._default_model
        
        client = self._get_client(provider)
        if client is None:
            raise ValueError(f"No client available for provider: {provider.value}")
        
        # Route to appropriate provider
        if provider == ProviderType.GROQ:
            return self._generate_groq(client, system_prompt, user_prompt, model, temperature, max_tokens)
        elif provider == ProviderType.GEMINI:
            return self._generate_gemini(client, system_prompt, user_prompt, model, temperature, max_tokens)
        elif provider == ProviderType.OPENAI:
            return self._generate_openai(client, system_prompt, user_prompt, model, temperature, max_tokens)
        elif provider == ProviderType.ANTHROPIC:
            return self._generate_anthropic(client, system_prompt, user_prompt, model, temperature, max_tokens)
        elif provider == ProviderType.OLLAMA:
            return self._generate_ollama(system_prompt, user_prompt, model, temperature, max_tokens)
        
        raise ValueError(f"Unsupported provider: {provider}")
    
    def _generate_groq(self, client, system_prompt, user_prompt, model, temperature, max_tokens) -> str:
        """Generate using Groq."""
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    
    def _generate_gemini(self, genai, system_prompt, user_prompt, model, temperature, max_tokens) -> str:
        """Generate using Google Gemini."""
        model_instance = genai.GenerativeModel(
            model,
            system_instruction=system_prompt
        )
        
        response = model_instance.generate_content(
            user_prompt,
            generation_config={
                "temperature": temperature,
                "max_output_tokens": max_tokens
            }
        )
        return response.text
    
    def _generate_openai(self, client, system_prompt, user_prompt, model, temperature, max_tokens) -> str:
        """Generate using OpenAI."""
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    
    def _generate_anthropic(self, client, system_prompt, user_prompt, model, temperature, max_tokens) -> str:
        """Generate using Anthropic Claude."""
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        return response.content[0].text
    
    def _generate_ollama(self, system_prompt, user_prompt, model, temperature, max_tokens) -> str:
        """Generate using Ollama (local)."""
        import requests
        
        base_url = self.config.get("providers", {}).get("ollama", {}).get("base_url", "http://localhost:11434")
        
        response = requests.post(
            f"{base_url}/api/generate",
            json={
                "model": model,
                "prompt": f"{system_prompt}\n\n{user_prompt}",
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            },
            timeout=120
        )
        
        if response.status_code == 200:
            return response.json().get("response", "")
        else:
            raise Exception(f"Ollama error: {response.text}")
    
    def get_available_models(self) -> List[ModelInfo]:
        """Get list of all configured models."""
        models = []
        providers = self.config.get("providers", {})
        
        for provider_name, provider_config in providers.items():
            for model_config in provider_config.get("models", []):
                models.append(ModelInfo(
                    id=model_config.get("id"),
                    name=model_config.get("name"),
                    provider=ProviderType(provider_name),
                    context_window=model_config.get("context_window", 4096),
                    cost_per_1k_input=model_config.get("cost_per_1k_input", 0),
                    cost_per_1k_output=model_config.get("cost_per_1k_output", 0),
                    recommended_for=model_config.get("recommended_for", [])
                ))
        
        return models
    
    def get_recommended_model(self, task: str) -> Optional[str]:
        """Get recommended model for a specific task."""
        for model in self.get_available_models():
            if task in model.recommended_for:
                # Check if provider is available
                client = self._get_client(model.provider)
                if client:
                    return model.id
        
        return self._default_model
    
    def get_agent_model(self, agent_name: str) -> str:
        """Get preferred model for a specific agent."""
        prefs = self.config.get("agent_preferences", {})
        agent_pref = prefs.get(agent_name, {})
        
        if agent_pref:
            model_id = agent_pref.get("model")
            provider = agent_pref.get("provider")
            
            # Check if provider is available
            if provider and self._get_client(ProviderType(provider)):
                return model_id
        
        return self._default_model


# Global provider instance
_provider_instance: Optional[ModelProvider] = None


def get_model_provider() -> ModelProvider:
    """Get or create global model provider instance."""
    global _provider_instance
    if _provider_instance is None:
        _provider_instance = ModelProvider()
    return _provider_instance
