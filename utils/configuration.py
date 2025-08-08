import json
import marshal
import os
import yaml
import toml
import msgpack

class ConfigurationTypes:
    JSON = "JSON"
    YAML = "YAML"
    TOML = "TOML"
    MSGPACK = "MSGPACK"

class Configuration:
    def save(self):
        # Да, я знаю что есть match, но он медленный(
        if self.type_of_config == ConfigurationTypes.JSON:
            file = open(self.path, "w", encoding='utf-8')
            json.dump(self.data, file)
        elif self.type_of_config == ConfigurationTypes.YAML:
            file = open(self.path, "w")
            yaml.dump(self.data, file)
        elif self.type_of_config == ConfigurationTypes.TOML:
            file = open(self.path, "w")
            toml.dump(self.data, file)
        elif self.type_of_config == ConfigurationTypes.MSGPACK:
            file = open(self.path, "wb")
            msgpack.dump(self.data, file)
        file.close()

    def _read(self):
        if self.type_of_config == ConfigurationTypes.JSON:
            file = open(self.path, "r", encoding='utf-8')
            self.data = json.load(file)
        elif self.type_of_config == ConfigurationTypes.YAML:
            file = open(self.path, "r")
            self.data = yaml.safe_load(file)
        elif self.type_of_config == ConfigurationTypes.TOML:
            file = open(self.path, "r")
            self.data = toml.load(file)
        elif self.type_of_config == ConfigurationTypes.MSGPACK:
            file = open(self.path, "rb")
            self.data = msgpack.load(file)

        file.close()

    def __init__(self, path, type_of_config=ConfigurationTypes.JSON):
        self.data = None
        self.path = path
        self.type_of_config = type_of_config

        if os.path.exists(path) and os.path.isfile(path):
            self._read()

    def __getitem__(self, item):
        return self.data.get(item)

    def __setitem__(self, key, value):
        self.data[key] = value

    def get_data(self):
        return self.data
    def get(self, item, not_found=None):
        return self.data.get(item, not_found)
