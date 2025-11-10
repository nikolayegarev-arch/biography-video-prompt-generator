"""
Unified API manager for OpenRouter, OpenAI, Gemini, and Anthropic.
"""
import requests
import logging
from typing import Dict, Any, Optional
from config import APIConfig
from exceptions import APIError, RateLimitError
from utils.retry_handler import RateLimiter

logger = logging.getLogger(__name__)


class APIManager:
    """Unified API manager for multiple AI providers."""
    
    def __init__(self, config: APIConfig):
        """
        Initialize API manager.
        
        Args:
            config: API configuration
        """
        self.config = config
        self.rate_limiter = RateLimiter(config.get_rate_limit())
        self.session = requests.Session()
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API request based on provider."""
        if self.config.provider == "openrouter":
            return {
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/biography-video-prompt-generator",
            }
        elif self.config.provider == "openai":
            return {
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
            }
        elif self.config.provider == "gemini":
            return {
                "Content-Type": "application/json",
            }
        elif self.config.provider == "anthropic":
            return {
                "x-api-key": self.config.api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01",
            }
        else:
            raise APIError(f"Unknown provider: {self.config.provider}")
    
    def _get_endpoint(self) -> str:
        """Get API endpoint based on provider."""
        if self.config.provider == "openrouter":
            return "https://openrouter.ai/api/v1/chat/completions"
        elif self.config.provider == "openai":
            return "https://api.openai.com/v1/chat/completions"
        elif self.config.provider == "gemini":
            return f"https://generativelanguage.googleapis.com/v1beta/models/{self.config.model}:generateContent?key={self.config.api_key}"
        elif self.config.provider == "anthropic":
            return "https://api.anthropic.com/v1/messages"
        else:
            raise APIError(f"Unknown provider: {self.config.provider}")
    
    def _format_request(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """Format request payload based on provider."""
        if self.config.provider in ["openrouter", "openai"]:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            return {
                "model": self.config.model,
                "messages": messages,
                "max_tokens": self.config.max_tokens,
                "temperature": self.config.temperature,
            }
        
        elif self.config.provider == "gemini":
            content = prompt
            if system_prompt:
                content = f"{system_prompt}\n\n{prompt}"
            
            return {
                "contents": [{
                    "parts": [{"text": content}]
                }],
                "generationConfig": {
                    "temperature": self.config.temperature,
                    "maxOutputTokens": self.config.max_tokens,
                }
            }
        
        elif self.config.provider == "anthropic":
            return {
                "model": self.config.model,
                "max_tokens": self.config.max_tokens,
                "temperature": self.config.temperature,
                "messages": [{"role": "user", "content": prompt}],
                **({"system": system_prompt} if system_prompt else {})
            }
        
        else:
            raise APIError(f"Unknown provider: {self.config.provider}")
    
    def _extract_response(self, response_data: Dict[str, Any]) -> str:
        """Extract text response based on provider."""
        try:
            if self.config.provider in ["openrouter", "openai"]:
                return response_data["choices"][0]["message"]["content"]
            
            elif self.config.provider == "gemini":
                return response_data["candidates"][0]["content"]["parts"][0]["text"]
            
            elif self.config.provider == "anthropic":
                return response_data["content"][0]["text"]
            
            else:
                raise APIError(f"Unknown provider: {self.config.provider}")
        except (KeyError, IndexError) as e:
            raise APIError(f"Failed to extract response from {self.config.provider}: {e}")
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generate text using configured AI provider.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            
        Returns:
            Generated text
            
        Raises:
            APIError: If API call fails
            RateLimitError: If rate limit is exceeded
        """
        # Apply rate limiting
        self.rate_limiter.wait_if_needed()
        
        try:
            endpoint = self._get_endpoint()
            headers = self._get_headers()
            payload = self._format_request(prompt, system_prompt)
            
            logger.debug(f"Making request to {self.config.provider} ({self.config.model})")
            
            response = self.session.post(
                endpoint,
                headers=headers,
                json=payload,
                timeout=120
            )
            
            # Handle rate limiting
            if response.status_code == 429:
                retry_after = response.headers.get('Retry-After', '60')
                logger.warning(f"Rate limit hit for {self.config.provider}. Retry after: {retry_after}s")
                raise RateLimitError(f"Rate limit exceeded. Retry after {retry_after} seconds")
            
            # Handle other errors
            if response.status_code != 200:
                error_msg = f"API error ({response.status_code}): {response.text}"
                logger.error(error_msg)
                raise APIError(error_msg)
            
            response_data = response.json()
            return self._extract_response(response_data)
        
        except RateLimitError:
            raise
        except requests.exceptions.Timeout:
            raise APIError(f"Request timeout for {self.config.provider}")
        except requests.exceptions.ConnectionError:
            raise APIError(f"Connection error to {self.config.provider}")
        except Exception as e:
            if isinstance(e, (APIError, RateLimitError)):
                raise
            raise APIError(f"Unexpected error with {self.config.provider}: {e}")
    
    def close(self):
        """Close the session."""
        self.session.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
