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
from processing.similarity import SimilarityCalculator
from processing.prompt_quality import PromptQualityManager
from utils.file_ops import save_json, save_text, save_csv, load_json
from utils.retry_handler import RetryHandler
from exceptions import TextProcessingError, APIError

logger = logging.getLogger(__name__)

# Alias for backward compatibility
ProcessingConfig = Settings


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
        
        # Initialize quality management tools
        self.similarity_calculator = SimilarityCalculator(
            threshold=settings.deduplication_threshold
        )
        self.quality_manager = PromptQualityManager(
            enable_enhancement=settings.enable_enhancement
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
            
            # Calculate buffer factor for post-processing filters
            buffer_factor = self._calculate_buffer_factor()
            buffered_prompts = int(total_prompts * buffer_factor)
            logger.info(
                f"Generating {buffered_prompts} prompts (buffer factor: {buffer_factor:.2f}x) "
                f"to account for post-processing filters"
            )
            
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
                # Process chunks with buffered prompt count
                all_scenes = []
                prompts_per_chunk = max(1, buffered_prompts // total_chunks)
                
                start_chunk = metadata["processed_chunks"]
                
                for chunk_idx in range(start_chunk, total_chunks):
                    if progress_callback:
                        progress = 10 + (80 * chunk_idx / total_chunks)
                        progress_callback(
                            f"Processing chunk {chunk_idx + 1}/{total_chunks}...",
                            progress
                        )
                    
                    chunk_text = chunks[chunk_idx]
                    
                    # Get context from recent prompts for context-aware generation
                    recent_prompts = self._get_recent_prompts(all_scenes, count=3)
                    
                    # Generate prompts for chunk
                    chunk_scenes = self._process_chunk(
                        api_manager,
                        chunk_text,
                        chunk_idx,
                        total_chunks,
                        prompts_per_chunk,
                        len(all_scenes),
                        recent_prompts
                    )
                    
                    all_scenes.extend(chunk_scenes)
                    
                    # Update metadata and save partial progress
                    metadata["processed_chunks"] = chunk_idx + 1
                    metadata["scenes"] = all_scenes
                    save_json(partial_path, metadata)
                    
                    # Log to both logger and GUI
                    chunk_msg = f"Chunk {chunk_idx + 1}/{total_chunks} complete. Total scenes: {len(all_scenes)}"
                    logger.info(chunk_msg)
                    if progress_callback:
                        progress_callback(chunk_msg, 10 + (80 * (chunk_idx + 1) / total_chunks))
                
                # Post-processing: deduplication and quality filtering
                if progress_callback:
                    progress_callback("Post-processing prompts...", 90)
                
                original_count = len(all_scenes)
                all_scenes = self._post_process_scenes(all_scenes, total_prompts)
                
                logger.info(
                    f"Post-processing complete. "
                    f"Scenes: {original_count} -> {len(all_scenes)} "
                    f"(target: {total_prompts})"
                )
                
                # Finalize metadata
                metadata["total_prompts"] = len(all_scenes)
                metadata["metadata"]["total_prompts"] = len(all_scenes)  # Update nested path too
                metadata["scenes"] = all_scenes
                
                # Add quality metrics to metadata
                metadata["metadata"]["quality_metrics"] = self._calculate_quality_metrics(all_scenes)
                metadata["metadata"]["deduplication_enabled"] = self.settings.enable_deduplication
                metadata["metadata"]["quality_filter_enabled"] = self.settings.enable_quality_filter
                
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
        scene_offset: int,
        recent_prompts: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Process a single text chunk with context awareness.
        
        Args:
            api_manager: API manager
            chunk_text: Text chunk
            chunk_idx: Chunk index
            total_chunks: Total number of chunks
            prompts_needed: Number of prompts needed
            scene_offset: Scene offset for numbering
            recent_prompts: Recent prompts for context (to avoid repetition)
            
        Returns:
            List of scene dictionaries
        """
        system_prompt = PromptTemplates.get_system_prompt(
            self.settings.visual_style,
            self.settings.dense_mode
        )
        
        # Add context awareness to user prompt
        context_note = ""
        if recent_prompts:
            context_note = (
                "\n\nIMPORTANT: Avoid repetition. Recent prompts for context "
                "(generate different shots, angles, and visual elements):\n"
                + "\n".join(f"- {p}" for p in recent_prompts)
            )
        
        user_prompt = PromptTemplates.get_chunk_analysis_prompt(
            chunk_text,
            chunk_idx,
            total_chunks,
            prompts_needed,
            self.settings.visual_style
        ) + context_note
        
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
    
    def _post_process_scenes(
        self, 
        scenes: List[Dict[str, Any]], 
        target_count: int
    ) -> List[Dict[str, Any]]:
        """
        Post-process scenes with deduplication and quality filtering.
        
        Args:
            scenes: List of scene dictionaries
            target_count: Target number of prompts to maintain
            
        Returns:
            Processed list of scenes
        """
        if not scenes:
            return scenes
        
        # Deduplication
        if self.settings.enable_deduplication:
            logger.info(f"Running deduplication (threshold: {self.settings.deduplication_threshold})")
            scenes = self.similarity_calculator.deduplicate_with_metadata(scenes, key='prompt')
        
        # Quality filtering
        if self.settings.enable_quality_filter:
            logger.info(f"Running quality filter (min score: {self.settings.min_quality_score})")
            scenes = self._filter_low_quality_scenes(scenes)
        
        # Enhancement
        if self.settings.enable_enhancement:
            logger.info("Enhancing prompts")
            scenes = self._enhance_scenes(scenes)
        
        # Trim to target count if we have too many scenes
        if len(scenes) > target_count:
            logger.info(f"Trimming {len(scenes)} scenes to target count of {target_count}")
            scenes = scenes[:target_count]
        
        # Recalculate timestamps after filtering
        scenes = self._recalculate_timestamps(scenes)
        
        return scenes
    
    def _filter_low_quality_scenes(self, scenes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter out low-quality scenes.
        
        Args:
            scenes: List of scene dictionaries
            
        Returns:
            Filtered list of scenes
        """
        filtered_scenes = []
        
        for scene in scenes:
            prompt = scene.get('prompt', '')
            score = self.quality_manager.score_prompt(prompt)
            
            if score >= self.settings.min_quality_score:
                filtered_scenes.append(scene)
            else:
                logger.debug(
                    f"Filtered out low quality scene {scene.get('id', 'unknown')} "
                    f"(score: {score:.2f})"
                )
        
        removed_count = len(scenes) - len(filtered_scenes)
        if removed_count > 0:
            logger.info(f"Filtered out {removed_count} low-quality scenes")
        
        return filtered_scenes
    
    def _enhance_scenes(self, scenes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Enhance prompts in scenes.
        
        Args:
            scenes: List of scene dictionaries
            
        Returns:
            Enhanced list of scenes
        """
        for scene in scenes:
            if 'prompt' in scene:
                scene['prompt'] = self.quality_manager.enhance_prompt(scene['prompt'])
        
        return scenes
    
    def _recalculate_timestamps(self, scenes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Recalculate timestamps after filtering.
        
        Args:
            scenes: List of scene dictionaries
            
        Returns:
            Scenes with updated timestamps
        """
        for idx, scene in enumerate(scenes):
            scene['timestamp'] = idx * self.settings.frame_interval_seconds
        
        return scenes
    
    def _calculate_quality_metrics(self, scenes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate quality metrics for scenes.
        
        Args:
            scenes: List of scene dictionaries
            
        Returns:
            Quality metrics dictionary
        """
        if not scenes:
            return {}
        
        prompts = [scene.get('prompt', '') for scene in scenes]
        diversity = self.quality_manager.analyze_prompt_diversity(prompts)
        
        quality_scores = [self.quality_manager.score_prompt(p) for p in prompts]
        
        return {
            'avg_prompt_length': diversity['avg_length'],
            'vocabulary_size': diversity['vocabulary_size'],
            'avg_quality_score': diversity['avg_quality_score'],
            'min_quality_score': min(quality_scores) if quality_scores else 0,
            'max_quality_score': max(quality_scores) if quality_scores else 0
        }
    
    def _calculate_buffer_factor(self) -> float:
        """
        Calculate buffer factor for generating extra prompts.
        
        The buffer accounts for expected losses during post-processing:
        - Deduplication can remove 30-50% of prompts (depending on text repetition)
        - Quality filtering can remove 20-40% of prompts (depending on AI quality)
        - Combined effect can reduce count by 50-75% in worst cases
        
        Returns:
            Buffer multiplier (e.g., 2.0 means generate 2x the target)
        """
        buffer = 1.0
        
        # Add buffer for deduplication
        if self.settings.enable_deduplication:
            # Higher threshold means more aggressive filtering
            # Empirically, dedup can remove 30-50% with biographical texts
            dedup_factor = 1.8
            if self.settings.deduplication_threshold >= 0.9:
                dedup_factor = 1.5  # Less aggressive
            elif self.settings.deduplication_threshold <= 0.8:
                dedup_factor = 2.0  # More aggressive
            buffer *= dedup_factor
        
        # Add buffer for quality filtering
        if self.settings.enable_quality_filter:
            # Higher min score means more aggressive filtering
            # Quality filtering can remove 20-40% depending on min_score
            quality_factor = 1.4
            if self.settings.min_quality_score >= 0.6:
                quality_factor = 1.6  # More aggressive
            elif self.settings.min_quality_score <= 0.4:
                quality_factor = 1.25  # Less aggressive
            buffer *= quality_factor
        
        # Cap maximum buffer at 3.0x to balance quality and API costs
        # This ensures we generate enough prompts even with aggressive filtering
        buffer = min(buffer, 3.0)
        
        return buffer
    
    def _get_recent_prompts(self, scenes: List[Dict[str, Any]], count: int = 3) -> List[str]:
        """
        Get recent prompts for context-aware generation.
        
        Args:
            scenes: List of scene dictionaries
            count: Number of recent prompts to retrieve
            
        Returns:
            List of recent prompt texts
        """
        if not scenes:
            return []
        
        recent_scenes = scenes[-count:] if len(scenes) >= count else scenes
        return [scene.get('prompt', '') for scene in recent_scenes]
