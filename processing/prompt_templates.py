"""
Prompt templates for generating image prompts with 12-element structure.
"""
from typing import Optional


class PromptTemplates:
    """Templates for generating structured image prompts."""
    
    @staticmethod
    def get_system_prompt(visual_style: str, dense_mode: bool = False) -> str:
        """
        Get system prompt for AI model.
        
        Args:
            visual_style: Visual style for images
            dense_mode: Whether to generate detailed prompts
            
        Returns:
            System prompt
        """
        detail_level = "highly detailed and specific" if dense_mode else "concise but descriptive"
        
        return f"""You are an expert at creating image generation prompts for biographical video content.

Your task is to analyze biographical text and generate {detail_level} prompts following a 12-element structure:

1. SHOT TYPE: Specify camera angle and framing (wide shot, medium shot, close-up, extreme close-up, tracking shot, aerial shot, over-the-shoulder, etc.)

2. SUBJECT: Main characters/people with physical appearance details (age, build, facial features, posture)

3. ACTION: What the subject is doing, including micro-expressions and body language

4. SETTING: Location, architecture, interior/exterior details, time period indicators

5. COMPOSITION: Rule of thirds, camera position, visual balance, depth

6. LIGHTING: Light source, direction, quality (soft/hard), color temperature

7. MOOD: Overall atmosphere and emotional tone

8. KEY DETAILS: Important objects, textures, materials, effects (motion blur, depth of field)

9. COLOR PALETTE: Specific colors and color relationships (warm/cool, contrasting/harmonious)

10. STYLE: Visual style - "{visual_style}"

11. TECHNICAL: Quality descriptors (8k, highly detailed, cinematic, photorealistic, etc.)

12. CHARACTER APPEARANCE: Consistent character descriptions if applicable

Generate prompts that are visually rich, cinematically compelling, and appropriate for {visual_style} style.
Each prompt should be suitable for image generation AI like Midjourney, DALL-E, or Stable Diffusion."""
    
    @staticmethod
    def get_chunk_analysis_prompt(
        chunk_text: str,
        chunk_index: int,
        total_chunks: int,
        prompts_needed: int,
        visual_style: str,
        character_profiles: Optional[str] = None
    ) -> str:
        """
        Get prompt for analyzing a text chunk.
        
        Args:
            chunk_text: Text chunk to analyze
            chunk_index: Current chunk index (0-based)
            total_chunks: Total number of chunks
            prompts_needed: Number of prompts to generate for this chunk
            visual_style: Visual style
            character_profiles: Optional character descriptions for consistency
            
        Returns:
            Analysis prompt
        """
        character_context = ""
        if character_profiles:
            character_context = f"\n\nCharacter Profiles (maintain consistency):\n{character_profiles}\n"
        
        return f"""Analyze the following biographical text segment (chunk {chunk_index + 1} of {total_chunks}) and generate {prompts_needed} image prompts.

{character_context}

TEXT SEGMENT:
{chunk_text}

Generate exactly {prompts_needed} image prompts following the 12-element structure. Each prompt should:
- Capture a key moment or scene from the text
- Progress chronologically through the segment
- Include all 12 elements (shot type, subject, action, setting, composition, lighting, mood, key details, color palette, style, technical, character appearance)
- Be visually distinct and cinematically compelling
- Match the "{visual_style}" style

Format each prompt as a single paragraph with clear separation of the 12 elements.
Return ONLY the prompts, one per line, no numbering or extra text."""
    
    @staticmethod
    def get_scene_analysis_prompt(scene_text: str, visual_style: str) -> str:
        """
        Get prompt for analyzing a single scene.
        
        Args:
            scene_text: Scene text
            visual_style: Visual style
            
        Returns:
            Scene analysis prompt
        """
        return f"""Analyze this scene and generate a single image prompt with 12 elements:

SCENE TEXT:
{scene_text}

Generate ONE image prompt following this structure:
1. Shot type (camera angle/framing)
2. Subject (who, physical appearance)
3. Action (what they're doing, expressions)
4. Setting (where, architecture, time period)
5. Composition (visual arrangement)
6. Lighting (source, direction, quality, color)
7. Mood (atmosphere)
8. Key details (objects, textures, effects)
9. Color palette (specific colors)
10. Style: {visual_style}
11. Technical: 8k, highly detailed, cinematic
12. Character appearance (if applicable)

Return ONLY the prompt as a single paragraph, no explanations."""
    
    @staticmethod
    def format_prompt_with_metadata(
        prompt: str,
        shot_type: str,
        emotions: dict,
        objects: list,
        time_of_day: str,
        weather: str
    ) -> dict:
        """
        Format prompt with metadata.
        
        Args:
            prompt: Generated prompt text
            shot_type: Shot type classification
            emotions: Emotion dictionary
            objects: List of objects
            time_of_day: Time of day
            weather: Weather condition
            
        Returns:
            Formatted prompt dictionary
        """
        return {
            "prompt": prompt,
            "shot_type": shot_type,
            "emotions": emotions,
            "objects": objects,
            "time_of_day": time_of_day,
            "weather": weather
        }
