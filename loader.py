#!/usr/bin/env python3
"""
Configuration Loader Utility

Loads application configuration from YAML files based on the specified environment.
"""

import yaml
from pathlib import Path
import os

def load_config(env: str = "development") -> dict:
    """
    Loads configuration files, merging a base configuration with an
    environment-specific one.

    Args:
        env: The environment to load ('development', 'staging', 'production').

    Returns:
        A dictionary containing the merged configuration.
    """
    config_dir = Path(__file__).parent
    base_config_path = config_dir / "app_config.yaml"
    env_config_path = config_dir / "environment" / f"{env}.yaml"

    config = {}

    # Load base configuration
    if base_config_path.exists():
        with open(base_config_path, 'r') as f:
            config.update(yaml.safe_load(f))
    else:
        print(f"Warning: Base config file not found at {base_config_path}")

    # Load and merge environment-specific configuration
    if env_config_path.exists():
        with open(env_config_path, 'r') as f:
            env_config = yaml.safe_load(f)
            # Deep merge env_config into config
            for key, value in env_config.items():
                if isinstance(value, dict) and isinstance(config.get(key), dict):
                    config[key].update(value)
                else:
                    config[key] = value
    else:
        print(f"Warning: Environment config file not found for '{env}' at {env_config_path}")

    # Override with environment variables for sensitive data
    # Example: CHATBOT_API_KEY
    for key, value in config.items():
        env_var = f"CHATBOT_{key.upper()}"
        if env_var in os.environ:
            config[key] = os.environ[env_var]

    return config