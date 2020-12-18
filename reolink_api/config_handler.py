import io
import yaml
from typing import Optional, Dict


class ConfigHandler:
    camera_settings = {}

    @staticmethod
    def load() -> Optional[Dict]:
        try:
            stream = io.open("config.yml", 'r', encoding='utf8')
            data = yaml.safe_load(stream)
            return data
        except Exception as e:
            print("Config Property Error\n", e)
        return None
