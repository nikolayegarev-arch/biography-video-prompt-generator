#!/usr/bin/env python3
"""
Biography Video Prompt Generator - Main Entry Point

A modular Python application for analyzing biographical texts and generating
AI-powered image prompts for video production.
"""
import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from gui.main_window import main

if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('biography_generator.log')
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Starting Biography Video Prompt Generator")
    
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
