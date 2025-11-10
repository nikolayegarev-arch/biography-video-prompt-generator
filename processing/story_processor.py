"""
Main story processor for generating image prompts from biographical text.
"""
import logging
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from config import Settings
from api.api_manager import APIManager
from processing.text_processor import TextProcessor
from processing.prompt_templates import PromptTemplates
from processing.scene_analyzer import SceneAnalyzer
from utils.file_ops import save_json, save_text, save_csv, load_json
from utils.retry_handler import RetryHandler
from exceptions import TextProcessingError, APIError

logger = logging.getLogger(__name__)


class StoryProcessor:
    """Process biographical stories and generate image prompts."""
    
    def __init__(self, settings: Settings):
        """
        Initialize story processor.
        
        Args:
            settings: Application settings
        """
        self.settings = settings
        self.text_processor = TextProcessor(chunk_size=settings.chunk_size)
        self.scene_analyzer = SceneAnalyzer()
        self.retry_handler = RetryHandler(
            max_retries=settings.max_retries,
            initial_delay=settings.initial_retry_delay,
            max_delay=settings.max_retry_delay,
            exponential_base=settings.retry_exponential_base
        )
    
    def process_file(
        self,
        input_path: Path,
        output_path: Path,
        progress_callback: Optional[Callable[[str, float], None]] = None
    ) -> Dict[str, Any]:
        """
        Process a biographical text file and generate prompts.
        
        Args:
            input_path: Path to input text file
            output_path: Path to output JSON file
            progress_callback: Optional callback for progress updates (message, percentage)
            
        Returns:
            Processing results metadata
            
        Raises:
            TextProcessingError: If processing fails
        """
        try:
            logger.info(f"Processing file: {input_path}")
            
            # Read input file
            if progress_callback:
                progress_callback("Reading input file...", 0)
            
            with open(input_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            word_count = self.text_processor.count_words(text)
            logger.info(f"Input text: {word_count} words")
            
            # Calculate timeline
            if progress_callback:
                progress_callback("Calculating timeline...", 5)
            
            timeline = self.text_processor.calculate_timeline(
                word_count,
                self.settings.narration_speed_wpm,
                self.settings.frame_interval_seconds
            )
            
            total_prompts = timeline["total_prompts"]
            logger.info(f"Target: {total_prompts} prompts")
            
            # Split into chunks
            if progress_callback:
                progress_callback("Splitting text into chunks...", 10)
            
            chunks = self.text_processor.split_into_chunks(text)
            total_chunks = len(chunks)
            
            # Check for partial progress
            partial_path = output_path.with_suffix('.partial.json')
            metadata = self._load_or_create_metadata(
                partial_path, timeline, total_chunks, word_count
            )
            
            # Initialize API manager
            api_manager = APIManager(self.settings.api_config)
            
            try:
                # Process chunks
                all_scenes = []
                prompts_per_chunk = max(1, total_prompts // total_chunks)
                
                start_chunk = metadata["processed_chunks"]
                
                for chunk_idx in range(start_chunk, total_chunks):
                    if progress_callback:
                        progress = 10 + (80 * chunk_idx / total_chunks)
                        progress_callback(
                            f"Processing chunk {chunk_idx + 1}/{total_chunks}...",
                            progress
                        )
                    
                    chunk_text = chunks[chunk_idx]
                    
                    # Generate prompts for chunk
                    chunk_scenes = self._process_chunk(
                        api_manager,
                        chunk_text,
                        chunk_idx,
                        total_chunks,
                        prompts_per_chunk,
                        len(all_scenes)
                    )
                    
                    all_scenes.extend(chunk_scenes)
                    
                    # Update metadata and save partial progress
                    metadata["processed_chunks"] = chunk_idx + 1
                    metadata["scenes"] = all_scenes
                    save_json(partial_path, metadata)
                    
                    logger.info(
                        f"Chunk {chunk_idx + 1}/{total_chunks} complete. "
                        f"Total scenes: {len(all_scenes)}"
                    )
                
                # Finalize metadata
                metadata["total_prompts"] = len(all_scenes)
                metadata["scenes"] = all_scenes
                
                # Save final outputs
                if progress_callback:
                    progress_callback("Saving results...", 95)
                
                self._save_outputs(output_path, metadata)
                
                # Clean up partial file
                if partial_path.exists():
                    partial_path.unlink()
                
                if progress_callback:
                    progress_callback("Complete!", 100)
                
                logger.info(f"Processing complete. Generated {len(all_scenes)} prompts")
                return metadata
            
            finally:
                api_manager.close()
        
        except Exception as e:
            logger.error(f"Failed to process file: {e}")
            raise TextProcessingError(f"Processing failed: {e}")
    
    def _load_or_create_metadata(
        self,
        partial_path: Path,
        timeline: Dict[str, Any],
        total_chunks: int,
        word_count: int
    ) -> Dict[str, Any]:
        """Load partial progress or create new metadata."""
        if partial_path.exists():
            try:
                metadata = load_json(partial_path)
                logger.info(
                    f"Resuming from chunk {metadata['processed_chunks']}/{total_chunks}"
                )
                return metadata
            except Exception as e:
                logger.warning(f"Failed to load partial progress: {e}. Starting fresh.")
        
        # Create new metadata
        return {
            "metadata": {
                "total_prompts": timeline["total_prompts"],
                "total_duration_seconds": timeline["total_duration_seconds"],
                "frame_interval_seconds": self.settings.frame_interval_seconds,
                "narration_speed_wpm": self.settings.narration_speed_wpm,
                "visual_style": self.settings.visual_style,
                "character_profiles": {},
                "source_word_count": word_count,
                "total_chunks": total_chunks,
                "processed_chunks": 0,
                "dense_mode": self.settings.dense_mode,
                "character_consistency": self.settings.character_consistency
            },
            "scenes": [],
            "processed_chunks": 0
        }
    
    def _process_chunk(
        self,
        api_manager: APIManager,
        chunk_text: str,
        chunk_idx: int,
        total_chunks: int,
        prompts_needed: int,
        scene_offset: int
    ) -> List[Dict[str, Any]]:
        """Process a single text chunk."""
        system_prompt = PromptTemplates.get_system_prompt(
            self.settings.visual_style,
            self.settings.dense_mode
        )
        
        user_prompt = PromptTemplates.get_chunk_analysis_prompt(
            chunk_text,
            chunk_idx,
            total_chunks,
            prompts_needed,
            self.settings.visual_style
        )
        
        # Generate prompts with retry
        response = self.retry_handler.retry(
            api_manager.generate,
            user_prompt,
            system_prompt
        )
        
        # Parse response into individual prompts
        prompt_lines = [
            line.strip() 
            for line in response.strip().split('\n')
            if line.strip() and not line.strip().startswith('#')
        ]
        
        # Create scene objects
        scenes = []
        for idx, prompt_text in enumerate(prompt_lines[:prompts_needed]):
            scene_id = f"scene_{chunk_idx}_{idx}"
            timestamp = (scene_offset + idx) * self.settings.frame_interval_seconds
            
            # Analyze scene
            analysis = self.scene_analyzer.analyze_scene(prompt_text)
            
            scene = {
                "id": scene_id,
                "timestamp": timestamp,
                "prompt": prompt_text,
                "chunk": chunk_idx,
                "scene": idx,
                "word_index": chunk_idx * self.settings.chunk_size,
                "shot_type": analysis["shot_type"],
                "emotions": analysis["emotions"],
                "objects": analysis["objects"],
                "time_of_day": analysis["time_of_day"],
                "weather": analysis["weather"]
            }
            
            scenes.append(scene)
        
        return scenes
    
    def _save_outputs(self, output_path: Path, metadata: Dict[str, Any]):
        """Save outputs in multiple formats."""
        # Save JSON
        save_json(output_path, metadata)
        logger.info(f"Saved JSON: {output_path}")
        
        # Save TXT
        txt_path = output_path.with_suffix('.txt')
        txt_content = self._format_text_output(metadata)
        save_text(txt_path, txt_content)
        logger.info(f"Saved TXT: {txt_path}")
        
        # Save CSV
        csv_path = output_path.with_suffix('.csv')
        csv_data = self._format_csv_data(metadata)
        save_csv(csv_path, csv_data)
        logger.info(f"Saved CSV: {csv_path}")
    
    def _format_text_output(self, metadata: Dict[str, Any]) -> str:
        """Format metadata as readable text."""
        lines = []
        lines.append("=" * 80)
        lines.append("BIOGRAPHY VIDEO PROMPTS")
        lines.append("=" * 80)
        lines.append("")
        
        meta = metadata.get("metadata", {})
        lines.append(f"Total Prompts: {meta.get('total_prompts', 0)}")
        lines.append(f"Total Duration: {meta.get('total_duration_seconds', 0):.1f} seconds")
        lines.append(f"Frame Interval: {meta.get('frame_interval_seconds', 0)} seconds")
        lines.append(f"Visual Style: {meta.get('visual_style', 'N/A')}")
        lines.append(f"Source Words: {meta.get('source_word_count', 0)}")
        lines.append("")
        lines.append("=" * 80)
        lines.append("")
        
        for scene in metadata.get("scenes", []):
            lines.append(f"Scene ID: {scene['id']}")
            lines.append(f"Timestamp: {scene['timestamp']:.1f}s")
            lines.append(f"Shot Type: {scene['shot_type']}")
            lines.append(f"Time: {scene['time_of_day']} | Weather: {scene['weather']}")
            if scene.get('emotions'):
                lines.append(f"Emotions: {scene['emotions']}")
            if scene.get('objects'):
                lines.append(f"Objects: {', '.join(scene['objects'][:5])}")
            lines.append("")
            lines.append(f"PROMPT: {scene['prompt']}")
            lines.append("")
            lines.append("-" * 80)
            lines.append("")
        
        return "\n".join(lines)
    
    def _format_csv_data(self, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Format metadata as CSV data."""
        csv_data = []
        
        for scene in metadata.get("scenes", []):
            row = {
                "scene_id": scene["id"],
                "timestamp": f"{scene['timestamp']:.1f}",
                "chunk": scene["chunk"],
                "shot_type": scene["shot_type"],
                "time_of_day": scene["time_of_day"],
                "weather": scene["weather"],
                "emotions": json.dumps(scene.get("emotions", {})),
                "objects": ", ".join(scene.get("objects", [])[:5]),
                "prompt": scene["prompt"]
            }
            csv_data.append(row)
        
        return csv_data
