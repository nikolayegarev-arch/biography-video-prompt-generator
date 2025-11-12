#!/usr/bin/env python3
"""
Test script to verify buffer factor calculation for prompt generation.
"""
import sys
import logging
from pathlib import Path

# Setup paths
sys.path.insert(0, str(Path(__file__).parent))

from config import Settings, APIConfig
from processing.story_processor import StoryProcessor
from processing.text_processor import TextProcessor

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_buffer_calculation():
    """Test that buffer factor is calculated correctly."""
    
    logger.info("=" * 70)
    logger.info("BUFFER FACTOR CALCULATION TEST")
    logger.info("=" * 70)
    
    # Test scenario 1: Both dedup and quality filter enabled (default)
    logger.info("\nScenario 1: Default settings (dedup + quality filter)")
    settings1 = Settings()
    processor1 = StoryProcessor(settings1)
    buffer1 = processor1._calculate_buffer_factor()
    logger.info(f"  Deduplication: {settings1.enable_deduplication} (threshold: {settings1.deduplication_threshold})")
    logger.info(f"  Quality Filter: {settings1.enable_quality_filter} (min score: {settings1.min_quality_score})")
    logger.info(f"  Buffer Factor: {buffer1:.2f}x")
    
    # Test scenario 2: Only dedup enabled
    logger.info("\nScenario 2: Only deduplication enabled")
    settings2 = Settings(enable_quality_filter=False)
    processor2 = StoryProcessor(settings2)
    buffer2 = processor2._calculate_buffer_factor()
    logger.info(f"  Deduplication: {settings2.enable_deduplication} (threshold: {settings2.deduplication_threshold})")
    logger.info(f"  Quality Filter: {settings2.enable_quality_filter}")
    logger.info(f"  Buffer Factor: {buffer2:.2f}x")
    
    # Test scenario 3: Only quality filter enabled
    logger.info("\nScenario 3: Only quality filter enabled")
    settings3 = Settings(enable_deduplication=False)
    processor3 = StoryProcessor(settings3)
    buffer3 = processor3._calculate_buffer_factor()
    logger.info(f"  Deduplication: {settings3.enable_deduplication}")
    logger.info(f"  Quality Filter: {settings3.enable_quality_filter} (min score: {settings3.min_quality_score})")
    logger.info(f"  Buffer Factor: {buffer3:.2f}x")
    
    # Test scenario 4: Both disabled
    logger.info("\nScenario 4: No post-processing")
    settings4 = Settings(enable_deduplication=False, enable_quality_filter=False)
    processor4 = StoryProcessor(settings4)
    buffer4 = processor4._calculate_buffer_factor()
    logger.info(f"  Deduplication: {settings4.enable_deduplication}")
    logger.info(f"  Quality Filter: {settings4.enable_quality_filter}")
    logger.info(f"  Buffer Factor: {buffer4:.2f}x")
    
    logger.info("\n" + "=" * 70)
    logger.info("TIMELINE CALCULATION WITH BUFFER")
    logger.info("=" * 70)
    
    # User's scenario: 12,530 words, 150 WPM, 6s interval
    word_count = 12530
    wpm = 150
    interval = 6.0
    
    processor = TextProcessor()
    timeline = processor.calculate_timeline(word_count, wpm, interval)
    
    logger.info(f"\nInput: {word_count} words")
    logger.info(f"Narration Speed: {wpm} WPM")
    logger.info(f"Frame Interval: {interval}s")
    logger.info(f"Duration: {timeline['total_duration_minutes']:.2f} minutes ({timeline['total_duration_seconds']:.0f} seconds)")
    logger.info(f"Target Prompts: {timeline['total_prompts']}")
    
    # Calculate with buffer
    settings = Settings()
    processor_with_buffer = StoryProcessor(settings)
    buffer_factor = processor_with_buffer._calculate_buffer_factor()
    buffered_prompts = int(timeline['total_prompts'] * buffer_factor)
    
    logger.info(f"\nWith Buffer Factor {buffer_factor:.2f}x:")
    logger.info(f"  Generate: {buffered_prompts} prompts")
    logger.info(f"  After post-processing (estimated): ~{timeline['total_prompts']} prompts")
    logger.info(f"  Expected range: {int(timeline['total_prompts'] * 0.95)}-{timeline['total_prompts']} prompts")
    
    logger.info("\n" + "=" * 70)
    logger.info("TEST COMPLETE")
    logger.info("=" * 70)
    
    return True


if __name__ == "__main__":
    try:
        success = test_buffer_calculation()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        sys.exit(1)
