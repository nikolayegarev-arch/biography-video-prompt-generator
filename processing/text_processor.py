"""
Text processing utilities for chunking and timeline calculations.
"""
import re
import logging
from typing import List, Dict, Any
from exceptions import TextProcessingError

logger = logging.getLogger(__name__)


class TextProcessor:
    """Process biographical text for prompt generation."""
    
    def __init__(self, chunk_size: int = 1000):
        """
        Initialize text processor.
        
        Args:
            chunk_size: Number of words per chunk
        """
        self.chunk_size = chunk_size
    
    def count_words(self, text: str) -> int:
        """
        Count words in text.
        
        Args:
            text: Text to count
            
        Returns:
            Word count
        """
        return len(re.findall(r'\b\w+\b', text))
    
    def split_into_chunks(self, text: str) -> List[str]:
        """
        Split text into chunks of approximately chunk_size words.
        
        Args:
            text: Text to split
            
        Returns:
            List of text chunks
            
        Raises:
            TextProcessingError: If text processing fails
        """
        try:
            # Split text into words
            words = re.findall(r'\S+', text)
            
            if not words:
                raise TextProcessingError("No words found in text")
            
            chunks = []
            current_chunk = []
            current_count = 0
            
            for word in words:
                current_chunk.append(word)
                current_count += 1
                
                # Check if we've reached chunk size
                if current_count >= self.chunk_size:
                    chunks.append(' '.join(current_chunk))
                    current_chunk = []
                    current_count = 0
            
            # Add remaining words as final chunk
            if current_chunk:
                chunks.append(' '.join(current_chunk))
            
            logger.info(f"Split text into {len(chunks)} chunks (target: {self.chunk_size} words/chunk)")
            return chunks
        
        except Exception as e:
            raise TextProcessingError(f"Failed to split text into chunks: {e}")
    
    def calculate_timeline(
        self,
        word_count: int,
        narration_speed_wpm: int,
        frame_interval_seconds: float
    ) -> Dict[str, Any]:
        """
        Calculate timeline parameters.
        
        Args:
            word_count: Total word count
            narration_speed_wpm: Words per minute for narration
            frame_interval_seconds: Seconds per frame/prompt
            
        Returns:
            Timeline parameters dict
        """
        # Calculate total duration
        total_minutes = word_count / narration_speed_wpm
        total_seconds = total_minutes * 60
        
        # Calculate number of prompts needed
        total_prompts = int(total_seconds / frame_interval_seconds)
        
        # Ensure at least one prompt
        if total_prompts < 1:
            total_prompts = 1
        
        result = {
            "total_word_count": word_count,
            "narration_speed_wpm": narration_speed_wpm,
            "total_duration_seconds": total_seconds,
            "total_duration_minutes": total_minutes,
            "frame_interval_seconds": frame_interval_seconds,
            "total_prompts": total_prompts,
            "words_per_prompt": word_count / total_prompts if total_prompts > 0 else word_count
        }
        
        logger.info(
            f"Timeline: {word_count} words → {total_minutes:.1f} min → "
            f"{total_prompts} prompts @ {frame_interval_seconds}s intervals"
        )
        
        return result
    
    def split_into_scenes(
        self,
        text: str,
        total_prompts: int,
        words_per_prompt: float
    ) -> List[Dict[str, Any]]:
        """
        Split text into scenes for prompt generation.
        
        Args:
            text: Text to split
            total_prompts: Target number of prompts
            words_per_prompt: Average words per prompt
            
        Returns:
            List of scene dictionaries
        """
        try:
            words = re.findall(r'\S+', text)
            total_words = len(words)
            
            scenes = []
            words_per_scene = max(1, int(words_per_prompt))
            
            for i in range(total_prompts):
                start_idx = int(i * words_per_prompt)
                end_idx = min(int((i + 1) * words_per_prompt), total_words)
                
                if start_idx >= total_words:
                    break
                
                scene_words = words[start_idx:end_idx]
                scene_text = ' '.join(scene_words)
                
                scenes.append({
                    "index": i,
                    "start_word": start_idx,
                    "end_word": end_idx,
                    "text": scene_text,
                    "word_count": len(scene_words)
                })
            
            logger.debug(f"Split text into {len(scenes)} scenes")
            return scenes
        
        except Exception as e:
            raise TextProcessingError(f"Failed to split text into scenes: {e}")
    
    def extract_key_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract key entities from text (simple regex-based).
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary of entity types and lists
        """
        entities = {
            "people": [],
            "locations": [],
            "dates": [],
            "organizations": []
        }
        
        # Simple capitalized word detection for names/places
        # This is a basic implementation - could be enhanced with NER
        capitalized = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        
        # Date patterns
        dates = re.findall(
            r'\b(?:\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d{4}|(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4})\b',
            text,
            re.IGNORECASE
        )
        
        entities["people"] = list(set(capitalized))[:20]  # Limit to top 20
        entities["dates"] = list(set(dates))[:10]
        
        return entities
