"""Prompt management module for loading and caching prompts from JSON files."""

import json
import logging
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger("prompt_manager")

def load_prompts_from_file(file_path: Path) -> Dict[str, str]:
    """Load prompts from a single JSON file."""
    if not file_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {file_path}")
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            prompts = json.load(f)
        
        # Validate required keys
        required_keys = {"system", "user_template"}
        missing_keys = required_keys - set(prompts.keys())
        if missing_keys:
            raise ValueError(f"Missing required prompt keys: {missing_keys}")
        
        return prompts
    
    except json.JSONDecodeError as e:
        logger.error("Invalid JSON in %s: %s", file_path, e)
        raise ValueError(f"Invalid JSON in {file_path}: {e}") from e


def load_all_prompts(prompts_dir: str = "src/config/prompts") -> Dict[str, Dict[str, str]]:
    """Load all prompt files from the prompts directory."""
    prompts_path = Path(prompts_dir)
    if not prompts_path.exists():
        raise FileNotFoundError(f"Prompts directory not found: {prompts_path}")
    
    prompts_cache: Dict[str, Dict[str, str]] = {}
    
    for prompt_file in prompts_path.glob("*.json"):
        prompt_type = prompt_file.stem
        try:
            prompts_cache[prompt_type] = load_prompts_from_file(prompt_file)
            logger.info("Loaded prompts for type: %s", prompt_type)
        except (ValueError, FileNotFoundError) as e:
            logger.error("Failed to load prompts for %s: %s", prompt_type, e)
            raise
    
    return prompts_cache


def get_prompt(prompts_cache: Dict[str, Dict[str, str]], prompt_type: str, prompt_key: str) -> str:
    """Get a specific prompt from the cache."""
    if prompt_type not in prompts_cache:
        raise KeyError(f"Prompt type '{prompt_type}' not found")
    
    prompt = prompts_cache[prompt_type].get(prompt_key)
    if not prompt:
        raise KeyError(f"Prompt key '{prompt_key}' not found in type '{prompt_type}'")
    
    return prompt


def get_system_prompt(prompts_cache: Dict[str, Dict[str, str]], prompt_type: str) -> str:
    """Get system prompt for a specific type."""
    return get_prompt(prompts_cache, prompt_type, "system")


def get_user_template(prompts_cache: Dict[str, Dict[str, str]], prompt_type: str) -> str:
    """Get user template for a specific type."""
    return get_prompt(prompts_cache, prompt_type, "user_template")


def reload_prompts(prompts_dir: str = "src/config/prompts") -> Dict[str, Dict[str, str]]:
    """Reload all prompts from disk."""
    logger.info("Reloading prompts from %s", prompts_dir)
    return load_all_prompts(prompts_dir)


def validate_and_sanitize_input(user_input: str, max_length: int = 10000) -> str:
    """Validate and sanitize user input to prevent prompt injection attacks."""
    if not user_input:
        return ""
    
    # Check length
    if len(user_input) > max_length:
        logger.warning("User input too long, truncating: %d characters", len(user_input))
        user_input = user_input[:max_length]
    
    # Remove potentially dangerous patterns
    dangerous_patterns = [
        "ignore previous instructions",
        "ignore above instructions", 
        "forget everything above",
        "system prompt",
        "SYSTEM PROMPT",
        "act as",
        "pretend to be",
        "you are now",
        "new instructions:",
        "override:",
        "bypass",
        "ignore safety"
    ]
    
    sanitized_input = user_input
    for pattern in dangerous_patterns:
        if pattern.lower() in user_input.lower():
            logger.warning("Potentially dangerous pattern detected: %s", pattern)
            # Replace with safe alternative or remove
            sanitized_input = sanitized_input.replace(pattern, "[REDACTED]")
    
    return sanitized_input.strip()
