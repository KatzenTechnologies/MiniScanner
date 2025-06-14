import json
import marshal
import os

class ConfigurationTypes:
    MARSHAL = "MARSHAL"
    JSON = "JSON"

class Configuration:
    def save(self):
        # Да, я знаю что есть match, но он медленный(
        if self.type_of_config == ConfigurationTypes.MARSHAL:
            file = open(self.path, "wb")
            marshal.dump(self.data, file)
        elif self.type_of_config == ConfigurationTypes.JSON:
            file = open(self.path, "w")
            json.dump(self.data, file)
        file.close()

    def _read(self):
        if self.type_of_config == ConfigurationTypes.MARSHAL:
            file = open(self.path, "rb")
            self.data = marshal.load(file)
        elif self.type_of_config == ConfigurationTypes.JSON:
            file = open(self.path, "r")
            self.data = json.load(file)
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