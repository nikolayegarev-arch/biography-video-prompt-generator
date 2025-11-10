"""
Settings management for GUI.
"""
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class GUISettings:
    """Manage GUI settings persistence."""
    
    def __init__(self, settings_file: str = "gui_settings_dense.json"):
        """
        Initialize GUI settings.
        
        Args:
            settings_file: Path to settings file
        """
        self.settings_file = Path(settings_file)
        self.settings = self.load()
    
    def load(self) -> Dict[str, Any]:
        """
        Load settings from file.
        
        Returns:
            Settings dictionary
        """
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                logger.info(f"Loaded settings from {self.settings_file}")
                return settings
            except Exception as e:
                logger.warning(f"Failed to load settings: {e}")
        
        # Return default settings
        return self.get_defaults()
    
    def save(self):
        """Save settings to file."""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, indent=2, fp=f)
            logger.info(f"Saved settings to {self.settings_file}")
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a setting value.
        
        Args:
            key: Setting key
            default: Default value if key not found
            
        Returns:
            Setting value
        """
        return self.settings.get(key, default)
    
    def set(self, key: str, value: Any):
        """
        Set a setting value.
        
        Args:
            key: Setting key
            value: Setting value
        """
        self.settings[key] = value
    
    def update(self, updates: Dict[str, Any]):
        """
        Update multiple settings.
        
        Args:
            updates: Dictionary of updates
        """
        self.settings.update(updates)
    
    @staticmethod
    def get_defaults() -> Dict[str, Any]:
        """
        Get default settings.
        
        Returns:
            Default settings dictionary
        """
        return {
            "last_input_folder": "",
            "last_output_folder": "",
            "last_provider": "openrouter",
            "last_model": "",
            "frame_interval": 6.0,
            "narration_speed": 150,
            "visual_style": "historical illustration",
            "dense_mode": False,
            "character_consistency": False,
            "window_width": 900,
            "window_height": 700,
            "theme": "dark"
        }
    
    def get_visual_styles(self) -> list:
        """
        Get list of available visual styles.
        
        Returns:
            List of visual style names
        """
        return [
            "historical illustration",
            "photorealistic",
            "cinematic",
            "oil painting",
            "watercolor",
            "sketch",
            "vintage photograph",
            "documentary style",
            "dramatic lighting",
            "renaissance painting",
            "impressionist",
            "art nouveau",
            "black and white",
            "sepia tone"
        ]
    
    def get_provider_models(self, provider: str) -> list:
        """
        Get list of models for a provider.
        
        Args:
            provider: Provider name
            
        Returns:
            List of model names
        """
        models = {
            "openrouter": [
                "anthropic/claude-3.5-sonnet",
                "anthropic/claude-3-opus",
                "openai/gpt-4-turbo",
                "openai/gpt-4",
                "google/gemini-pro-1.5",
                "meta-llama/llama-3.1-70b-instruct"
            ],
            "openai": [
                "gpt-4-turbo-preview",
                "gpt-4",
                "gpt-4-32k",
                "gpt-3.5-turbo"
            ],
            "gemini": [
                "gemini-1.5-pro",
                "gemini-1.5-flash",
                "gemini-pro"
            ],
            "anthropic": [
                "claude-3-5-sonnet-20241022",
                "claude-3-opus-20240229",
                "claude-3-sonnet-20240229",
                "claude-3-haiku-20240307"
            ]
        }
        return models.get(provider, [])
