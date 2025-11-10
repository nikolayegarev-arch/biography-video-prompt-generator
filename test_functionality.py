#!/usr/bin/env python3
"""
Test script to demonstrate Biography Video Prompt Generator functionality.
This script processes a text file without using the GUI.
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


def test_processing_without_api():
    """Test the processing pipeline without making actual API calls."""
    
    logger.info("Starting test (no actual API calls)...")
    
    # Read test file
    input_file = Path("texts_to_process/test_biography.txt")
    
    if not input_file.exists():
        logger.error(f"Test file not found: {input_file}")
        return False
    
    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Initialize text processor
    processor = TextProcessor(chunk_size=1000)
    word_count = processor.count_words(text)
    
    logger.info(f"Input text: {word_count} words")
    
    # Calculate timeline
    timeline = processor.calculate_timeline(
        word_count=word_count,
        narration_speed_wpm=150,
        frame_interval_seconds=6.0
    )
    
    logger.info(f"Timeline: {timeline['total_prompts']} prompts needed")
    logger.info(f"Duration: {timeline['total_duration_minutes']:.1f} minutes")
    
    # Split into chunks
    chunks = processor.split_into_chunks(text)
    logger.info(f"Split into {len(chunks)} chunks")
    
    # Analyze first chunk
    from processing.scene_analyzer import SceneAnalyzer
    analyzer = SceneAnalyzer()
    
    first_chunk = chunks[0][:500]  # First 500 chars
    analysis = analyzer.analyze_scene(first_chunk)
    
    logger.info("\nScene analysis of first chunk:")
    logger.info(f"  Shot type: {analysis['shot_type']}")
    logger.info(f"  Emotions: {analysis['emotions']}")
    logger.info(f"  Objects: {analysis['objects']}")
    logger.info(f"  Time: {analysis['time_of_day']}")
    logger.info(f"  Weather: {analysis['weather']}")
    
    # Test prompt template generation
    from processing.prompt_templates import PromptTemplates
    
    system_prompt = PromptTemplates.get_system_prompt(
        visual_style="historical illustration",
        dense_mode=False
    )
    
    logger.info(f"\nSystem prompt generated ({len(system_prompt)} characters)")
    
    user_prompt = PromptTemplates.get_chunk_analysis_prompt(
        chunk_text=first_chunk,
        chunk_index=0,
        total_chunks=len(chunks),
        prompts_needed=5,
        visual_style="historical illustration"
    )
    
    logger.info(f"User prompt generated ({len(user_prompt)} characters)")
    
    logger.info("\n✅ All processing steps completed successfully!")
    logger.info("Note: To generate actual prompts, configure API keys and run with main.py")
    
    return True


def show_usage_instructions():
    """Show instructions for using the application."""
    
    print("\n" + "=" * 80)
    print("BIOGRAPHY VIDEO PROMPT GENERATOR - Usage Instructions")
    print("=" * 80)
    print()
    print("To use this application with real AI generation:")
    print()
    print("1. Configure API Keys:")
    print("   - Copy .env.example to .env")
    print("   - Add your API key for at least one provider:")
    print("     * OpenRouter: https://openrouter.ai/keys")
    print("     * OpenAI: https://platform.openai.com/api-keys")
    print("     * Gemini: https://makersuite.google.com/app/apikey")
    print("     * Anthropic: https://console.anthropic.com/")
    print()
    print("2. Run the GUI application:")
    print("   python main.py")
    print()
    print("3. Or use programmatically:")
    print("""
from config import Settings, APIConfig
from processing.story_processor import StoryProcessor

# Configure
api_config = APIConfig(
    provider='openrouter',
    api_key='your-key-here',
    model='anthropic/claude-3.5-sonnet'
)
settings = Settings(
    frame_interval_seconds=6.0,
    narration_speed_wpm=150,
    visual_style='historical illustration',
    api_config=api_config
)

# Process
processor = StoryProcessor(settings)
result = processor.process_file(
    input_path=Path('texts_to_process/your_file.txt'),
    output_path=Path('video_prompts/your_file.video_prompts.json')
)
    """)
    print()
    print("=" * 80)
    print()


if __name__ == "__main__":
    print("\n🎬 Biography Video Prompt Generator - Test Suite\n")
    
    success = test_processing_without_api()
    
    if success:
        show_usage_instructions()
        sys.exit(0)
    else:
        logger.error("Test failed!")
        sys.exit(1)
