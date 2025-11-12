#!/usr/bin/env python3
"""
Test script to verify the specific issue scenario is fixed.

User scenario:
- 12,530 words
- 150 WPM
- 6 seconds per frame
- Expected: 835 prompts
- Previously got: 193 prompts (77% loss)
- Now should get: ~835 prompts (with buffer system)
"""
import sys
import logging
from pathlib import Path

# Setup paths
sys.path.insert(0, str(Path(__file__).parent))

from config import Settings
from processing.story_processor import StoryProcessor
from processing.text_processor import TextProcessor

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_issue_scenario():
    """Test the exact scenario reported in the issue."""
    
    logger.info("=" * 70)
    logger.info("ISSUE SCENARIO TEST: Queen Victoria Biography")
    logger.info("=" * 70)
    
    # User's exact parameters
    word_count = 12530
    wpm = 150
    interval = 6.0
    
    logger.info(f"\nUser Input:")
    logger.info(f"  Word count: {word_count:,}")
    logger.info(f"  Narration speed: {wpm} WPM")
    logger.info(f"  Frame interval: {interval} seconds")
    
    # Calculate expected values
    processor = TextProcessor()
    timeline = processor.calculate_timeline(word_count, wpm, interval)
    
    logger.info(f"\nExpected Timeline:")
    logger.info(f"  Duration: {timeline['total_duration_minutes']:.2f} minutes")
    logger.info(f"  Duration: {timeline['total_duration_seconds']:.0f} seconds")
    logger.info(f"  Target prompts: {timeline['total_prompts']}")
    
    # Calculate with buffer
    settings = Settings(
        narration_speed_wpm=wpm,
        frame_interval_seconds=interval
    )
    story_processor = StoryProcessor(settings)
    buffer_factor = story_processor._calculate_buffer_factor()
    buffered_prompts = int(timeline['total_prompts'] * buffer_factor)
    
    logger.info(f"\nBuffer System:")
    logger.info(f"  Deduplication enabled: {settings.enable_deduplication}")
    logger.info(f"  Deduplication threshold: {settings.deduplication_threshold}")
    logger.info(f"  Quality filter enabled: {settings.enable_quality_filter}")
    logger.info(f"  Min quality score: {settings.min_quality_score}")
    logger.info(f"  Buffer factor: {buffer_factor:.2f}x")
    logger.info(f"  Prompts to generate: {buffered_prompts:,}")
    
    # Simulate worst-case post-processing losses
    logger.info(f"\nPost-Processing Simulation:")
    
    # Simulate deduplication removing 40%
    after_dedup = int(buffered_prompts * 0.6)
    logger.info(f"  After deduplication (40% removed): {after_dedup:,} prompts")
    
    # Simulate quality filter removing 30% of remaining
    after_quality = int(after_dedup * 0.7)
    logger.info(f"  After quality filter (30% removed): {after_quality:,} prompts")
    
    # Check if we're within acceptable range of target
    target = timeline['total_prompts']
    acceptable_min = int(target * 0.9)  # 90% of target
    acceptable_max = target
    
    logger.info(f"\nResult Analysis:")
    logger.info(f"  Target: {target} prompts")
    logger.info(f"  Acceptable range: {acceptable_min}-{acceptable_max}")
    logger.info(f"  Simulated final count: {after_quality} prompts")
    
    if acceptable_min <= after_quality <= acceptable_max:
        logger.info(f"  ✓ PASS: Within acceptable range!")
        result = "PASS"
    elif after_quality < acceptable_min:
        shortage = acceptable_min - after_quality
        logger.warning(f"  ⚠ MARGINAL: {shortage} prompts short of target")
        result = "MARGINAL"
    else:
        logger.info(f"  ✓ PASS: Exceeds minimum target")
        result = "PASS"
    
    # Compare with reported issue
    logger.info(f"\nComparison with Original Issue:")
    logger.info(f"  Original result: 193 prompts (23% of target)")
    logger.info(f"  New result (simulated): {after_quality} prompts ({after_quality*100//target}% of target)")
    improvement = after_quality - 193
    logger.info(f"  Improvement: +{improvement} prompts ({improvement*100//193}% increase)")
    
    logger.info("\n" + "=" * 70)
    logger.info(f"TEST RESULT: {result}")
    logger.info("=" * 70)
    
    return result == "PASS"


def test_alternative_scenarios():
    """Test with different filter settings."""
    
    logger.info("\n" + "=" * 70)
    logger.info("ALTERNATIVE SCENARIOS")
    logger.info("=" * 70)
    
    word_count = 12530
    wpm = 150
    interval = 6.0
    
    processor = TextProcessor()
    timeline = processor.calculate_timeline(word_count, wpm, interval)
    target = timeline['total_prompts']
    
    scenarios = [
        ("Dedup only", Settings(enable_quality_filter=False)),
        ("Quality filter only", Settings(enable_deduplication=False)),
        ("No filters", Settings(enable_deduplication=False, enable_quality_filter=False)),
        ("Strict dedup (0.9)", Settings(deduplication_threshold=0.9)),
        ("Loose dedup (0.8)", Settings(deduplication_threshold=0.8)),
        ("High quality (0.6)", Settings(min_quality_score=0.6)),
    ]
    
    for name, settings in scenarios:
        settings.narration_speed_wpm = wpm
        settings.frame_interval_seconds = interval
        
        story_processor = StoryProcessor(settings)
        buffer_factor = story_processor._calculate_buffer_factor()
        buffered_prompts = int(target * buffer_factor)
        
        logger.info(f"\n{name}:")
        logger.info(f"  Buffer factor: {buffer_factor:.2f}x")
        logger.info(f"  Generate: {buffered_prompts} prompts → Target: {target}")


if __name__ == "__main__":
    try:
        success = test_issue_scenario()
        test_alternative_scenarios()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        sys.exit(1)
