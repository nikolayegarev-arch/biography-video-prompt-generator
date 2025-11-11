# Feature Request: Custom Model Selector

## Overview
Add ability to add custom AI models to the Model dropdown, allowing users to easily input and save custom model names (e.g., `tngtech/deepseek-r1t2-chimera:free`) for any provider, especially OpenRouter.

## Current Behavior
- Model dropdown shows predefined models from `gui/settings.py`
- Users cannot add custom models without modifying code
- Each provider has a fixed list of models

## Proposed Behavior
- Add a "+" button next to the Model dropdown
- Clicking "+" opens a dialog to enter custom model name
- Custom models are saved to user preferences
- Custom models appear in dropdown alongside predefined models
- Users can remove custom models they've added

## Implementation Details

### UI Changes Required

#### 1. Add "+" Button to Model Selection Area
**File**: `gui/main_window.py` (~line 151-161)

Current code:
```python
ctk.CTkLabel(top_frame, text="Model:").grid(
    row=row, column=0, padx=10, pady=5, sticky="w"
)
self.model_var = ctk.StringVar()
models = self._get_models_for_provider(self.provider_var.get())
self.model_var.set(models[0] if models else "")
self.model_menu = ctk.CTkOptionMenu(
    top_frame,
    variable=self.model_var,
    values=models,
    width=400
)
self.model_menu.grid(row=row, column=1, columnspan=2, padx=5, pady=5, sticky="w")
```

Proposed change:
```python
ctk.CTkLabel(top_frame, text="Model:").grid(
    row=row, column=0, padx=10, pady=5, sticky="w"
)

# Create frame for model dropdown and add button
model_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
model_frame.grid(row=row, column=1, columnspan=2, padx=5, pady=5, sticky="w")

self.model_var = ctk.StringVar()
models = self._get_models_for_provider(self.provider_var.get())
self.model_var.set(models[0] if models else "")
self.model_menu = ctk.CTkOptionMenu(
    model_frame,
    variable=self.model_var,
    values=models,
    width=350
)
self.model_menu.pack(side="left", padx=(0, 5))

# Add "+" button
self.add_model_btn = ctk.CTkButton(
    model_frame,
    text="+",
    width=40,
    height=28,
    command=self._add_custom_model
)
self.add_model_btn.pack(side="left")
```

#### 2. Create Custom Model Dialog
**New File**: `gui/custom_model_dialog.py`

```python
"""Dialog for adding custom AI models."""
import customtkinter as ctk
from typing import Optional

class CustomModelDialog(ctk.CTkToplevel):
    """Dialog for entering custom model name."""
    
    def __init__(self, parent, provider: str):
        super().__init__(parent)
        self.provider = provider
        self.result = None
        
        self.title(f"Add Custom Model - {provider.title()}")
        self.geometry("500x250")
        self.resizable(False, False)
        
        self.transient(parent)
        self.grab_set()
        
        self._create_widgets()
        self._center_on_parent(parent)
    
    def _create_widgets(self):
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title = ctk.CTkLabel(
            main_frame,
            text="Add Custom Model",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title.pack(pady=(0, 10))
        
        # Instructions
        instructions = ctk.CTkLabel(
            main_frame,
            text=f"Enter the model identifier for {self.provider}.\n"
                 "Examples:\n"
                 "  • tngtech/deepseek-r1t2-chimera:free\n"
                 "  • anthropic/claude-3-opus\n"
                 "  • meta-llama/llama-3-70b",
            justify="left",
            wraplength=450
        )
        instructions.pack(pady=(0, 15))
        
        # Model name entry
        label = ctk.CTkLabel(main_frame, text="Model Name:")
        label.pack(anchor="w", pady=(0, 5))
        
        self.model_entry = ctk.CTkEntry(
            main_frame,
            width=450,
            placeholder_text="e.g., provider/model-name:variant"
        )
        self.model_entry.pack(pady=(0, 20))
        self.model_entry.focus()
        
        # Buttons
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x")
        
        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Cancel",
            width=100,
            command=self._on_cancel
        )
        cancel_btn.pack(side="right", padx=(10, 0))
        
        ok_btn = ctk.CTkButton(
            btn_frame,
            text="Add Model",
            width=100,
            command=self._on_ok
        )
        ok_btn.pack(side="right")
        
        self.model_entry.bind("<Return>", lambda e: self._on_ok())
    
    def _center_on_parent(self, parent):
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")
    
    def _on_ok(self):
        model = self.model_entry.get().strip()
        if model:
            self.result = model
            self.destroy()
    
    def _on_cancel(self):
        self.result = None
        self.destroy()
    
    def get_result(self) -> Optional[str]:
        return self.result
```

#### 3. Add Custom Model Management Methods
**File**: `gui/main_window.py`

Add these methods:
```python
def _add_custom_model(self):
    """Show dialog to add custom model."""
    from gui.custom_model_dialog import CustomModelDialog
    
    provider = self.provider_var.get()
    dialog = CustomModelDialog(self, provider)
    self.wait_window(dialog)
    
    model = dialog.get_result()
    if model:
        # Save to custom models
        self._save_custom_model(provider, model)
        
        # Update dropdown
        models = self._get_models_for_provider(provider)
        self.model_menu.configure(values=models)
        self.model_var.set(model)
        
        self.log(f"Added custom model: {model}")

def _save_custom_model(self, provider: str, model: str):
    """Save custom model to settings."""
    custom_models = self.gui_settings.get("custom_models", {})
    if provider not in custom_models:
        custom_models[provider] = []
    
    if model not in custom_models[provider]:
        custom_models[provider].append(model)
        self.gui_settings.set("custom_models", custom_models)
        self.gui_settings.save()

def _get_custom_models(self, provider: str) -> list:
    """Get custom models for provider."""
    custom_models = self.gui_settings.get("custom_models", {})
    return custom_models.get(provider, [])
```

#### 4. Update Model Retrieval
**File**: `gui/main_window.py`

Modify `_get_models_for_provider`:
```python
def _get_models_for_provider(self, provider: str) -> list:
    """Get models for provider including custom models."""
    # Get predefined models
    models = self.gui_settings.get_provider_models(provider)
    if not models:
        models = ["default"]
    
    # Add custom models
    custom_models = self._get_custom_models(provider)
    
    # Combine: custom models first (user's preference), then predefined
    all_models = custom_models + [m for m in models if m not in custom_models]
    
    return all_models
```

### Settings Persistence

**File**: `gui/settings.py`

Ensure the settings file can store custom models:
```python
# Custom models structure in settings:
{
    "custom_models": {
        "openrouter": [
            "tngtech/deepseek-r1t2-chimera:free",
            "custom/model-1"
        ],
        "openai": [
            "gpt-4-custom"
        ],
        "anthropic": [],
        "gemini": []
    }
}
```

## Testing Requirements

1. **Add Custom Model**
   - Click "+" button
   - Enter model name
   - Verify model appears in dropdown
   - Verify model is selected automatically

2. **Persistence**
   - Add custom model
   - Close application
   - Reopen application
   - Verify custom model still appears in dropdown

3. **Multiple Providers**
   - Add custom models for different providers
   - Switch between providers
   - Verify correct custom models show for each provider

4. **Model Selection**
   - Add custom model
   - Process file using custom model
   - Verify custom model is passed to API

## Future Enhancements

- Add "×" button to remove custom models
- Validate model name format
- Test model connectivity before saving
- Import/export custom model lists
- Share custom models between users

## Priority
**Medium** - Useful feature for power users, not critical for basic functionality

## Estimated Effort
- UI Implementation: 2-3 hours
- Testing: 1 hour
- Documentation: 30 minutes
- **Total**: ~4 hours
