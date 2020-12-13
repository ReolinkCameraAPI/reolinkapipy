import io
import yaml


class ConfigHandler:
    camera_settings = {}

    @staticmethod
    def load() -> yaml or None:
        try:
            stream = io.open("config.yml", 'r', encoding='utf8')
            data = yaml.safe_load(stream)
            return data
        except Exception as e:
            print("Config Property Error\n", e)
        return None
