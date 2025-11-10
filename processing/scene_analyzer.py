"""
Scene analyzer for automatic detection of shot types, emotions, objects, time, and weather.
"""
import re
import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


class SceneAnalyzer:
    """Analyze scenes for visual elements."""
    
    # Shot type keywords
    SHOT_TYPES = {
        "wide shot": ["landscape", "full scene", "establishing", "panorama", "wide view", "vast"],
        "medium shot": ["waist up", "mid-range", "conversation", "interaction"],
        "close-up": ["face", "eyes", "expression", "detail", "intimate", "focused"],
        "extreme close-up": ["extreme detail", "macro", "very close"],
        "tracking shot": ["following", "moving with", "tracking", "pursuit"],
        "aerial shot": ["overhead", "bird's eye", "from above", "aerial view"],
        "over-the-shoulder": ["looking over", "perspective from behind"],
        "low angle": ["looking up", "from below", "towering"],
        "high angle": ["looking down", "from above"]
    }
    
    # Emotion keywords with intensity
    EMOTIONS = {
        "rage": ["furious", "enraged", "wrathful", "livid", "angry", "irate"],
        "joy": ["happy", "joyful", "delighted", "cheerful", "ecstatic", "elated"],
        "melancholy": ["sad", "melancholic", "sorrowful", "mournful", "gloomy", "depressed"],
        "anxiety": ["anxious", "worried", "nervous", "tense", "uneasy", "fearful"],
        "determination": ["determined", "resolute", "focused", "steadfast", "unwavering"],
        "surprise": ["surprised", "shocked", "astonished", "amazed", "startled"],
        "contempt": ["disdainful", "contemptuous", "scornful", "dismissive"],
        "fear": ["afraid", "scared", "terrified", "frightened", "horrified"],
        "disgust": ["disgusted", "revolted", "repulsed", "nauseated"],
        "calm": ["calm", "peaceful", "serene", "tranquil", "composed"]
    }
    
    # Object categories
    OBJECT_KEYWORDS = {
        "documents": ["letter", "document", "paper", "scroll", "book", "manuscript", "contract"],
        "furniture": ["chair", "table", "desk", "bed", "cabinet", "shelf", "sofa"],
        "clothing": ["dress", "suit", "coat", "hat", "uniform", "robe", "cloak"],
        "weapons": ["sword", "gun", "rifle", "dagger", "weapon", "pistol"],
        "nature": ["tree", "flower", "plant", "grass", "leaves", "forest"],
        "architecture": ["building", "palace", "castle", "house", "structure", "monument"],
        "vehicles": ["carriage", "car", "horse", "ship", "boat", "train"],
        "tools": ["pen", "quill", "hammer", "tool", "instrument"],
        "decorations": ["painting", "portrait", "chandelier", "curtain", "decoration"],
        "food": ["food", "meal", "feast", "drink", "wine", "tea"]
    }
    
    # Time of day keywords
    TIME_KEYWORDS = {
        "dawn": ["dawn", "sunrise", "early morning", "first light"],
        "morning": ["morning", "mid-morning", "forenoon"],
        "afternoon": ["afternoon", "midday", "noon"],
        "golden hour": ["golden hour", "dusk", "sunset", "evening light"],
        "evening": ["evening", "twilight"],
        "night": ["night", "midnight", "darkness", "nocturnal"]
    }
    
    # Weather keywords
    WEATHER_KEYWORDS = {
        "clear": ["clear", "cloudless"],
        "sunny": ["sunny", "bright", "sunshine"],
        "rainy": ["rain", "rainy", "downpour", "drizzle", "wet"],
        "foggy": ["fog", "foggy", "mist", "misty", "hazy"],
        "overcast": ["overcast", "cloudy", "gray sky", "clouds"],
        "snowy": ["snow", "snowy", "blizzard", "snowfall"],
        "stormy": ["storm", "stormy", "thunder", "lightning"]
    }
    
    def analyze_shot_type(self, text: str) -> str:
        """
        Analyze text to determine shot type.
        
        Args:
            text: Text to analyze
            
        Returns:
            Shot type
        """
        text_lower = text.lower()
        
        for shot_type, keywords in self.SHOT_TYPES.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return shot_type
        
        # Default to medium shot
        return "medium shot"
    
    def analyze_emotions(self, text: str) -> Dict[str, str]:
        """
        Analyze text for emotions.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary of emotion: intensity
        """
        text_lower = text.lower()
        emotions = {}
        
        for emotion, keywords in self.EMOTIONS.items():
            matches = sum(1 for keyword in keywords if keyword in text_lower)
            if matches > 0:
                # Determine intensity based on number of matches
                if matches >= 3:
                    intensity = "high"
                elif matches >= 2:
                    intensity = "medium"
                else:
                    intensity = "low"
                emotions[emotion] = intensity
        
        return emotions
    
    def analyze_objects(self, text: str) -> List[str]:
        """
        Analyze text for objects.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of detected objects
        """
        text_lower = text.lower()
        objects = []
        
        for category, keywords in self.OBJECT_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text_lower and keyword not in objects:
                    objects.append(keyword)
        
        return objects[:10]  # Limit to top 10
    
    def analyze_time_of_day(self, text: str) -> str:
        """
        Analyze text for time of day.
        
        Args:
            text: Text to analyze
            
        Returns:
            Time of day
        """
        text_lower = text.lower()
        
        for time, keywords in self.TIME_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return time
        
        # Default to afternoon
        return "afternoon"
    
    def analyze_weather(self, text: str) -> str:
        """
        Analyze text for weather.
        
        Args:
            text: Text to analyze
            
        Returns:
            Weather condition
        """
        text_lower = text.lower()
        
        for weather, keywords in self.WEATHER_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return weather
        
        # Default to clear
        return "clear"
    
    def analyze_scene(self, text: str) -> Dict[str, any]:
        """
        Perform complete scene analysis.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with all analysis results
        """
        return {
            "shot_type": self.analyze_shot_type(text),
            "emotions": self.analyze_emotions(text),
            "objects": self.analyze_objects(text),
            "time_of_day": self.analyze_time_of_day(text),
            "weather": self.analyze_weather(text)
        }
