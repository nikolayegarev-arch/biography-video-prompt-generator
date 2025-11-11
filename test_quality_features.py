#!/usr/bin/env python3
"""
Tests for prompt quality and deduplication features.
"""
import sys
import logging
from pathlib import Path

# Setup paths
sys.path.insert(0, str(Path(__file__).parent))

from processing.similarity import SimilarityCalculator
from processing.prompt_quality import PromptQualityManager
from config import PromptStructure

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_similarity_calculator():
    """Test the similarity calculator."""
    logger.info("\n=== Testing Similarity Calculator ===")
    
    calc = SimilarityCalculator(threshold=0.85)
    
    # Test identical prompts
    prompt1 = "Medium shot of a Victorian woman reading a letter"
    prompt2 = "Medium shot of a Victorian woman reading a letter"
    similarity = calc.calculate_similarity(prompt1, prompt2)
    logger.info(f"Identical prompts similarity: {similarity:.2f}")
    assert similarity >= 0.95, "Identical prompts should have high similarity"
    
    # Test very similar prompts
    prompt3 = "Medium shot of Victorian woman reading letter"
    similarity = calc.calculate_similarity(prompt1, prompt3)
    logger.info(f"Very similar prompts similarity: {similarity:.2f}")
    assert similarity >= 0.80, "Very similar prompts should have high similarity"
    
    # Test different prompts
    prompt4 = "Wide aerial shot of a castle at sunset with dramatic clouds"
    similarity = calc.calculate_similarity(prompt1, prompt4)
    logger.info(f"Different prompts similarity: {similarity:.2f}")
    assert similarity < 0.5, "Different prompts should have low similarity"
    
    # Test duplicate detection
    prompts = [
        "Medium shot of woman reading",
        "Close-up of man writing",
        "Medium shot of woman reading a book",  # Similar to first
        "Wide shot of landscape",
        "Medium shot of woman reading"  # Very similar to first
    ]
    
    duplicates = calc.find_duplicates(prompts)
    logger.info(f"Found {len(duplicates)} duplicates: {duplicates}")
    assert len(duplicates) > 0, "Should find at least one duplicate"
    
    # Test deduplication
    unique_prompts = calc.deduplicate(prompts)
    logger.info(f"Deduplicated: {len(prompts)} -> {len(unique_prompts)} prompts")
    assert len(unique_prompts) < len(prompts), "Deduplication should reduce count"
    
    logger.info("✅ Similarity Calculator tests passed")
    return True


def test_prompt_quality_manager():
    """Test the prompt quality manager."""
    logger.info("\n=== Testing Prompt Quality Manager ===")
    
    qm = PromptQualityManager(enable_enhancement=True)
    
    # Test validation of good prompt
    good_prompt = (
        "Medium shot of a Victorian woman in elegant dress reading a letter "
        "by candlelight in a dimly lit study. Composition follows rule of thirds "
        "with warm golden lighting from the candle. Mood is contemplative and intimate. "
        "Rich mahogany furniture and books visible. Warm color palette with deep browns "
        "and golden tones. Historical illustration style, 8k, highly detailed, cinematic."
    )
    
    is_valid, issues = qm.validate_prompt(good_prompt)
    logger.info(f"Good prompt valid: {is_valid}, issues: {issues}")
    assert is_valid, "Good prompt should be valid"
    
    # Test validation of poor prompt
    poor_prompt = "woman reading"
    is_valid, issues = qm.validate_prompt(poor_prompt)
    logger.info(f"Poor prompt valid: {is_valid}, issues: {len(issues)} issues")
    assert not is_valid, "Poor prompt should be invalid"
    assert len(issues) > 0, "Poor prompt should have issues"
    
    # Test enhancement
    repetitive_prompt = "The man man walked walked to the the castle castle"
    enhanced = qm.enhance_prompt(repetitive_prompt)
    logger.info(f"Original: {repetitive_prompt}")
    logger.info(f"Enhanced: {enhanced}")
    assert enhanced != repetitive_prompt, "Enhancement should modify prompt"
    assert "man man" not in enhanced.lower(), "Enhancement should remove duplicates"
    
    # Test scoring
    scores = []
    test_prompts = [
        good_prompt,
        poor_prompt,
        "Close-up shot of determined character with intense lighting",
        "Wide landscape view"
    ]
    
    for prompt in test_prompts:
        score = qm.score_prompt(prompt)
        scores.append(score)
        logger.info(f"Score {score:.2f}: {prompt[:60]}...")
    
    assert scores[0] > scores[1], "Good prompt should score higher than poor"
    assert all(0.0 <= s <= 1.0 for s in scores), "Scores should be 0-1"
    
    # Test quality filtering
    high_quality, low_quality = qm.filter_low_quality(test_prompts, min_score=0.5)
    logger.info(f"Quality filter: {len(test_prompts)} -> {len(high_quality)} high, {len(low_quality)} low")
    assert len(high_quality) + len(low_quality) == len(test_prompts), "Should account for all prompts"
    
    # Test diversity analysis
    diversity = qm.analyze_prompt_diversity(test_prompts)
    logger.info(f"Diversity metrics: {diversity}")
    assert 'avg_length' in diversity, "Should have average length"
    assert 'vocabulary_size' in diversity, "Should have vocabulary size"
    assert 'avg_quality_score' in diversity, "Should have average quality score"
    
    logger.info("✅ Prompt Quality Manager tests passed")
    return True


def test_prompt_structure_validation():
    """Test PromptStructure validation."""
    logger.info("\n=== Testing PromptStructure Validation ===")
    
    qm = PromptQualityManager()
    
    # Test complete structure
    complete = PromptStructure(
        shot_type="Medium shot",
        subject="Victorian woman in elegant dress",
        action="reading a letter with focused expression",
        setting="dimly lit study with bookshelves",
        composition="rule of thirds, subject on right third",
        lighting="warm candlelight from left, soft shadows",
        mood="contemplative and intimate",
        key_details="leather-bound books, antique desk, quill pen",
        color_palette="warm browns, golden tones, deep shadows",
        style="historical illustration",
        technical="8k, highly detailed, cinematic",
        character_appearance="middle-aged, grey hair, serious demeanor"
    )
    
    is_valid, issues = qm.validate_prompt_structure(complete)
    logger.info(f"Complete structure valid: {is_valid}, issues: {issues}")
    assert is_valid, "Complete structure should be valid"
    
    # Test incomplete structure
    incomplete = PromptStructure(
        shot_type="Medium",
        subject="person",
        action="",  # Missing
        setting="",  # Missing
    )
    
    is_valid, issues = qm.validate_prompt_structure(incomplete)
    logger.info(f"Incomplete structure valid: {is_valid}, issues: {len(issues)} issues")
    assert not is_valid, "Incomplete structure should be invalid"
    
    # Test enhancement
    enhanced = qm.enhance_prompt_structure(complete)
    logger.info(f"Enhanced structure technical: {enhanced.technical}")
    assert enhanced.technical, "Enhanced should have technical specs"
    
    logger.info("✅ PromptStructure validation tests passed")
    return True


def test_integration():
    """Test integration of quality features."""
    logger.info("\n=== Testing Integration ===")
    
    calc = SimilarityCalculator(threshold=0.85)
    qm = PromptQualityManager(enable_enhancement=True)
    
    # Create test prompts with duplicates and varying quality
    prompts = [
        {
            'id': 'scene_0_0',
            'prompt': 'Medium shot of Queen Victoria in royal attire signing documents in palace office. Warm lighting, detailed historical style, 8k, cinematic.',
            'timestamp': 0.0
        },
        {
            'id': 'scene_0_1',
            'prompt': 'woman writing',  # Low quality
            'timestamp': 6.0
        },
        {
            'id': 'scene_0_2',
            'prompt': 'Medium shot of Queen Victoria in royal dress signing papers in palace room. Warm lighting, detailed historical, 8k.',  # Similar to first
            'timestamp': 12.0
        },
        {
            'id': 'scene_0_3',
            'prompt': 'Close-up of Queen Victoria determined expression as she reads a letter. Dramatic lighting from window, cinematic detail, historical style.',
            'timestamp': 18.0
        },
        {
            'id': 'scene_0_4',
            'prompt': 'Wide shot of palace exterior at golden hour with guards. Rich architectural detail, warm sunset colors, cinematic, 8k.',
            'timestamp': 24.0
        }
    ]
    
    logger.info(f"Starting with {len(prompts)} prompts")
    
    # Deduplication
    unique_prompts = calc.deduplicate_with_metadata(prompts, key='prompt')
    logger.info(f"After deduplication: {len(unique_prompts)} prompts")
    
    # Quality filtering
    prompt_texts = [p['prompt'] for p in unique_prompts]
    high_quality, low_quality = qm.filter_low_quality(prompt_texts, min_score=0.5)
    logger.info(f"After quality filter: {len(high_quality)} high quality, {len(low_quality)} low quality")
    
    # Keep only high quality
    final_prompts = [p for p in unique_prompts if p['prompt'] in high_quality]
    logger.info(f"Final count: {len(final_prompts)} prompts")
    
    # Calculate metrics
    final_texts = [p['prompt'] for p in final_prompts]
    diversity = qm.analyze_prompt_diversity(final_texts)
    logger.info(f"Final diversity metrics:")
    logger.info(f"  - Avg length: {diversity['avg_length']:.1f}")
    logger.info(f"  - Vocabulary: {diversity['vocabulary_size']}")
    logger.info(f"  - Avg quality: {diversity['avg_quality_score']:.2f}")
    
    assert len(final_prompts) < len(prompts), "Should have filtered some prompts"
    assert diversity['avg_quality_score'] > 0.5, "Final prompts should have good quality"
    
    logger.info("✅ Integration tests passed")
    return True


def run_all_tests():
    """Run all tests."""
    logger.info("=" * 80)
    logger.info("PROMPT QUALITY & DEDUPLICATION TEST SUITE")
    logger.info("=" * 80)
    
    tests = [
        ("Similarity Calculator", test_similarity_calculator),
        ("Prompt Quality Manager", test_prompt_quality_manager),
        ("PromptStructure Validation", test_prompt_structure_validation),
        ("Integration", test_integration)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            logger.error(f"Test '{name}' failed with error: {e}", exc_info=True)
            results.append((name, False))
    
    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("TEST SUMMARY")
    logger.info("=" * 80)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        logger.info(f"{status}: {name}")
    
    logger.info("=" * 80)
    logger.info(f"Result: {passed}/{total} tests passed")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
