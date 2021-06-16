import json
import os
from graph_representation.vivo.vivo import Vivo


class Component:

    """
        Наименование и графовое описание компонента согласия
        Также необходимость, но до сизх пор не использовалось
    """

    def __init__(self, name, vivo, necessity=True):
        self.name = name
        self.vivo = vivo
        self.necessity = necessity
    
    def __repr__(self):
        return "{0} \n {1}".format(self.name, self.vivo)

    @classmethod
    def read_components_from_directory(cls, directory):
        """Получение элементов согласия"""
        directory = directory
        json_file_names = os.listdir(directory)
        components = {}
        for json_file_name in json_file_names:
            json_file_full_address = directory + "/" + json_file_name
            # отбрасываем тип файла
            name = json_file_name.split(".")[0]
            component = cls.read_component_from_json(name, json_file_full_address)
            components[component.name] = component
        return components

    @classmethod
    def read_component_from_json(cls, json_file_name, json_file_address):
        with open(json_file_address, "r", encoding="utf-8") as read_file:
            json_object = json.load(read_file)
        vivo = Vivo.get_vivo_from_json_file(json_object["nodes"], json_object["relations"])
        return cls(json_file_name, vivo, necessity=True)

