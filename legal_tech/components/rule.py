import json
import os

from file_processing.file_processing import get_general_address
from graph_representation.vivo.vivo import Vivo
from legal_tech.components.component import Component


class Rule(Component):

    def __init__(self, name, vivo, necessity=True):
        Component.__init__(self, name, vivo, necessity)

    @classmethod
    def read_agreement_samples(cls, directory):
        """Получение элементов согласия"""
        directory = get_general_address(directory)
        json_file_names = filter(lambda x: x.endswith('.json'), os.listdir(directory))
        sample_components = {}
        for json_file_name in json_file_names:
            json_file_full_address = directory + "/" + json_file_name
            with open(json_file_full_address, "r", encoding="utf-8") as read_file:
                json_object = json.load(read_file)
                vivo = Vivo.get_vivo_from_json_file(json_object["nodes"], json_object["relations"])
                sample_components[json_file_name] = cls(json_file_name, vivo, necessity=True)
        return sample_components
    