"""
Configuration utility module for loading and managing application settings.
"""

import os
from pathlib import Path
from typing import Dict
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

class ConfigurationError(Exception):
    """Custom exception for configuration-related errors."""
    pass

class Config:
    """Configuration manager for the application."""
    
    def __init__(self, env_path: str = None):
        """
        Initialize configuration manager.
        
        Args:
            env_path (str, optional): Path to .env file. If not provided,
                                    will look in project root directory.
        """
        self._config = {}
        self._load_env(env_path)
        self._validate_config()

    def _load_env(self, env_path: str = None) -> None:
        """
        Load environment variables from .env file.
        
        Args:
            env_path (str, optional): Path to .env file.
        
        Raises:
            ConfigurationError: If .env file cannot be found or loaded.
        """
        try:
            if env_path is None:
                # Find the project root directory
                project_root = Path(__file__).parent.parent
                env_path = project_root / '.env'
                env_template_path = project_root / '.env.template'

            if not os.path.exists(env_path):
                if os.path.exists(env_template_path):
                    # If .env doesn't exist but template does, guide the user
                    raise ConfigurationError(
                        "No .env file found! Please:\n"
                        "1. Rename .env.template to .env\n"
                        "2. Edit .env and add your Google Maps API key"
                    )
                else:
                    # No .env or template found
                    raise ConfigurationError(
                        "No .env file found! Please create a .env file with your Google Maps API key:\n"
                        "GOOGLE_MAPS_API_KEY=your_api_key_here"
                    )
            # Check if .env file exists
            # if not os.path.exists(env_path):
            #     raise ConfigurationError(f".env file not found at {env_path}")

            # Load environment variables from .env file
            load_dotenv(env_path)
            
            # Store configuration values
            self._config = {
                'google_maps_api_key': os.getenv('GOOGLE_MAPS_API_KEY'),
                'log_level': os.getenv('LOG_LEVEL', 'INFO'),
                'max_retries': int(os.getenv('MAX_RETRIES', '3')),
                'timeout': int(os.getenv('TIMEOUT', '10')),
            }
            
            logger.debug("Environment variables loaded successfully")
            
        except Exception as e:
            raise ConfigurationError(f"Error loading environment variables: {str(e)}")

    def _validate_config(self) -> None:
        """
        Validate required configuration values.
        
        Raises:
            ConfigurationError: If any required configuration is missing or invalid.
        """
        # Check for required configurations
        if not self._config.get('google_maps_api_key'):
            raise ConfigurationError(
                "Google Maps API key is required. "
                "Please set GOOGLE_MAPS_API_KEY in .env file"
            )

        # Validate numeric values
        try:
            if not isinstance(self._config['max_retries'], int) or self._config['max_retries'] < 1:
                raise ConfigurationError("MAX_RETRIES must be a positive integer")
            
            if not isinstance(self._config['timeout'], int) or self._config['timeout'] < 1:
                raise ConfigurationError("TIMEOUT must be a positive integer")
        except (ValueError, TypeError) as e:
            raise ConfigurationError(f"Invalid configuration value: {str(e)}")

    def get(self, key: str, default=None) -> any:
        """
        Get configuration value.
        
        Args:
            key (str): Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value or default if not found
        """
        return self._config.get(key, default)

    def get_all(self) -> Dict:
        """
        Get all configuration values.
        
        Returns:
            Dict: Dictionary containing all configuration values
        """
        return self._config.copy()

# Create a singleton instance
config = Config()

def get_config() -> Config:
    """
    Get configuration instance.
    
    Returns:
        Config: Singleton configuration instance
    """
    return config