# Changelog

All notable changes to the Biography Video Prompt Generator project.

## [1.0.0] - 2025-11-10

### Added - Initial Release

#### Core Application
- Complete modular Python application for biographical text analysis
- AI-powered image prompt generation for video production
- Support for texts of 12,000-15,000 words

#### AI Provider Integration
- **OpenRouter** support with 20 requests/minute rate limit
- **OpenAI** support with 50 requests/minute rate limit
- **Google Gemini** support with 15 requests/minute rate limit
- **Anthropic** support with 10 requests/minute rate limit
- Unified API manager for all providers (`api/api_manager.py`)
- Automatic provider-specific rate limiting
- Retry logic with exponential backoff (up to 5 attempts)
- HTTP 429 (rate limit) graceful handling

#### Text Processing
- Text chunking system (1000 words per chunk)
- Scene splitting (5-7 seconds per scene)
- Timeline calculation with timestamps
- Word count and duration estimation
- Character consistency tracking (optional)
- Key entity extraction

#### Scene Analysis
- **Shot Type Detection**: Wide shot, medium shot, close-up, tracking shot, aerial, etc.
- **Emotion Analysis**: Rage, joy, melancholy, anxiety, determination (with intensity levels)
- **Object Detection**: Documents, furniture, clothing, weapons, nature, architecture, etc.
- **Time of Day**: Dawn, morning, afternoon, golden hour, evening, night
- **Weather Conditions**: Clear, sunny, rainy, foggy, overcast, snowy, stormy

#### Prompt Structure (12 Elements)
1. Shot Type - Camera angle and framing
2. Subject - Characters with physical appearance
3. Action - Activities and micro-emotions
4. Setting - Location, architecture, time period
5. Composition - Visual arrangement (rule of thirds, etc.)
6. Lighting - Source, direction, quality, color
7. Mood - Atmosphere and emotional tone
8. Key Details - Objects, textures, effects
9. Color Palette - Specific colors and relationships
10. Style - Visual style (historical, photorealistic, etc.)
11. Technical - Quality descriptors (8k, cinematic, etc.)
12. Character Appearance - Consistent character descriptions

#### Output Formats
- **JSON**: Primary format with complete metadata
- **TXT**: Human-readable text format
- **CSV**: Spreadsheet-compatible format for analysis
- Partial save capability for resume functionality

#### GUI (CustomTkinter)
- Modern dark theme interface
- Folder selection with browse dialogs
- AI provider dropdown (4 providers)
- Model selection per provider
- Secure API key management with dialog
- Video settings configuration:
  - Frame interval slider (3-30 seconds, default 6)
  - Narration speed slider (100-200 wpm, default 150)
  - Visual style dropdown (14 styles)
- Processing options:
  - Dense mode toggle (detailed prompts)
  - Character consistency toggle
- Real-time progress bar and status updates
- Live processing logs with scrollable view
- Estimated images calculation
- Settings persistence between sessions

#### Error Handling & Resilience
- Atomic file writes using tempfile + rename
- Partial progress saves after each chunk
- Resume capability from last successful chunk
- Graceful API error degradation
- Detailed logging to file and console
- Safe interrupt handling

#### Utilities
- `utils/config_loader.py` - API key and configuration loading from .env or config.txt
- `utils/retry_handler.py` - Rate limiter and retry handler with exponential backoff
- `utils/file_ops.py` - Atomic file operations for JSON, TXT, CSV

#### Configuration
- `config.py` - Settings, APIConfig, and PromptStructure dataclasses
- `exceptions.py` - Custom exception hierarchy
- `.env.example` - Environment variables template
- `config.txt.example` - Alternative configuration file template
- `.gitignore` - Comprehensive ignore patterns

#### Documentation
- **README.md** - Complete bilingual documentation (English + Russian):
  - Project description and features
  - Installation instructions
  - API key setup for all providers
  - Usage guide (GUI and programmatic)
  - Output structure examples
  - Troubleshooting section
  - Project structure overview
- **test_functionality.py** - Demonstration script for core functionality

#### Project Structure
```
biography-video-prompt-generator/
├── api/                    # API integration
├── processing/             # Text and scene processing
├── utils/                  # Utility functions
├── gui/                    # CustomTkinter interface
├── texts_to_process/       # Input folder
├── video_prompts/          # Output folder
├── main.py                # Application entry point
├── config.py              # Configuration classes
├── exceptions.py          # Custom exceptions
├── requirements.txt       # Python dependencies
├── README.md             # Documentation
└── test_functionality.py # Test script
```

#### Dependencies
- requests>=2.31.0 - HTTP requests
- colorama>=0.4.6 - Colored terminal output
- customtkinter>=5.2.0 - Modern GUI framework
- anthropic>=0.25.0 - Anthropic API client
- tenacity>=8.2.3 - Retry logic
- pydantic>=2.5.0 - Data validation
- python-dotenv>=1.0.0 - Environment variables

### Testing
- ✅ All module imports verified
- ✅ Configuration system tested
- ✅ Text processing validated
- ✅ Scene analyzer verified
- ✅ File operations tested
- ✅ Rate limiting and retry logic validated
- ✅ All Python files compile without errors
- ✅ CodeQL security scan: 0 vulnerabilities found

### Security
- No vulnerabilities detected by CodeQL analysis
- Secure API key handling (not stored in code)
- Input validation on all user inputs
- Atomic file operations prevent data corruption
- Error messages don't expose sensitive information

### Known Limitations
- GUI requires tkinter (not available in headless environments)
- Actual AI generation requires valid API keys
- Processing time depends on text length and API response times
- CSV export has simplified metadata compared to JSON

### Future Enhancements (Potential)
- Sound notification on completion
- Auto-open results in default viewer
- Batch processing queue
- Custom visual style definitions
- Advanced character profile management
- Integration with video editing software
- Support for additional AI providers
- Multi-language support for prompts
