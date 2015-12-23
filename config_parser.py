import json
import os


class StudentWebConfig(object):

    def __init__(self, path=os.path.join(os.path.dirname(__file__), 'config.json')):
        self.path = path
        self.data = None
        self._read_config(path)

    def _read_config(self, path):
        try:
            with open(path) as raw_data:
                self.data = json.load(raw_data)
        except FileNotFoundError:
            print('You must create a config file in the project root')
            exit(0)

    def get_config(self):
        return self.data

