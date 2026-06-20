"""
Configuration loader for YAML and JSON files.
"""

import json
import yaml
from pathlib import Path
from typing import Dict, Any, Union

from .config import RAGConfig


class ConfigLoader:
    """Load RAG configurations from YAML or JSON files."""

    @staticmethod
    def load_yaml(filepath: Union[str, Path]) -> RAGConfig:
        """Load configuration from YAML file."""
        with open(filepath, 'r') as f:
            data = yaml.safe_load(f)
        return RAGConfig.from_dict(data)

    @staticmethod
    def load_json(filepath: Union[str, Path]) -> RAGConfig:
        """Load configuration from JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        return RAGConfig.from_dict(data)

    @staticmethod
    def load(filepath: Union[str, Path]) -> RAGConfig:
        """Load configuration from file (auto-detect format)."""
        filepath = Path(filepath)

        if filepath.suffix == '.yaml' or filepath.suffix == '.yml':
            return ConfigLoader.load_yaml(filepath)
        elif filepath.suffix == '.json':
            return ConfigLoader.load_json(filepath)
        else:
            raise ValueError(f"Unsupported format: {filepath.suffix}")

    @staticmethod
    def save_yaml(config: RAGConfig, filepath: Union[str, Path]) -> None:
        """Save configuration to YAML file."""
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w') as f:
            yaml.dump(config.to_dict(), f, default_flow_style=False)

    @staticmethod
    def save_json(config: RAGConfig, filepath: Union[str, Path]) -> None:
        """Save configuration to JSON file."""
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(config.to_dict(), f, indent=2)

    @staticmethod
    def save(config: RAGConfig, filepath: Union[str, Path]) -> None:
        """Save configuration to file (auto-detect format)."""
        filepath = Path(filepath)

        if filepath.suffix == '.yaml' or filepath.suffix == '.yml':
            ConfigLoader.save_yaml(config, filepath)
        elif filepath.suffix == '.json':
            ConfigLoader.save_json(config, filepath)
        else:
            raise ValueError(f"Unsupported format: {filepath.suffix}")
