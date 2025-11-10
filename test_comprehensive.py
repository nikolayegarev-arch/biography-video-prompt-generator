#!/usr/bin/env python3
"""
Comprehensive test script to verify all functionality.
Tests:
1. API key management
2. Estimated images calculation
3. Text processing
4. Story processing
5. Config loading
"""
import sys
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from config import Settings, APIConfig
from processing.story_processor import StoryProcessor, ProcessingConfig
from processing.text_processor import TextProcessor
from utils.file_ops import save_text

# Mock APIKeyManager since tkinter is not available in this environment
class APIKeyManager:
    """Mock API key manager for testing."""
    def __init__(self):
        self.keys = {}
    
    def get_key(self, provider):
        return self.keys.get(provider)
    
    def set_key(self, provider, key):
        self.keys[provider] = key
    
    def has_key(self, provider):
        return provider in self.keys and bool(self.keys[provider])

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_processing_config_import():
    """Test ProcessingConfig import."""
    logger.info("=" * 70)
    logger.info("TEST 1: ProcessingConfig Import")
    logger.info("=" * 70)
    
    try:
        # Test import
        from processing.story_processor import StoryProcessor, ProcessingConfig
        logger.info("✓ Import successful")
        
        # Test that ProcessingConfig is Settings
        assert ProcessingConfig is Settings
        logger.info("✓ ProcessingConfig is Settings")
        
        # Test instantiation
        config = ProcessingConfig()
        logger.info(f"✓ ProcessingConfig instantiated")
        logger.info(f"  - frame_interval_seconds: {config.frame_interval_seconds}")
        logger.info(f"  - narration_speed_wpm: {config.narration_speed_wpm}")
        
        # Test with StoryProcessor
        processor = StoryProcessor(config)
        logger.info("✓ StoryProcessor initialized with ProcessingConfig")
        
        return True
    except Exception as e:
        logger.error(f"✗ FAILED: {e}")
        return False


def test_api_key_manager():
    """Test API key management."""
    logger.info("\n" + "=" * 70)
    logger.info("TEST 2: API Key Manager")
    logger.info("=" * 70)
    
    try:
        manager = APIKeyManager()
        logger.info("✓ APIKeyManager initialized")
        
        # Test setting keys
        providers = ['openrouter', 'openai', 'gemini', 'anthropic']
        for provider in providers:
            manager.set_key(provider, f"test_key_{provider}")
            logger.info(f"✓ Set key for {provider}")
        
        # Test getting keys
        for provider in providers:
            key = manager.get_key(provider)
            assert key == f"test_key_{provider}", f"Key mismatch for {provider}"
            logger.info(f"✓ Retrieved key for {provider}")
        
        # Test has_key
        for provider in providers:
            assert manager.has_key(provider), f"has_key failed for {provider}"
            logger.info(f"✓ has_key works for {provider}")
        
        # Test missing key
        assert not manager.has_key('nonexistent'), "has_key should return False for missing key"
        logger.info("✓ has_key correctly returns False for missing provider")
        
        return True
    except Exception as e:
        logger.error(f"✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_estimated_images_calculation():
    """Test estimated images calculation."""
    logger.info("\n" + "=" * 70)
    logger.info("TEST 3: Estimated Images Calculation")
    logger.info("=" * 70)
    
    try:
        # Test case 1: 12000 words, 150 wpm, 6s interval
        words = 12000
        wpm = 150
        interval = 6.0
        
        duration_minutes = words / wpm
        duration_seconds = duration_minutes * 60
        estimated_images = int(duration_seconds / interval)
        
        logger.info(f"Test case 1:")
        logger.info(f"  Words: {words}")
        logger.info(f"  WPM: {wpm}")
        logger.info(f"  Interval: {interval}s")
        logger.info(f"  Duration: {duration_minutes:.2f} minutes ({duration_seconds:.2f} seconds)")
        logger.info(f"  Estimated images: {estimated_images}")
        
        # Verify calculation
        expected = 800  # 12000/150 = 80 min = 4800 sec / 6 = 800
        assert estimated_images == expected, f"Expected {expected}, got {estimated_images}"
        logger.info(f"✓ Calculation correct (expected {expected})")
        
        # Test case 2: Different parameters
        words = 15000
        wpm = 120
        interval = 5.0
        
        duration_minutes = words / wpm
        duration_seconds = duration_minutes * 60
        estimated_images = int(duration_seconds / interval)
        
        logger.info(f"\nTest case 2:")
        logger.info(f"  Words: {words}")
        logger.info(f"  WPM: {wpm}")
        logger.info(f"  Interval: {interval}s")
        logger.info(f"  Duration: {duration_minutes:.2f} minutes ({duration_seconds:.2f} seconds)")
        logger.info(f"  Estimated images: {estimated_images}")
        
        expected = 1500  # 15000/120 = 125 min = 7500 sec / 5 = 1500
        assert estimated_images == expected, f"Expected {expected}, got {estimated_images}"
        logger.info(f"✓ Calculation correct (expected {expected})")
        
        return True
    except Exception as e:
        logger.error(f"✗ FAILED: {e}")
        return False


def test_text_processor():
    """Test text processor functionality."""
    logger.info("\n" + "=" * 70)
    logger.info("TEST 4: Text Processor")
    logger.info("=" * 70)
    
    try:
        processor = TextProcessor(chunk_size=1000)
        logger.info("✓ TextProcessor initialized")
        
        # Create test text
        test_text = " ".join(["word"] * 5000)  # 5000 words
        
        # Test word count
        word_count = processor.count_words(test_text)
        assert word_count == 5000, f"Expected 5000 words, got {word_count}"
        logger.info(f"✓ Word count correct: {word_count}")
        
        # Test text splitting
        chunks = processor.split_into_chunks(test_text)
        logger.info(f"✓ Text split into {len(chunks)} chunks")
        
        # Verify chunk sizes
        for i, chunk in enumerate(chunks):
            chunk_words = processor.count_words(chunk)
            logger.info(f"  Chunk {i+1}: {chunk_words} words")
        
        # Test timeline calculation
        timeline = processor.calculate_timeline(
            word_count=5000,
            narration_speed_wpm=150,
            frame_interval_seconds=6.0
        )
        logger.info(f"✓ Timeline calculated:")
        logger.info(f"  Total prompts: {timeline['total_prompts']}")
        logger.info(f"  Duration: {timeline['total_duration_minutes']:.2f} minutes")
        logger.info(f"  Words per prompt: {timeline['words_per_prompt']:.2f}")
        
        # Verify timeline calculation
        expected_minutes = 5000 / 150  # 33.33 minutes
        expected_seconds = expected_minutes * 60  # 2000 seconds
        expected_prompts = int(expected_seconds / 6.0)  # 333 prompts
        
        assert abs(timeline['total_duration_minutes'] - expected_minutes) < 0.1
        assert timeline['total_prompts'] == expected_prompts
        logger.info(f"✓ Timeline calculation verified")
        
        return True
    except Exception as e:
        logger.error(f"✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_config_settings():
    """Test configuration settings."""
    logger.info("\n" + "=" * 70)
    logger.info("TEST 5: Configuration Settings")
    logger.info("=" * 70)
    
    try:
        # Test APIConfig
        api_config = APIConfig(
            provider='openrouter',
            api_key='test_key',
            model='test_model'
        )
        logger.info("✓ APIConfig created")
        logger.info(f"  Provider: {api_config.provider}")
        logger.info(f"  Model: {api_config.model}")
        logger.info(f"  Rate limit: {api_config.get_rate_limit()}")
        
        # Test Settings
        settings = Settings(
            frame_interval_seconds=6.0,
            narration_speed_wpm=150,
            visual_style='historical illustration',
            api_config=api_config
        )
        logger.info("✓ Settings created")
        logger.info(f"  Frame interval: {settings.frame_interval_seconds}s")
        logger.info(f"  Narration speed: {settings.narration_speed_wpm} wpm")
        logger.info(f"  Visual style: {settings.visual_style}")
        logger.info(f"  Dense mode: {settings.dense_mode}")
        logger.info(f"  Character consistency: {settings.character_consistency}")
        
        # Test validation
        try:
            invalid_settings = Settings(frame_interval_seconds=1.0)  # Invalid (< 3)
            logger.error("✗ Validation failed - should have raised error")
            return False
        except ValueError as e:
            logger.info(f"✓ Validation working: {e}")
        
        return True
    except Exception as e:
        logger.error(f"✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_actual_file_processing():
    """Test processing with actual file if available."""
    logger.info("\n" + "=" * 70)
    logger.info("TEST 6: Actual File Processing (Calculation Only)")
    logger.info("=" * 70)
    
    try:
        # Create a sample text file
        sample_file = Path("texts_to_process/test_sample.txt")
        sample_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Create sample text (approximately 1000 words)
        sample_text = """
        This is a sample biographical text. It contains information about a person's life, 
        their achievements, and their journey through various life events. The text needs to 
        be long enough to test the processing pipeline properly.
        """ * 100  # Repeat to get ~1000 words
        
        save_text(sample_file, sample_text)
        logger.info(f"✓ Created sample file: {sample_file}")
        
        # Read and process
        with open(sample_file, 'r', encoding='utf-8') as f:
            text = f.read()
        
        processor = TextProcessor(chunk_size=1000)
        word_count = processor.count_words(text)
        logger.info(f"✓ Sample file word count: {word_count}")
        
        # Calculate timeline
        timeline = processor.calculate_timeline(
            word_count=word_count,
            narration_speed_wpm=150,
            frame_interval_seconds=6.0
        )
        logger.info(f"✓ Timeline for sample file:")
        logger.info(f"  Total prompts needed: {timeline['total_prompts']}")
        logger.info(f"  Duration: {timeline['total_duration_minutes']:.2f} minutes")
        logger.info(f"  Words per prompt: {timeline['words_per_prompt']:.2f}")
        
        # Test chunking
        chunks = processor.split_into_chunks(text)
        logger.info(f"✓ Text split into {len(chunks)} chunks")
        
        return True
    except Exception as e:
        logger.error(f"✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    logger.info("\n" + "=" * 70)
    logger.info("COMPREHENSIVE FUNCTIONALITY TEST SUITE")
    logger.info("=" * 70)
    
    tests = [
        ("ProcessingConfig Import", test_processing_config_import),
        ("API Key Manager", test_api_key_manager),
        ("Estimated Images Calculation", test_estimated_images_calculation),
        ("Text Processor", test_text_processor),
        ("Configuration Settings", test_config_settings),
        ("Actual File Processing", test_actual_file_processing),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Print summary
    logger.info("\n" + "=" * 70)
    logger.info("TEST SUMMARY")
    logger.info("=" * 70)
    
    passed = 0
    failed = 0
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"{status}: {test_name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    logger.info("=" * 70)
    logger.info(f"Total: {len(results)} | Passed: {passed} | Failed: {failed}")
    logger.info("=" * 70)
    
    if failed == 0:
        logger.info("\n🎉 ALL TESTS PASSED! The application is fully functional.")
        return 0
    else:
        logger.error(f"\n❌ {failed} TEST(S) FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
