import json
from pathlib import Path


class DataManager:

    def __init__(self, data_directory):
        self.data_directory = Path(data_directory)

    def save_data(self, filename, data):
        file_path = self.data_directory / filename

        with open(file_path, "w") as file:
            json.dump(data, file, indent=4)

    def load_data(self, filename):
        file_path = self.data_directory / filename

        with open(file_path, "r") as file:
            return json.load(file)

    def save(self, filename, data):
        return self.save_data(filename, data)

    def load(self, filename):
        return self.load_data(filename)