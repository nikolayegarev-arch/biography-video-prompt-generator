"""
Main window for Biography Video Prompt Generator GUI.
"""
import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import logging
from pathlib import Path
from typing import Optional

from config import Settings, APIConfig
from gui.settings import GUISettings
from gui.api_key_dialog import APIKeyManager
from processing.story_processor import StoryProcessor
from utils.file_ops import list_files
from utils.config_loader import load_api_keys

# Configure CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

logger = logging.getLogger(__name__)


class MainWindow(ctk.CTk):
    """Main application window."""
    
    def __init__(self):
        """Initialize main window."""
        super().__init__()
        
        # Window configuration
        self.title("Biography Video Prompt Generator")
        self.geometry("900x700")
        self.minsize(800, 600)
        
        # Settings
        self.gui_settings = GUISettings()
        self.api_key_manager = APIKeyManager()
        self.processing = False
        
        # Load saved API keys
        self._load_saved_api_keys()
        
        # Create GUI
        self._create_widgets()
        self._load_gui_settings()
        
        # Protocol for window close
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _load_saved_api_keys(self):
        """Load API keys from config files."""
        try:
            api_keys = load_api_keys()
            for provider, key in api_keys.items():
                if key:
                    self.api_key_manager.set_key(provider, key)
        except Exception as e:
            logger.warning(f"Could not load saved API keys: {e}")
    
    def _create_widgets(self):
        """Create all GUI widgets."""
        # Main container with grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Top frame (settings)
        self._create_top_frame()
        
        # Middle frame (options and progress)
        self._create_middle_frame()
        
        # Bottom frame (logs)
        self._create_bottom_frame()
        
        # Control buttons at bottom
        self._create_control_frame()
    
    def _create_top_frame(self):
        """Create top settings frame."""
        top_frame = ctk.CTkFrame(self)
        top_frame.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="ew")
        top_frame.grid_columnconfigure(1, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            top_frame,
            text="Biography Video Prompt Generator",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(10, 20), sticky="w", padx=10)
        
        # Input folder
        row = 1
        ctk.CTkLabel(top_frame, text="Input Folder:").grid(
            row=row, column=0, padx=10, pady=5, sticky="w"
        )
        self.input_folder_var = ctk.StringVar(value="texts_to_process")
        self.input_folder_entry = ctk.CTkEntry(
            top_frame, textvariable=self.input_folder_var, width=400
        )
        self.input_folder_entry.grid(row=row, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkButton(
            top_frame, text="Browse", width=100, command=self._browse_input
        ).grid(row=row, column=2, padx=10, pady=5)
        
        # Output folder
        row += 1
        ctk.CTkLabel(top_frame, text="Output Folder:").grid(
            row=row, column=0, padx=10, pady=5, sticky="w"
        )
        self.output_folder_var = ctk.StringVar(value="video_prompts")
        self.output_folder_entry = ctk.CTkEntry(
            top_frame, textvariable=self.output_folder_var, width=400
        )
        self.output_folder_entry.grid(row=row, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkButton(
            top_frame, text="Browse", width=100, command=self._browse_output
        ).grid(row=row, column=2, padx=10, pady=5)
        
        # AI Provider
        row += 1
        ctk.CTkLabel(top_frame, text="AI Provider:").grid(
            row=row, column=0, padx=10, pady=5, sticky="w"
        )
        provider_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
        provider_frame.grid(row=row, column=1, columnspan=2, padx=5, pady=5, sticky="ew")
        
        self.provider_var = ctk.StringVar(value="openrouter")
        providers = ["openrouter", "openai", "gemini", "anthropic"]
        self.provider_menu = ctk.CTkOptionMenu(
            provider_frame,
            variable=self.provider_var,
            values=providers,
            width=200,
            command=self._on_provider_change
        )
        self.provider_menu.pack(side="left", padx=(0, 10))
        
        self.api_key_btn = ctk.CTkButton(
            provider_frame,
            text="Set API Key",
            width=120,
            command=self._set_api_key
        )
        self.api_key_btn.pack(side="left")
        
        # Model selection
        row += 1
        ctk.CTkLabel(top_frame, text="Model:").grid(
            row=row, column=0, padx=10, pady=5, sticky="w"
        )
        self.model_var = ctk.StringVar()
        self.model_menu = ctk.CTkOptionMenu(
            top_frame,
            variable=self.model_var,
            values=self._get_models_for_provider("openrouter"),
            width=400
        )
        self.model_menu.grid(row=row, column=1, columnspan=2, padx=5, pady=5, sticky="w")
        
        # Frame interval
        row += 1
        ctk.CTkLabel(top_frame, text="Frame Interval (3-30s):").grid(
            row=row, column=0, padx=10, pady=5, sticky="w"
        )
        interval_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
        interval_frame.grid(row=row, column=1, columnspan=2, padx=5, pady=5, sticky="ew")
        
        self.frame_interval_var = ctk.DoubleVar(value=6.0)
        self.frame_interval_slider = ctk.CTkSlider(
            interval_frame,
            from_=3,
            to=30,
            number_of_steps=27,
            variable=self.frame_interval_var,
            width=300,
            command=self._update_frame_label
        )
        self.frame_interval_slider.pack(side="left", padx=(0, 10))
        
        self.frame_interval_label = ctk.CTkLabel(interval_frame, text="6.0s")
        self.frame_interval_label.pack(side="left")
        
        # Narration speed
        row += 1
        ctk.CTkLabel(top_frame, text="Narration Speed (100-200 wpm):").grid(
            row=row, column=0, padx=10, pady=5, sticky="w"
        )
        speed_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
        speed_frame.grid(row=row, column=1, columnspan=2, padx=5, pady=5, sticky="ew")
        
        self.narration_speed_var = ctk.IntVar(value=150)
        self.narration_speed_slider = ctk.CTkSlider(
            speed_frame,
            from_=100,
            to=200,
            number_of_steps=100,
            variable=self.narration_speed_var,
            width=300,
            command=self._update_speed_label
        )
        self.narration_speed_slider.pack(side="left", padx=(0, 10))
        
        self.narration_speed_label = ctk.CTkLabel(speed_frame, text="150 wpm")
        self.narration_speed_label.pack(side="left")
        
        # Visual style
        row += 1
        ctk.CTkLabel(top_frame, text="Visual Style:").grid(
            row=row, column=0, padx=10, pady=5, sticky="w"
        )
        styles = self.gui_settings.get_visual_styles()
        self.visual_style_var = ctk.StringVar(value="historical illustration")
        self.visual_style_menu = ctk.CTkOptionMenu(
            top_frame,
            variable=self.visual_style_var,
            values=styles,
            width=400
        )
        self.visual_style_menu.grid(row=row, column=1, columnspan=2, padx=5, pady=5, sticky="w")
        
        # Padding at bottom
        top_frame.grid_rowconfigure(row + 1, minsize=10)
    
    def _create_middle_frame(self):
        """Create middle frame with options and progress."""
        middle_frame = ctk.CTkFrame(self)
        middle_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        middle_frame.grid_columnconfigure(0, weight=1)
        
        # Options section
        options_frame = ctk.CTkFrame(middle_frame)
        options_frame.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="ew")
        
        ctk.CTkLabel(
            options_frame,
            text="Options",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))
        
        self.dense_mode_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            options_frame,
            text="Dense Mode (detailed prompts)",
            variable=self.dense_mode_var
        ).pack(anchor="w", padx=20, pady=2)
        
        self.character_consistency_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            options_frame,
            text="Character Consistency",
            variable=self.character_consistency_var
        ).pack(anchor="w", padx=20, pady=2)
        
        options_frame.pack_configure(pady=(10, 5))
        
        # Progress section
        progress_frame = ctk.CTkFrame(middle_frame)
        progress_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        
        ctk.CTkLabel(
            progress_frame,
            text="Progress",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))
        
        # Status label
        self.status_var = ctk.StringVar(value="Ready")
        self.status_label = ctk.CTkLabel(
            progress_frame,
            textvariable=self.status_var,
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(padx=10, pady=5)
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(progress_frame, width=400)
        self.progress_bar.pack(padx=10, pady=(5, 10))
        self.progress_bar.set(0)
        
        # Estimated images label
        self.estimated_label = ctk.CTkLabel(
            progress_frame,
            text="Estimated images: 0",
            font=ctk.CTkFont(size=11)
        )
        self.estimated_label.pack(padx=10, pady=(0, 10))
    
    def _create_bottom_frame(self):
        """Create bottom frame with log output."""
        bottom_frame = ctk.CTkFrame(self)
        bottom_frame.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="nsew")
        bottom_frame.grid_columnconfigure(0, weight=1)
        bottom_frame.grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(
            bottom_frame,
            text="Logs",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
        
        # Log text box
        self.log_text = ctk.CTkTextbox(bottom_frame, height=150)
        self.log_text.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        self.log_text.configure(state="disabled")
    
    def _create_control_frame(self):
        """Create control buttons frame."""
        control_frame = ctk.CTkFrame(self, fg_color="transparent")
        control_frame.grid(row=3, column=0, padx=10, pady=(0, 10), sticky="ew")
        
        # Start/Stop button
        self.start_btn = ctk.CTkButton(
            control_frame,
            text="Start Processing",
            width=150,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._start_processing
        )
        self.start_btn.pack(side="right", padx=10)
        
        # Clear logs button
        clear_btn = ctk.CTkButton(
            control_frame,
            text="Clear Logs",
            width=120,
            command=self._clear_logs
        )
        clear_btn.pack(side="right")
    
    def _get_models_for_provider(self, provider: str) -> list:
        """Get models for provider."""
        models = self.gui_settings.get_provider_models(provider)
        return models if models else ["default"]
    
    def _on_provider_change(self, provider: str):
        """Handle provider change."""
        models = self._get_models_for_provider(provider)
        self.model_menu.configure(values=models)
        if models:
            self.model_var.set(models[0])
    
    def _update_frame_label(self, value):
        """Update frame interval label."""
        self.frame_interval_label.configure(text=f"{value:.1f}s")
        self._update_estimated_images()
    
    def _update_speed_label(self, value):
        """Update narration speed label."""
        self.narration_speed_label.configure(text=f"{int(value)} wpm")
        self._update_estimated_images()
    
    def _update_estimated_images(self):
        """Update estimated images count."""
        # This is a rough estimate - actual count depends on text
        # Assume average 12000 words
        try:
            words = 12000
            wpm = self.narration_speed_var.get()
            interval = self.frame_interval_var.get()
            
            duration_minutes = words / wpm
            duration_seconds = duration_minutes * 60
            estimated_images = int(duration_seconds / interval)
            
            self.estimated_label.configure(
                text=f"Estimated images: ~{estimated_images} (for 12k words)"
            )
        except:
            pass
    
    def _browse_input(self):
        """Browse for input folder."""
        folder = filedialog.askdirectory(
            title="Select Input Folder",
            initialdir=self.input_folder_var.get()
        )
        if folder:
            self.input_folder_var.set(folder)
    
    def _browse_output(self):
        """Browse for output folder."""
        folder = filedialog.askdirectory(
            title="Select Output Folder",
            initialdir=self.output_folder_var.get()
        )
        if folder:
            self.output_folder_var.set(folder)
    
    def _set_api_key(self):
        """Show API key dialog."""
        provider = self.provider_var.get()
        current_key = self.api_key_manager.get_key(provider) or ""
        
        from gui.api_key_dialog import APIKeyDialog
        dialog = APIKeyDialog(self, provider, current_key)
        self.wait_window(dialog)
        
        result = dialog.get_result()
        if result:
            self.api_key_manager.set_key(provider, result)
            self.log(f"API key set for {provider}")
    
    def _start_processing(self):
        """Start processing files."""
        if self.processing:
            self.log("Already processing...")
            return
        
        # Validate settings
        provider = self.provider_var.get()
        if not self.api_key_manager.has_key(provider):
            messagebox.showerror(
                "API Key Required",
                f"Please set API key for {provider} before processing."
            )
            return
        
        model = self.model_var.get()
        if not model:
            messagebox.showerror("Model Required", "Please select a model.")
            return
        
        input_folder = Path(self.input_folder_var.get())
        if not input_folder.exists():
            messagebox.showerror("Error", "Input folder does not exist.")
            return
        
        # Get list of files to process
        files = list_files(input_folder, "*.txt")
        if not files:
            messagebox.showwarning("No Files", "No .txt files found in input folder.")
            return
        
        # Start processing in thread
        self.processing = True
        self.start_btn.configure(state="disabled", text="Processing...")
        self.log(f"Starting processing of {len(files)} file(s)...")
        
        thread = threading.Thread(
            target=self._process_files_thread,
            args=(files,),
            daemon=True
        )
        thread.start()
    
    def _process_files_thread(self, files: list):
        """Process files in background thread."""
        try:
            # Create settings
            api_config = APIConfig(
                provider=self.provider_var.get(),
                api_key=self.api_key_manager.get_key(self.provider_var.get()),
                model=self.model_var.get()
            )
            
            settings = Settings(
                frame_interval_seconds=self.frame_interval_var.get(),
                narration_speed_wpm=self.narration_speed_var.get(),
                visual_style=self.visual_style_var.get(),
                dense_mode=self.dense_mode_var.get(),
                character_consistency=self.character_consistency_var.get(),
                api_config=api_config,
                input_folder=self.input_folder_var.get(),
                output_folder=self.output_folder_var.get()
            )
            
            # Process each file
            processor = StoryProcessor(settings)
            output_folder = Path(settings.output_folder)
            output_folder.mkdir(parents=True, exist_ok=True)
            
            for i, input_file in enumerate(files):
                self.log(f"\nProcessing {input_file.name} ({i+1}/{len(files)})...")
                
                output_file = output_folder / f"{input_file.stem}.video_prompts.json"
                
                def progress_callback(message: str, percent: float):
                    self.update_progress(message, percent / 100.0)
                
                try:
                    result = processor.process_file(
                        input_file,
                        output_file,
                        progress_callback
                    )
                    
                    self.log(f"✓ Completed {input_file.name}")
                    self.log(f"  Generated {result['metadata']['total_prompts']} prompts")
                    self.log(f"  Output: {output_file}")
                
                except Exception as e:
                    self.log(f"✗ Error processing {input_file.name}: {e}")
                    logger.error(f"Processing error: {e}", exc_info=True)
            
            self.log("\n=== Processing Complete ===")
            self.update_progress("Complete!", 1.0)
        
        except Exception as e:
            self.log(f"\n✗ Fatal error: {e}")
            logger.error(f"Fatal processing error: {e}", exc_info=True)
        
        finally:
            self.processing = False
            self.after(0, lambda: self.start_btn.configure(
                state="normal",
                text="Start Processing"
            ))
    
    def update_progress(self, message: str, percent: float):
        """Update progress from thread."""
        def update():
            self.status_var.set(message)
            self.progress_bar.set(percent)
        self.after(0, update)
    
    def log(self, message: str):
        """Add message to log."""
        def add_log():
            self.log_text.configure(state="normal")
            self.log_text.insert("end", message + "\n")
            self.log_text.see("end")
            self.log_text.configure(state="disabled")
        self.after(0, add_log)
    
    def _clear_logs(self):
        """Clear log output."""
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")
    
    def _load_gui_settings(self):
        """Load GUI settings."""
        try:
            if self.gui_settings.get("last_input_folder"):
                self.input_folder_var.set(self.gui_settings.get("last_input_folder"))
            if self.gui_settings.get("last_output_folder"):
                self.output_folder_var.set(self.gui_settings.get("last_output_folder"))
            if self.gui_settings.get("last_provider"):
                provider = self.gui_settings.get("last_provider")
                self.provider_var.set(provider)
                self._on_provider_change(provider)
            if self.gui_settings.get("frame_interval"):
                self.frame_interval_var.set(self.gui_settings.get("frame_interval"))
            if self.gui_settings.get("narration_speed"):
                self.narration_speed_var.set(self.gui_settings.get("narration_speed"))
            if self.gui_settings.get("visual_style"):
                self.visual_style_var.set(self.gui_settings.get("visual_style"))
            if self.gui_settings.get("dense_mode") is not None:
                self.dense_mode_var.set(self.gui_settings.get("dense_mode"))
            if self.gui_settings.get("character_consistency") is not None:
                self.character_consistency_var.set(
                    self.gui_settings.get("character_consistency")
                )
            
            self._update_estimated_images()
        except Exception as e:
            logger.warning(f"Failed to load GUI settings: {e}")
    
    def _save_gui_settings(self):
        """Save GUI settings."""
        try:
            self.gui_settings.update({
                "last_input_folder": self.input_folder_var.get(),
                "last_output_folder": self.output_folder_var.get(),
                "last_provider": self.provider_var.get(),
                "last_model": self.model_var.get(),
                "frame_interval": self.frame_interval_var.get(),
                "narration_speed": self.narration_speed_var.get(),
                "visual_style": self.visual_style_var.get(),
                "dense_mode": self.dense_mode_var.get(),
                "character_consistency": self.character_consistency_var.get()
            })
            self.gui_settings.save()
        except Exception as e:
            logger.error(f"Failed to save GUI settings: {e}")
    
    def _on_closing(self):
        """Handle window close."""
        if self.processing:
            if not messagebox.askokcancel(
                "Processing in Progress",
                "Processing is still running. Are you sure you want to quit?"
            ):
                return
        
        self._save_gui_settings()
        self.destroy()


def main():
    """Main entry point for GUI."""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and run app
    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    main()
