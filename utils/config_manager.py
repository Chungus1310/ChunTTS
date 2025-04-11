import json
import os

class ConfigManager:
    def __init__(self, config_file):
        self.config_file = config_file
        self.config = self._load_config()

    def _load_config(self):
        """Load configuration from JSON file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            else:
                # Return default config if file doesn't exist
                return {
                    "default_provider": "gtts",
                    "output_dir": "output",
                    "history_limit": 50,
                    "default_voice": "",
                    "default_rate": 1.0,
                    "default_pitch": 1.0,
                    "theme": "dark"
                }
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}

    def save_config(self):
        """Save current configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    def get(self, key, default=None):
        """Get a configuration value"""
        return self.config.get(key, default)

    def set(self, key, value):
        """Set a configuration value"""
        self.config[key] = value
        self.save_config()

    def update(self, updates):
        """Update multiple configuration values at once"""
        self.config.update(updates)
        self.save_config()
