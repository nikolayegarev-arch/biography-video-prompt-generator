# Prompt Quality & Deduplication Features

This document describes the prompt quality and deduplication features implemented in the Biography Video Prompt Generator.

## Overview

The quality system ensures that generated prompts are:
- **Unique**: No duplicate or highly similar prompts
- **High Quality**: Meet minimum standards for detail and completeness
- **Enhanced**: Automatically improved for better results
- **Contextually Diverse**: Avoid repetitive visual elements across scenes

## Features

### 1. Deduplication System

Automatically removes duplicate or highly similar prompts using advanced similarity matching.

**How it works:**
- Calculates similarity between prompts using both sequence matching (SequenceMatcher) and token-based similarity (Jaccard)
- Default threshold: 85% similarity = duplicate
- Prompts above threshold are removed automatically
- Keeps the first occurrence of similar prompts

**Configuration:**
```python
settings = Settings(
    enable_deduplication=True,        # Enable/disable deduplication
    deduplication_threshold=0.85      # Similarity threshold (0.0-1.0)
)
```

**Example:**
```
Original: "Medium shot of Queen Victoria signing documents in palace office"
Similar:  "Medium shot of Queen Victoria signing papers in palace room"
Result:   Only the first prompt is kept (similarity > 85%)
```

### 2. Quality Filtering

Filters out low-quality prompts based on comprehensive scoring.

**Quality Scoring Factors (0.0-1.0 scale):**
- **Length**: Minimum character count (50+ chars)
- **Visual Elements**: Presence of shot type, lighting, composition, mood, style keywords (30% weight)
- **Subject/Character**: Clear subject identification (10% weight)
- **Descriptive Detail**: Rich descriptive keywords like "detailed", "cinematic", "atmospheric" (20% weight)
- **Color/Lighting**: Color and lighting specifications (10% weight)
- **Variety**: Unique word ratio to detect repetition (10% weight)
- **Technical Quality**: Professional quality descriptors like "8k", "cinematic" (10% weight)

**Configuration:**
```python
settings = Settings(
    enable_quality_filter=True,       # Enable/disable quality filtering
    min_quality_score=0.5             # Minimum acceptable score (0.0-1.0)
)
```

**Example Scores:**
- High quality (0.9): "Medium shot of Victorian woman in elegant dress reading letter by candlelight. Warm golden lighting, rule of thirds composition, contemplative mood. Rich mahogany furniture, detailed historical style, 8k, cinematic."
- Low quality (0.2): "woman reading"

### 3. Automatic Enhancement

Improves prompts by fixing common issues and adding missing elements.

**Enhancements Applied:**
- Removes duplicate consecutive words
- Removes excessive whitespace
- Ensures proper capitalization
- Adds technical descriptors if missing ("highly detailed, cinematic")
- Fixes formatting issues

**Configuration:**
```python
settings = Settings(
    enable_enhancement=True           # Enable/disable auto-enhancement
)
```

**Example:**
```
Before: "The man man walked walked to the the castle castle"
After:  "The man walked to the castle, highly detailed, cinematic"
```

### 4. Context-Aware Generation

Prevents repetitive visual elements by providing context to the AI.

**How it works:**
- Tracks the last 3 generated prompts
- Passes them as context to the AI with instructions to vary shots and visual elements
- AI generates new prompts that differ from recent ones

**Example Context Note Sent to AI:**
```
IMPORTANT: Avoid repetition. Recent prompts for context 
(generate different shots, angles, and visual elements):
- Medium shot of Queen Victoria signing documents
- Close-up of determined expression
- Wide shot of palace exterior at sunset
```

## Quality Metrics

After processing, detailed quality metrics are included in the output:

```json
{
  "metadata": {
    "quality_metrics": {
      "avg_prompt_length": 145.3,      // Average characters per prompt
      "vocabulary_size": 1250,          // Unique words across all prompts
      "avg_quality_score": 0.78,        // Average quality score
      "min_quality_score": 0.52,        // Lowest scoring prompt
      "max_quality_score": 0.95         // Highest scoring prompt
    },
    "deduplication_enabled": true,
    "quality_filter_enabled": true
  }
}
```

## GUI Configuration

Quality settings are accessible in the GUI Options panel:

```
Options
  ☑ Dense Mode (detailed prompts)
  ☑ Character Consistency

Quality Settings:
  ☑ Enable Deduplication (remove similar prompts)
  ☑ Enable Quality Filter (remove low-quality prompts)
  ☑ Enable Enhancement (auto-improve prompts)
```

All three are enabled by default for best results.

## Processing Pipeline

The quality system integrates into the processing pipeline:

```
1. Text Chunking
2. AI Generation (with context awareness)
   ↓
3. Scene Creation
   ↓
4. POST-PROCESSING:
   4a. Deduplication (if enabled)
   4b. Quality Filtering (if enabled)
   4c. Enhancement (if enabled)
   4d. Timestamp Recalculation
   ↓
5. Quality Metrics Calculation
6. Output Generation
```

## API

### SimilarityCalculator

```python
from processing.similarity import SimilarityCalculator

calc = SimilarityCalculator(threshold=0.85)

# Calculate similarity
similarity = calc.calculate_similarity(text1, text2)  # Returns 0.0-1.0

# Check if duplicate
is_dup = calc.is_duplicate(text1, text2)  # Returns bool

# Deduplicate list
unique_prompts = calc.deduplicate(prompts)

# Deduplicate with metadata
unique_scenes = calc.deduplicate_with_metadata(scenes, key='prompt')
```

### PromptQualityManager

```python
from processing.prompt_quality import PromptQualityManager

qm = PromptQualityManager(enable_enhancement=True)

# Validate prompt
is_valid, issues = qm.validate_prompt(prompt)

# Score prompt
score = qm.score_prompt(prompt)  # Returns 0.0-1.0

# Enhance prompt
enhanced = qm.enhance_prompt(prompt)

# Filter by quality
high_quality, low_quality = qm.filter_low_quality(prompts, min_score=0.5)

# Analyze diversity
metrics = qm.analyze_prompt_diversity(prompts)
```

## Testing

Comprehensive test suite included:

```bash
python test_quality_features.py
```

Tests cover:
- Similarity calculation and deduplication
- Quality validation and scoring
- Prompt enhancement
- PromptStructure validation
- Integration testing

## Performance Impact

The quality features add minimal overhead:
- **Deduplication**: O(n²) comparison, but only on final prompts (typically <1000)
- **Quality Filtering**: O(n) scoring operation
- **Enhancement**: O(n) string operations
- **Total Overhead**: ~1-2% of total processing time

For a typical 12,000 word biography generating 800 prompts:
- Without quality features: ~100% time
- With quality features: ~101-102% time
- Benefits: 5-10% fewer prompts, significantly higher quality

## Best Practices

1. **Keep defaults enabled**: The default settings (all enabled, 85% threshold, 0.5 min score) work well for most cases

2. **Adjust threshold for creative variety**: Lower deduplication threshold (e.g., 0.75) for more variety, higher (e.g., 0.90) for more aggressive deduplication

3. **Adjust min_quality_score based on needs**:
   - 0.3: Very permissive, keeps almost everything
   - 0.5: Balanced (default)
   - 0.7: Strict, only high-quality prompts

4. **Monitor quality metrics**: Check the output metrics to understand your prompt quality distribution

5. **Use enhancement**: Always keep enhancement enabled for best results

## Troubleshooting

**Too many prompts filtered:**
- Lower `min_quality_score` (e.g., 0.4 instead of 0.5)
- Ensure `dense_mode=True` for more detailed prompts

**Not enough deduplication:**
- Lower `deduplication_threshold` (e.g., 0.75 instead of 0.85)
- Check that prompts are actually similar enough

**Prompts too similar:**
- Ensure context-aware generation is working (automatic)
- Increase variety in input text
- Enable `dense_mode` for more varied details

## Future Enhancements

Potential future improvements:
- Configurable threshold and min_score in GUI (currently code-only)
- More granular quality metrics (per-element scoring)
- Machine learning-based quality prediction
- Semantic similarity (requires ML models)
- Custom quality rules configuration

## License

Part of Biography Video Prompt Generator - open source project.
