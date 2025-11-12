"""
Configuration classes for the Biography Video Prompt Generator.
"""
from dataclasses import dataclass, field
from typing import Optional, Dict


@dataclass
class APIConfig:
    """Configuration for API providers."""
    provider: str = "openrouter"  # openrouter, openai, gemini, anthropic
    api_key: str = ""
    model: str = ""
    max_tokens: int = 4000
    temperature: float = 0.7
    
    # Rate limiting (requests per minute)
    rate_limits: Dict[str, int] = field(default_factory=lambda: {
        "openrouter": 20,
        "openai": 50,
        "gemini": 15,
        "anthropic": 10
    })
    
    def get_rate_limit(self) -> int:
        """Get rate limit for current provider."""
        return self.rate_limits.get(self.provider, 10)


@dataclass
class Settings:
    """Application settings."""
    # Video settings
    frame_interval_seconds: float = 6.0  # 3-30 seconds
    narration_speed_wpm: int = 150  # 100-200 words per minute
    visual_style: str = "historical illustration"
    
    # Processing options
    dense_mode: bool = False  # Detailed prompts
    character_consistency: bool = False  # Maintain character descriptions
    chunk_size: int = 1000  # Words per chunk
    scene_duration: float = 6.0  # Seconds per scene (5-7 range)
    
    # Quality settings
    enable_deduplication: bool = True  # Remove duplicate prompts
    deduplication_threshold: float = 0.85  # Similarity threshold (0.0-1.0)
    enable_quality_filter: bool = True  # Filter low-quality prompts
    min_quality_score: float = 0.5  # Minimum quality score (0.0-1.0)
    enable_enhancement: bool = True  # Auto-enhance prompts
    
    # API configuration
    api_config: APIConfig = field(default_factory=APIConfig)
    
    # Paths
    input_folder: str = "texts_to_process"
    output_folder: str = "video_prompts"
    
    # Retry settings
    max_retries: int = 5
    initial_retry_delay: float = 1.0
    max_retry_delay: float = 60.0
    retry_exponential_base: float = 2.0
    
    def __post_init__(self):
        """Validate settings after initialization."""
        if not 3 <= self.frame_interval_seconds <= 30:
            raise ValueError("frame_interval_seconds must be between 3 and 30")
        if not 100 <= self.narration_speed_wpm <= 200:
            raise ValueError("narration_speed_wpm must be between 100 and 200")
        if not 5 <= self.scene_duration <= 7:
            self.scene_duration = 6.0  # Default to middle value
        if not 0.0 <= self.deduplication_threshold <= 1.0:
            raise ValueError("deduplication_threshold must be between 0.0 and 1.0")
        if not 0.0 <= self.min_quality_score <= 1.0:
            raise ValueError("min_quality_score must be between 0.0 and 1.0")


@dataclass
class PromptStructure:
    """12-element prompt structure."""
    shot_type: str = ""
    subject: str = ""
    action: str = ""
    setting: str = ""
    composition: str = ""
    lighting: str = ""
    mood: str = ""
    key_details: str = ""
    color_palette: str = ""
    style: str = ""
    technical: str = "8k, highly detailed, cinematic"
    character_appearance: str = ""
    
    def to_prompt(self) -> str:
        """Convert structure to formatted prompt string."""
        parts = []
        if self.shot_type:
            parts.append(f"{self.shot_type}")
        if self.subject:
            parts.append(f"{self.subject}")
        if self.action:
            parts.append(f"{self.action}")
        if self.setting:
            parts.append(f"{self.setting}")
        if self.composition:
            parts.append(f"Composition: {self.composition}")
        if self.lighting:
            parts.append(f"Lighting: {self.lighting}")
        if self.mood:
            parts.append(f"Mood: {self.mood}")
        if self.key_details:
            parts.append(f"Details: {self.key_details}")
        if self.color_palette:
            parts.append(f"Colors: {self.color_palette}")
        if self.style:
            parts.append(f"Style: {self.style}")
        if self.technical:
            parts.append(self.technical)
        if self.character_appearance:
            parts.append(f"Character: {self.character_appearance}")
        
        return ", ".join(parts)
