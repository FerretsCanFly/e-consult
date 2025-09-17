"""Settings management module for storing and retrieving application settings."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional
from src.models.schemas import Settings

logger = logging.getLogger("settings_manager")

# Settings file path (relative to project root)
SETTINGS_FILE = "settings.json"

def get_settings_file_path() -> Path:
    """Get the absolute path to the settings file."""
    return Path(SETTINGS_FILE)

def load_settings() -> Settings:
    """Load settings from the JSON file."""
    settings_path = get_settings_file_path()
    
    if not settings_path.exists():
        logger.info("Settings file not found, creating default settings")
        default_settings = Settings()
        save_settings(default_settings)
        return default_settings
    
    try:
        with open(settings_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Handle migration from old format if needed
        if isinstance(data, dict):
            return Settings(**data)
        else:
            logger.warning("Invalid settings format, using defaults")
            return Settings()
            
    except (json.JSONDecodeError, KeyError) as e:
        logger.error("Failed to load settings: %s", e)
        return Settings()

def save_settings(settings: Settings) -> bool:
    """Save settings to the JSON file."""
    try:
        settings_path = get_settings_file_path()
        
        # Update timestamp
        settings.last_updated = datetime.now().isoformat()
        
        # Ensure directory exists
        settings_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(settings_path, "w", encoding="utf-8") as f:
            json.dump(settings.model_dump(), f, indent=2, ensure_ascii=False)
        
        logger.info("Settings saved successfully")
        return True
        
    except Exception as e:
        logger.error("Failed to save settings: %s", e)
        return False

def get_default_system_prompts() -> str:
    """Get the current default system prompts."""
    settings = load_settings()
    return settings.default_system_prompts

def update_default_system_prompts(prompts: str) -> bool:
    """Update the default system prompts."""
    settings = load_settings()
    settings.default_system_prompts = prompts
    
    return save_settings(settings)

def reset_settings() -> bool:
    """Reset settings to defaults."""
    try:
        settings_path = get_settings_file_path()
        if settings_path.exists():
            settings_path.unlink()
            logger.info("Settings reset to defaults")
        return True
    except Exception as e:
        logger.error("Failed to reset settings: %s", e)
        return False
