"""
Similarity calculation for prompt deduplication.
"""
import re
from typing import List, Set
from difflib import SequenceMatcher
import logging

logger = logging.getLogger(__name__)


class SimilarityCalculator:
    """Calculate similarity between prompts for deduplication."""
    
    def __init__(self, threshold: float = 0.85):
        """
        Initialize similarity calculator.
        
        Args:
            threshold: Similarity threshold (0.0-1.0) above which prompts are considered duplicates
        """
        if not 0.0 <= threshold <= 1.0:
            raise ValueError("Threshold must be between 0.0 and 1.0")
        self.threshold = threshold
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two text strings using multiple methods.
        
        Args:
            text1: First text string
            text2: Second text string
            
        Returns:
            Similarity score (0.0-1.0)
        """
        if not text1 or not text2:
            return 0.0
        
        # Normalize texts
        norm1 = self._normalize_text(text1)
        norm2 = self._normalize_text(text2)
        
        # Calculate different similarity metrics
        sequence_sim = self._sequence_similarity(norm1, norm2)
        token_sim = self._token_similarity(norm1, norm2)
        
        # Weighted combination (favor sequence similarity)
        combined_similarity = (sequence_sim * 0.6) + (token_sim * 0.4)
        
        return combined_similarity
    
    def _normalize_text(self, text: str) -> str:
        """
        Normalize text for comparison.
        
        Args:
            text: Text to normalize
            
        Returns:
            Normalized text
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove punctuation at boundaries
        text = text.strip(' .,;:!?')
        
        return text
    
    def _sequence_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate sequence-based similarity using SequenceMatcher.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0.0-1.0)
        """
        return SequenceMatcher(None, text1, text2).ratio()
    
    def _token_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate token-based similarity (Jaccard similarity).
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0.0-1.0)
        """
        # Split into tokens (words)
        tokens1 = set(text1.split())
        tokens2 = set(text2.split())
        
        if not tokens1 or not tokens2:
            return 0.0
        
        # Calculate Jaccard similarity: intersection / union
        intersection = len(tokens1 & tokens2)
        union = len(tokens1 | tokens2)
        
        return intersection / union if union > 0 else 0.0
    
    def is_duplicate(self, text1: str, text2: str) -> bool:
        """
        Check if two texts are duplicates based on similarity threshold.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            True if texts are duplicates
        """
        similarity = self.calculate_similarity(text1, text2)
        return similarity >= self.threshold
    
    def find_duplicates(self, prompts: List[str]) -> List[int]:
        """
        Find indices of duplicate prompts in a list.
        
        Args:
            prompts: List of prompt strings
            
        Returns:
            List of indices of prompts to remove (duplicates)
        """
        if not prompts:
            return []
        
        duplicates = set()
        
        for i in range(len(prompts)):
            if i in duplicates:
                continue
            
            for j in range(i + 1, len(prompts)):
                if j in duplicates:
                    continue
                
                if self.is_duplicate(prompts[i], prompts[j]):
                    duplicates.add(j)
                    logger.debug(
                        f"Found duplicate: prompt {j} is similar to prompt {i} "
                        f"(similarity: {self.calculate_similarity(prompts[i], prompts[j]):.2f})"
                    )
        
        return sorted(list(duplicates))
    
    def deduplicate(self, prompts: List[str]) -> List[str]:
        """
        Remove duplicate prompts from a list.
        
        Args:
            prompts: List of prompt strings
            
        Returns:
            List of unique prompts
        """
        duplicate_indices = self.find_duplicates(prompts)
        
        if duplicate_indices:
            logger.info(f"Removing {len(duplicate_indices)} duplicate prompts")
        
        # Return prompts that are not duplicates
        return [prompt for i, prompt in enumerate(prompts) if i not in duplicate_indices]
    
    def deduplicate_with_metadata(self, prompt_dicts: List[dict], key: str = 'prompt') -> List[dict]:
        """
        Remove duplicate prompts from a list of dictionaries.
        
        Args:
            prompt_dicts: List of dictionaries containing prompts
            key: Key name for the prompt text in each dictionary
            
        Returns:
            List of unique prompt dictionaries
        """
        if not prompt_dicts:
            return []
        
        # Extract prompts
        prompts = [pd.get(key, '') for pd in prompt_dicts]
        
        # Find duplicates
        duplicate_indices = self.find_duplicates(prompts)
        
        if duplicate_indices:
            logger.info(f"Removing {len(duplicate_indices)} duplicate prompts")
        
        # Return dictionaries that are not duplicates
        return [pd for i, pd in enumerate(prompt_dicts) if i not in duplicate_indices]
