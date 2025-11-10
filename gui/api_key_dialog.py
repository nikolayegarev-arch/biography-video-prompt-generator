"""
API key dialog for secure key input.
"""
import customtkinter as ctk
from typing import Optional, Dict


class APIKeyDialog(ctk.CTkToplevel):
    """Dialog for entering and managing API keys."""
    
    def __init__(self, parent, provider: str, current_key: str = ""):
        """
        Initialize API key dialog.
        
        Args:
            parent: Parent window
            provider: API provider name
            current_key: Current API key (if any)
        """
        super().__init__(parent)
        
        self.provider = provider
        self.result = None
        
        # Configure window
        self.title(f"Enter {provider.title()} API Key")
        self.geometry("500x300")
        self.resizable(False, False)
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        # Center on parent
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")
        
        self._create_widgets(current_key)
    
    def _create_widgets(self, current_key: str):
        """Create dialog widgets."""
        # Main frame
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text=f"{self.provider.title()} API Key",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(pady=(0, 10))
        
        # Instructions
        instructions = self._get_instructions()
        inst_label = ctk.CTkLabel(
            main_frame,
            text=instructions,
            wraplength=450,
            justify="left"
        )
        inst_label.pack(pady=(0, 20))
        
        # API Key entry
        key_label = ctk.CTkLabel(main_frame, text="API Key:")
        key_label.pack(anchor="w", pady=(0, 5))
        
        self.key_entry = ctk.CTkEntry(
            main_frame,
            width=450,
            show="*",
            placeholder_text="Enter your API key..."
        )
        self.key_entry.pack(pady=(0, 10))
        
        if current_key:
            self.key_entry.insert(0, current_key)
        
        # Show/hide checkbox
        self.show_var = ctk.BooleanVar(value=False)
        show_check = ctk.CTkCheckBox(
            main_frame,
            text="Show API key",
            variable=self.show_var,
            command=self._toggle_show_key
        )
        show_check.pack(anchor="w", pady=(0, 20))
        
        # Buttons frame
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(10, 0))
        
        # Cancel button
        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Cancel",
            width=100,
            command=self._on_cancel
        )
        cancel_btn.pack(side="right", padx=(10, 0))
        
        # OK button
        ok_btn = ctk.CTkButton(
            btn_frame,
            text="OK",
            width=100,
            command=self._on_ok
        )
        ok_btn.pack(side="right")
        
        # Bind Enter key
        self.key_entry.bind("<Return>", lambda e: self._on_ok())
        self.key_entry.focus()
    
    def _get_instructions(self) -> str:
        """Get instructions for the provider."""
        instructions = {
            "openrouter": "Get your API key from: https://openrouter.ai/keys\nKey format: sk-or-...",
            "openai": "Get your API key from: https://platform.openai.com/api-keys\nKey format: sk-...",
            "gemini": "Get your API key from: https://makersuite.google.com/app/apikey\nKey format: AIza...",
            "anthropic": "Get your API key from: https://console.anthropic.com/\nKey format: sk-ant-..."
        }
        return instructions.get(self.provider, "Enter your API key below.")
    
    def _toggle_show_key(self):
        """Toggle API key visibility."""
        if self.show_var.get():
            self.key_entry.configure(show="")
        else:
            self.key_entry.configure(show="*")
    
    def _on_ok(self):
        """Handle OK button."""
        key = self.key_entry.get().strip()
        if key:
            self.result = key
            self.destroy()
    
    def _on_cancel(self):
        """Handle Cancel button."""
        self.result = None
        self.destroy()
    
    def get_result(self) -> Optional[str]:
        """
        Get dialog result.
        
        Returns:
            API key or None if cancelled
        """
        return self.result


class APIKeyManager:
    """Manage API keys for multiple providers."""
    
    def __init__(self):
        """Initialize API key manager."""
        self.keys: Dict[str, str] = {}
    
    def get_key(self, provider: str) -> Optional[str]:
        """
        Get API key for provider.
        
        Args:
            provider: Provider name
            
        Returns:
            API key or None
        """
        return self.keys.get(provider)
    
    def set_key(self, provider: str, key: str):
        """
        Set API key for provider.
        
        Args:
            provider: Provider name
            key: API key
        """
        self.keys[provider] = key
    
    def has_key(self, provider: str) -> bool:
        """
        Check if key exists for provider.
        
        Args:
            provider: Provider name
            
        Returns:
            True if key exists
        """
        return provider in self.keys and bool(self.keys[provider])
    
    def prompt_for_key(self, parent, provider: str, current_key: str = "") -> Optional[str]:
        """
        Show dialog to prompt for API key.
        
        Args:
            parent: Parent window
            provider: Provider name
            current_key: Current key value
            
        Returns:
            API key or None if cancelled
        """
        dialog = APIKeyDialog(parent, provider, current_key)
        parent.wait_window(dialog)
        return dialog.get_result()
