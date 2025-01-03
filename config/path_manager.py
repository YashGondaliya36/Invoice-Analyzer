import yaml
from pathlib import Path

"""
A singleton class PathManager that loads file paths from a config.yaml file 
by changing in config.yaml it changes the path in whole code
"""

class PathManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PathManager, cls).__new__(cls)
            cls._instance._load_paths()
        return cls._instance

    def _load_paths(self):
        config_path = Path(__file__).parent / 'config.yaml'
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        self.paths = {k: v for k, v in config['paths'].items()}

    def get(self, key):
        return self.paths.get(key)

    def __getattr__(self, key):
        return self.get(key)


path_manager = PathManager()