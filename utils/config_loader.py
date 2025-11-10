"""
Configuration loader for API keys and settings.
"""
import os
from pathlib import Path
from typing import Dict, Optional
from dotenv import load_dotenv
from exceptions import ConfigurationError


def load_api_keys() -> Dict[str, str]:
    """
    Load API keys from .env file or config.txt.
    
    Returns:
        Dictionary of API keys
    """
    api_keys = {}
    
    # Try loading from .env first
    env_path = Path(".env")
    if env_path.exists():
        load_dotenv(env_path)
    
    # Try loading from config.txt as fallback
    config_path = Path("config.txt")
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        if value:  # Only add non-empty values
                            os.environ[key] = value
        except Exception as e:
            raise ConfigurationError(f"Failed to load config.txt: {e}")
    
    # Extract API keys from environment
    api_keys['openrouter'] = os.getenv('OPENROUTER_API_KEY', '')
    api_keys['openai'] = os.getenv('OPENAI_API_KEY', '')
    api_keys['gemini'] = os.getenv('GEMINI_API_KEY', '')
    api_keys['anthropic'] = os.getenv('ANTHROPIC_API_KEY', '')
    
    return api_keys


def get_api_key(provider: str) -> Optional[str]:
    """
    Get API key for a specific provider.
    
    Args:
        provider: Provider name (openrouter, openai, gemini, anthropic)
        
    Returns:
        API key or None if not found
    """
    api_keys = load_api_keys()
    return api_keys.get(provider.lower())


def validate_api_key(api_key: str, provider: str) -> bool:
    """
    Validate API key format.
    
    Args:
        api_key: API key to validate
        provider: Provider name
        
    Returns:
        True if valid, False otherwise
    """
    if not api_key or not api_key.strip():
        return False
    
    # Basic validation - check if it looks like an API key
    api_key = api_key.strip()
    
    if provider == "openrouter":
        return api_key.startswith("sk-or-") and len(api_key) > 10
    elif provider == "openai":
        return api_key.startswith("sk-") and len(api_key) > 20
    elif provider == "gemini":
        return len(api_key) > 20  # Gemini keys don't have a specific prefix
    elif provider == "anthropic":
        return api_key.startswith("sk-ant-") and len(api_key) > 20
    
    return len(api_key) > 10  # Generic validation
