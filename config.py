"""Configuration management for Caesar cipher application."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict


class Config:
    """Manages application configuration with persistence."""

    DEFAULT_CONFIG = {
        "theme": "dark",
        "keep_case": True,
        "keep_punct": True,
        "auto_select_best": True,
        "show_all": False,
        "top_n": 50,
        "last_cipher": "Caesar",
        "input_mode": "ciphertext",
        "window_geometry": None,
    }

    def __init__(self):
        self.config_dir = Path.home() / ".caesar_cipher"
        self.config_file = self.config_dir / "config.json"
        self.config: Dict[str, Any] = self.DEFAULT_CONFIG.copy()
        self.load()

    def load(self) -> None:
        """Load configuration from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r") as f:
                    loaded = json.load(f)
                    self.config.update(loaded)
            except Exception as e:
                print(f"Failed to load config: {e}")

    def save(self) -> None:
        """Save configuration to file."""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, "w") as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Failed to save config: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set configuration value and save."""
        self.config[key] = value
        self.save()

    def reset(self) -> None:
        """Reset to default configuration."""
        self.config = self.DEFAULT_CONFIG.copy()
        self.save()
