import json
import os
from json import JSONEncoder


class MyJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set): 
            return list(obj) 
        return obj.__dict__

def read_json_directory(directory_address):
    """
    считывание json-ов из директории
    """
    file_names = os.listdir(directory_address)
    json_objects = []
    for file_name in file_names:
        file_address = "{0}\\{1}".format(directory_address, file_name)
        with open(file_address, "r", encoding="utf-8") as file:
            json_object = json.load(file)
            json_objects.append(json_object)
    return json_objects



