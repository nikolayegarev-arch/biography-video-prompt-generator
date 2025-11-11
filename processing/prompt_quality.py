"""
Prompt quality management for validation and enhancement.
"""
import re
import logging
from typing import Dict, List, Optional, Tuple
from config import PromptStructure

logger = logging.getLogger(__name__)


class PromptQualityManager:
    """Manage prompt quality through validation and enhancement."""
    
    # Minimum lengths for quality validation
    MIN_PROMPT_LENGTH = 50
    MIN_ELEMENT_LENGTH = 5
    
    # Required elements for a complete prompt
    REQUIRED_ELEMENTS = [
        'shot_type', 'subject', 'action', 'setting',
        'lighting', 'mood', 'style'
    ]
    
    # Optional but recommended elements
    OPTIONAL_ELEMENTS = [
        'composition', 'key_details', 'color_palette',
        'technical', 'character_appearance'
    ]
    
    def __init__(self, enable_enhancement: bool = True):
        """
        Initialize prompt quality manager.
        
        Args:
            enable_enhancement: Whether to automatically enhance prompts
        """
        self.enable_enhancement = enable_enhancement
    
    def validate_prompt(self, prompt: str) -> Tuple[bool, List[str]]:
        """
        Validate a prompt for quality.
        
        Args:
            prompt: Prompt text to validate
            
        Returns:
            Tuple of (is_valid, list of issues)
        """
        issues = []
        
        # Check minimum length
        if len(prompt) < self.MIN_PROMPT_LENGTH:
            issues.append(f"Prompt too short (minimum {self.MIN_PROMPT_LENGTH} characters)")
        
        # Check for empty or whitespace-only
        if not prompt.strip():
            issues.append("Prompt is empty or whitespace-only")
        
        # Check for basic structure indicators
        has_visual_elements = any(
            keyword in prompt.lower() 
            for keyword in ['shot', 'lighting', 'mood', 'composition', 'style']
        )
        
        if not has_visual_elements:
            issues.append("Prompt lacks visual element keywords")
        
        # Check for subject/character
        has_subject = any(
            keyword in prompt.lower()
            for keyword in ['man', 'woman', 'person', 'character', 'figure', 'people']
        )
        
        if not has_subject:
            issues.append("Prompt lacks clear subject or character")
        
        # Check for repetitive words (more than 3 times)
        words = prompt.lower().split()
        word_counts = {}
        for word in words:
            if len(word) > 4:  # Only check longer words
                word_counts[word] = word_counts.get(word, 0) + 1
        
        repetitive = [word for word, count in word_counts.items() if count > 3]
        if repetitive:
            issues.append(f"Repetitive words detected: {', '.join(repetitive[:3])}")
        
        is_valid = len(issues) == 0
        return is_valid, issues
    
    def validate_prompt_structure(self, prompt_structure: PromptStructure) -> Tuple[bool, List[str]]:
        """
        Validate a PromptStructure object.
        
        Args:
            prompt_structure: PromptStructure to validate
            
        Returns:
            Tuple of (is_valid, list of issues)
        """
        issues = []
        
        # Check required elements
        for element in self.REQUIRED_ELEMENTS:
            value = getattr(prompt_structure, element, '')
            if not value or len(value.strip()) < self.MIN_ELEMENT_LENGTH:
                issues.append(f"Required element '{element}' is missing or too short")
        
        # Validate full prompt
        full_prompt = prompt_structure.to_prompt()
        prompt_valid, prompt_issues = self.validate_prompt(full_prompt)
        
        if not prompt_valid:
            issues.extend(prompt_issues)
        
        is_valid = len(issues) == 0
        return is_valid, issues
    
    def enhance_prompt(self, prompt: str) -> str:
        """
        Enhance a prompt for better quality.
        
        Args:
            prompt: Original prompt text
            
        Returns:
            Enhanced prompt text
        """
        if not self.enable_enhancement:
            return prompt
        
        enhanced = prompt
        
        # Remove excessive whitespace
        enhanced = re.sub(r'\s+', ' ', enhanced).strip()
        
        # Remove duplicate consecutive words
        words = enhanced.split()
        cleaned_words = []
        prev_word = None
        for word in words:
            if word.lower() != prev_word:
                cleaned_words.append(word)
            prev_word = word.lower()
        enhanced = ' '.join(cleaned_words)
        
        # Ensure proper capitalization at start
        if enhanced:
            enhanced = enhanced[0].upper() + enhanced[1:]
        
        # Add technical descriptors if missing
        if 'cinematic' not in enhanced.lower() and 'detailed' not in enhanced.lower():
            enhanced += ", highly detailed, cinematic"
        
        return enhanced
    
    def enhance_prompt_structure(self, prompt_structure: PromptStructure) -> PromptStructure:
        """
        Enhance a PromptStructure object.
        
        Args:
            prompt_structure: PromptStructure to enhance
            
        Returns:
            Enhanced PromptStructure
        """
        if not self.enable_enhancement:
            return prompt_structure
        
        # Enhance text fields
        for element in self.REQUIRED_ELEMENTS + self.OPTIONAL_ELEMENTS:
            if hasattr(prompt_structure, element):
                value = getattr(prompt_structure, element, '')
                if value:
                    enhanced_value = self._enhance_element(value)
                    setattr(prompt_structure, element, enhanced_value)
        
        # Ensure technical descriptors
        if not prompt_structure.technical:
            prompt_structure.technical = "8k, highly detailed, cinematic"
        
        return prompt_structure
    
    def _enhance_element(self, text: str) -> str:
        """
        Enhance a single element text.
        
        Args:
            text: Element text
            
        Returns:
            Enhanced text
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove duplicate consecutive words
        words = text.split()
        cleaned_words = []
        prev_word = None
        for word in words:
            if word.lower() != prev_word:
                cleaned_words.append(word)
            prev_word = word.lower()
        
        return ' '.join(cleaned_words)
    
    def score_prompt(self, prompt: str) -> float:
        """
        Score a prompt for quality (0.0-1.0).
        
        Args:
            prompt: Prompt text
            
        Returns:
            Quality score
        """
        score = 0.0
        max_score = 10.0
        
        # Length score (1 point)
        if len(prompt) >= self.MIN_PROMPT_LENGTH:
            score += 1.0
        elif len(prompt) >= self.MIN_PROMPT_LENGTH // 2:
            score += 0.5
        
        # Visual elements score (3 points)
        visual_keywords = ['shot', 'lighting', 'composition', 'mood', 'atmosphere', 'style', 'camera']
        visual_count = sum(1 for kw in visual_keywords if kw in prompt.lower())
        score += min(3.0, visual_count * 0.5)
        
        # Subject/character score (1 point)
        subject_keywords = ['man', 'woman', 'person', 'character', 'figure', 'people', 'subject']
        has_subject = any(kw in prompt.lower() for kw in subject_keywords)
        if has_subject:
            score += 1.0
        
        # Descriptive detail score (2 points)
        descriptive_keywords = [
            'detailed', 'cinematic', 'professional', 'realistic', 'atmospheric',
            'dramatic', 'vivid', 'rich', 'intricate', 'refined'
        ]
        descriptive_count = sum(1 for kw in descriptive_keywords if kw in prompt.lower())
        score += min(2.0, descriptive_count * 0.5)
        
        # Color/lighting score (1 point)
        color_lighting_keywords = [
            'light', 'shadow', 'color', 'warm', 'cool', 'bright', 'dark',
            'golden', 'blue', 'red', 'green', 'illuminated'
        ]
        has_color_lighting = any(kw in prompt.lower() for kw in color_lighting_keywords)
        if has_color_lighting:
            score += 1.0
        
        # Variety score (1 point) - no excessive repetition
        words = prompt.lower().split()
        unique_ratio = len(set(words)) / len(words) if words else 0
        if unique_ratio >= 0.7:
            score += 1.0
        elif unique_ratio >= 0.5:
            score += 0.5
        
        # Technical quality score (1 point)
        technical_keywords = ['8k', '4k', 'hd', 'uhd', 'high quality', 'professional']
        has_technical = any(kw in prompt.lower() for kw in technical_keywords)
        if has_technical:
            score += 1.0
        
        # Normalize to 0-1 range
        return min(1.0, score / max_score)
    
    def filter_low_quality(
        self,
        prompts: List[str],
        min_score: float = 0.5
    ) -> Tuple[List[str], List[str]]:
        """
        Filter out low-quality prompts.
        
        Args:
            prompts: List of prompts
            min_score: Minimum quality score (0.0-1.0)
            
        Returns:
            Tuple of (high_quality_prompts, low_quality_prompts)
        """
        high_quality = []
        low_quality = []
        
        for prompt in prompts:
            score = self.score_prompt(prompt)
            if score >= min_score:
                high_quality.append(prompt)
            else:
                low_quality.append(prompt)
                logger.debug(f"Low quality prompt (score {score:.2f}): {prompt[:100]}...")
        
        if low_quality:
            logger.info(f"Filtered out {len(low_quality)} low-quality prompts")
        
        return high_quality, low_quality
    
    def analyze_prompt_diversity(self, prompts: List[str]) -> Dict[str, float]:
        """
        Analyze diversity metrics for a list of prompts.
        
        Args:
            prompts: List of prompts
            
        Returns:
            Dictionary of diversity metrics
        """
        if not prompts:
            return {
                'avg_length': 0,
                'avg_unique_words': 0,
                'vocabulary_size': 0,
                'avg_quality_score': 0
            }
        
        # Calculate metrics
        total_length = sum(len(p) for p in prompts)
        avg_length = total_length / len(prompts)
        
        all_words = []
        unique_word_counts = []
        
        for prompt in prompts:
            words = prompt.lower().split()
            all_words.extend(words)
            unique_word_counts.append(len(set(words)))
        
        avg_unique_words = sum(unique_word_counts) / len(unique_word_counts)
        vocabulary_size = len(set(all_words))
        
        # Calculate average quality score
        quality_scores = [self.score_prompt(p) for p in prompts]
        avg_quality_score = sum(quality_scores) / len(quality_scores)
        
        return {
            'avg_length': avg_length,
            'avg_unique_words': avg_unique_words,
            'vocabulary_size': vocabulary_size,
            'avg_quality_score': avg_quality_score
        }
