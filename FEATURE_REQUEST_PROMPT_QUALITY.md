# Feature Request: Improve Prompt Quality and Reduce Duplicates

## Overview
Enhance the quality of generated image prompts and eliminate duplicate prompts that occur when chunks generate similar content.

## Current Issues

### 1. Duplicate Prompts
**Problem**: When processing biographical text, chunks sometimes generate identical or very similar prompts, resulting in duplicate scenes.

**Example**:
```
Prompt 1: "Medium shot of Queen Victoria sitting in ornate chair, Victorian era interior"
Prompt 15: "Medium shot of Queen Victoria sitting in ornate chair, Victorian interior"
Prompt 87: "Queen Victoria seated in ornate chair, Victorian setting"
```

**Root Cause**: 
- Each chunk is processed independently
- AI doesn't have context of previously generated prompts
- Similar narrative passages lead to similar visual descriptions

### 2. Insufficient Detail for Image Generation
**Problem**: Prompts lack specific details needed for high-quality image generation.

**Current Prompt Example**:
```
"Queen Victoria in her study"
```

**Desired Prompt Example**:
```
"Medium shot of Queen Victoria, aged 45, wearing black mourning dress with white lace collar and gold brooch, seated at mahogany writing desk in Buckingham Palace study, soft natural light from tall windows illuminating ornate Victorian decor, warm sepia tones, dignified and contemplative mood, historical illustration style, 8k, highly detailed"
```

## Proposed Solutions

### Solution 1: Deduplication System

#### Implementation Approach

**File**: `processing/story_processor.py`

Add deduplication after all scenes are generated:

```python
from difflib import SequenceMatcher

def _deduplicate_scenes(self, scenes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Remove duplicate or very similar prompts.
    
    Args:
        scenes: List of scene dictionaries
        
    Returns:
        Deduplicated list of scenes
    """
    if not scenes:
        return scenes
    
    unique_scenes = []
    seen_prompts = []
    
    for scene in scenes:
        prompt = scene["prompt"].lower().strip()
        
        # Check similarity against all seen prompts
        is_duplicate = False
        for seen_prompt in seen_prompts:
            similarity = SequenceMatcher(None, prompt, seen_prompt).ratio()
            
            # If >85% similar, consider it a duplicate
            if similarity > 0.85:
                logger.info(f"Skipping duplicate prompt (similarity: {similarity:.2%})")
                is_duplicate = True
                break
        
        if not is_duplicate:
            unique_scenes.append(scene)
            seen_prompts.append(prompt)
    
    logger.info(f"Deduplication: {len(scenes)} → {len(unique_scenes)} scenes "
                f"({len(scenes) - len(unique_scenes)} duplicates removed)")
    
    return unique_scenes
```

Add call after chunk processing (line ~145):
```python
# Before finalizing metadata
all_scenes = self._deduplicate_scenes(all_scenes)

# Finalize metadata
metadata["total_prompts"] = len(all_scenes)
metadata["metadata"]["total_prompts"] = len(all_scenes)
metadata["scenes"] = all_scenes
```

#### Configuration Option

Add to `config.py`:
```python
@dataclass
class Settings:
    # ... existing fields ...
    
    # Deduplication settings
    enable_deduplication: bool = True
    similarity_threshold: float = 0.85  # 0.0-1.0, higher = more strict
```

Add checkbox to GUI:
```python
self.deduplication_var = ctk.BooleanVar(value=True)
ctk.CTkCheckBox(
    options_frame,
    text="Remove Duplicate Prompts",
    variable=self.deduplication_var
).pack(anchor="w", padx=20, pady=(5, 5))
```

### Solution 2: Enhanced Prompt Template

#### Current Prompt Structure (Basic)
```
Subject: [character/scene]
Action: [what's happening]
Setting: [location]
```

#### Proposed 12-Element Structure

**File**: `processing/prompt_templates.py`

Update system prompt to enforce detailed structure:

```python
@staticmethod
def get_system_prompt(visual_style: str, dense_mode: bool) -> str:
    """Generate system prompt with enhanced structure requirements."""
    
    base_prompt = """You are an expert at creating detailed image generation prompts for biographical video production.

CRITICAL REQUIREMENTS:
1. Each prompt must follow the 12-element structure exactly
2. Provide specific, visual details (colors, textures, lighting, mood)
3. Include subject's age/appearance when relevant
4. Specify camera angle and shot type
5. Describe setting in detail (architecture, decor, time period)
6. Add atmospheric elements (lighting, weather, mood)
7. Keep prompts distinct - avoid repeating descriptions

12-ELEMENT PROMPT STRUCTURE:
1. SHOT TYPE: (wide shot/medium shot/close-up/tracking shot/aerial view)
2. SUBJECT: (character name, age, physical appearance, clothing details)
3. ACTION: (specific action, gesture, facial expression, micro-emotions)
4. SETTING: (specific location, architecture style, time period indicators)
5. COMPOSITION: (rule of thirds, symmetry, leading lines, depth)
6. LIGHTING: (light source, direction, quality - soft/hard, color temperature)
7. MOOD: (emotional atmosphere, tone, feeling)
8. KEY DETAILS: (important objects, textures, materials, props)
9. COLOR PALETTE: (specific colors, color relationships, saturation)
10. STYLE: (artistic style - {visual_style})
11. TECHNICAL: (image quality indicators)
12. CHARACTER APPEARANCE: (consistent physical description)

EXAMPLE OUTPUT FORMAT:
"Medium shot of Queen Victoria, aged 45, black mourning dress with white lace collar, gold mourning brooch, writing at ornate mahogany desk, Buckingham Palace private study, composition following rule of thirds with subject slightly right, soft natural window light from left creating gentle shadows, somber yet dignified mood, details include leather-bound journals, ivory letter opener, crystal inkwell, warm sepia and gold tones with deep blacks, historical illustration style, 8k highly detailed cinematic, character: pale complexion, dark hair in center part, small frame"
"""
    
    if dense_mode:
        base_prompt += "\n\nDENSE MODE: Maximize detail in every element. Include textures, materials, specific colors, lighting quality, and atmospheric effects."
    
    return base_prompt
```

#### Update Chunk Analysis Prompt

```python
@staticmethod
def get_chunk_analysis_prompt(
    chunk_text: str,
    chunk_idx: int,
    total_chunks: int,
    prompts_needed: int,
    visual_style: str,
    previous_prompts: List[str] = None
) -> str:
    """Generate prompt with context of previous prompts to avoid duplication."""
    
    prompt = f"""Analyze this biographical text excerpt and generate {prompts_needed} distinct, highly detailed image prompts.

TEXT EXCERPT (Chunk {chunk_idx + 1}/{total_chunks}):
{chunk_text}

REQUIREMENTS:
1. Generate exactly {prompts_needed} unique prompts
2. Follow the 12-element structure for each prompt
3. Make each prompt visually distinct with different:
   - Camera angles/shot types
   - Character poses/actions
   - Settings/locations
   - Lighting conditions
   - Moods/atmospheres
4. Include specific visual details (colors, textures, lighting, props)
5. Progress through the narrative chronologically
6. Visual style: {visual_style}

"""
    
    # Add context from previous prompts to avoid duplication
    if previous_prompts and len(previous_prompts) > 0:
        recent = previous_prompts[-3:]  # Last 3 prompts
        prompt += f"""
AVOID REPEATING THESE RECENT SCENES:
{chr(10).join([f"- {p}" for p in recent])}

Create NEW and DIFFERENT scenes from the current text excerpt.
"""
    
    prompt += """
OUTPUT FORMAT:
One prompt per line, no numbering, no commentary.
Each prompt must be complete and follow all 12 elements.
"""
    
    return prompt
```

#### Update _process_chunk to Pass Context

**File**: `processing/story_processor.py`

```python
def _process_chunk(
    self,
    api_manager: APIManager,
    chunk_text: str,
    chunk_idx: int,
    total_chunks: int,
    prompts_needed: int,
    scene_offset: int,
    all_scenes: List[Dict[str, Any]] = None  # Add context
) -> List[Dict[str, Any]]:
    """Process a single text chunk with context."""
    
    system_prompt = PromptTemplates.get_system_prompt(
        self.settings.visual_style,
        self.settings.dense_mode
    )
    
    # Get previous prompts for context
    previous_prompts = []
    if all_scenes:
        previous_prompts = [s["prompt"] for s in all_scenes[-5:]]  # Last 5 prompts
    
    user_prompt = PromptTemplates.get_chunk_analysis_prompt(
        chunk_text,
        chunk_idx,
        total_chunks,
        prompts_needed,
        self.settings.visual_style,
        previous_prompts  # Pass context
    )
    
    # ... rest of method
```

Update the caller:
```python
# In process_file method
chunk_scenes = self._process_chunk(
    api_manager,
    chunk_text,
    chunk_idx,
    total_chunks,
    prompts_per_chunk,
    len(all_scenes),
    all_scenes  # Pass context
)
```

### Solution 3: Post-Processing Enhancement

**File**: `processing/prompt_enhancer.py` (new file)

```python
"""
Enhance prompts with additional detail if they're too short.
"""
import re
from typing import List, Dict, Any

class PromptEnhancer:
    """Enhance and validate prompts for image generation."""
    
    REQUIRED_ELEMENTS = [
        "shot_type", "subject", "action", "setting", 
        "lighting", "mood", "style"
    ]
    
    MIN_PROMPT_LENGTH = 100  # characters
    
    @staticmethod
    def enhance_if_needed(prompt: str, visual_style: str) -> str:
        """Enhance prompt if it lacks detail."""
        
        # If prompt is already detailed, return as-is
        if len(prompt) >= PromptEnhancer.MIN_PROMPT_LENGTH:
            return prompt
        
        # Add default enhancements
        enhancements = []
        
        # Add style if missing
        if visual_style.lower() not in prompt.lower():
            enhancements.append(f"{visual_style} style")
        
        # Add quality indicators if missing
        if "8k" not in prompt.lower() and "detailed" not in prompt.lower():
            enhancements.append("8k highly detailed")
        
        # Add cinematic if missing
        if "cinematic" not in prompt.lower():
            enhancements.append("cinematic composition")
        
        if enhancements:
            prompt = f"{prompt}, {', '.join(enhancements)}"
        
        return prompt
    
    @staticmethod
    def validate_prompt(prompt: str) -> tuple[bool, str]:
        """
        Validate prompt has sufficient detail.
        
        Returns:
            (is_valid, reason)
        """
        if len(prompt) < 50:
            return False, "Prompt too short"
        
        if not any(word in prompt.lower() for word in ["shot", "view", "angle"]):
            return False, "Missing camera angle"
        
        return True, "OK"
```

Integrate into story_processor:
```python
from processing.prompt_enhancer import PromptEnhancer

# In _process_chunk, after parsing prompts:
enhancer = PromptEnhancer()
enhanced_scenes = []

for idx, prompt_text in enumerate(prompt_lines[:prompts_needed]):
    # Enhance if needed
    prompt_text = enhancer.enhance_if_needed(
        prompt_text, 
        self.settings.visual_style
    )
    
    # Validate
    is_valid, reason = enhancer.validate_prompt(prompt_text)
    if not is_valid:
        logger.warning(f"Invalid prompt: {reason} - {prompt_text[:50]}...")
    
    # Create scene...
```

## Testing Requirements

### 1. Deduplication Testing
- Process a file with repetitive content
- Verify duplicates are removed
- Check that similarity threshold works correctly
- Ensure unique prompts are preserved

### 2. Quality Testing
- Generate prompts and manually review
- Verify all 12 elements are present
- Check for specific visual details
- Validate variety across prompts

### 3. Performance Testing
- Measure processing time with deduplication
- Ensure not too slow for large files
- Test with various similarity thresholds

## Configuration

Add to GUI settings panel:
```python
# Quality Settings Section
quality_frame = ctk.CTkFrame(middle_frame)
quality_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

ctk.CTkLabel(
    quality_frame,
    text="Quality Settings",
    font=ctk.CTkFont(size=14, weight="bold")
).pack(anchor="w", padx=10, pady=(10, 5))

self.deduplication_var = ctk.BooleanVar(value=True)
ctk.CTkCheckBox(
    quality_frame,
    text="Remove Duplicate Prompts",
    variable=self.deduplication_var
).pack(anchor="w", padx=20, pady=2)

# Similarity threshold slider
threshold_frame = ctk.CTkFrame(quality_frame, fg_color="transparent")
threshold_frame.pack(fill="x", padx=20, pady=5)

ctk.CTkLabel(threshold_frame, text="Similarity Threshold:").pack(side="left")
self.similarity_var = ctk.DoubleVar(value=0.85)
self.similarity_slider = ctk.CTkSlider(
    threshold_frame,
    from_=0.7,
    to=0.95,
    variable=self.similarity_var,
    width=200
)
self.similarity_slider.pack(side="left", padx=10)
self.similarity_label = ctk.CTkLabel(threshold_frame, text="85%")
self.similarity_label.pack(side="left")
```

## Priority
**High** - Directly impacts output quality and user satisfaction

## Estimated Effort
- Deduplication: 3-4 hours
- Enhanced Prompts: 4-5 hours
- Post-processing: 2 hours
- Testing: 2-3 hours
- Documentation: 1 hour
- **Total**: ~12-15 hours

## Success Metrics
- Reduce duplicate prompts by >80%
- Average prompt length >150 characters
- User satisfaction with prompt quality
- Variety score (measure uniqueness across prompts)
