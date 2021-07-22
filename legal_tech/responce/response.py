import json

from file_processing.json_processing import MyJSONEncoder
from legal_tech.components.final_component import FinalComponent
from legal_tech.responce.found_component import FoundComponent
from legal_tech.responce.unfound_component import UnfoundComponent

description = dict()
description["name"] = "Наименование документа"
description["subject"] = "Субъет персональных данных"
description["will"] = "Волеизявление о представлении персональных данных"
description["purpose"] = "Цели обработки"
description["operator"] = "Описание оператора, кому передаются данные Цели обработки"
description["common_data"] = "Персонральные данные"
description["data_action"] = "Перечень действий с персональными данными"
description["processing_method"] = "Описание используемых оператором способов обработки персональных данных"
description["time"] = "Срок, в течении которого дейтсвует согласие"
description["recall"] = "Порядок отзыва согласия"
description["assign"] = "Подпись"
description["spokesman"] = "Представитель субъекта персональных данных"
description["third_person"] = "Третьи лица"

class Response:
    def __init__(self, text, found_components = None, unfound_components = None):
        self.text = text
        self.found_components = found_components
        self.unfound_components = unfound_components
        self.description = description

    @classmethod
    def get_json_responce_from_text(cls, text, final_components):
        """
        расчитываем и собираем json_responce
        """

        found_components = FoundComponent.get_from_final_components(text, final_components)

        unfound_components = UnfoundComponent.get_unfound_components(found_components)

        responce = Response(text, found_components, unfound_components)

        return responce

    @classmethod
    def get_from_result_components(cls, text, result_components):
        """
        расчитываем и собираем json_responce
        """

        found_components = FoundComponent.get_from_result_components(result_components)

        unfound_components = UnfoundComponent.get_unfound_components(found_components)

        responce = Response(text, found_components, unfound_components)

        return responce

    @classmethod
    def get_json_responce_from_sentences(cls, category_and_sentence_tuples, text):
        """
        расчитываем и собираем json_responce
        """

        found_components = FoundComponent.get_from_sentences(category_and_sentence_tuples)

        unfound_components = UnfoundComponent.get_unfound_components(found_components, last_text_index=len(text))

        responce = Response(text, found_components, unfound_components)

        return responce

    def write_json(self, address):
        with open(address, "w", encoding="utf-8") as json_file:
            json.dump(self, json_file, ensure_ascii=False, cls=MyJSONEncoder)


if __name__ == '__main__':

    text_address = "in\\agreements\\2\\clean_agreement"
    with open(text_address, "r", encoding="utf-8") as read_file:
        text = read_file.read()

    categpries_address = "in\\agreements\\2/categories/json_categories"
    with open(categpries_address, "r", encoding="utf-8") as file:
        components = json.load(file)

    final_components = dict()
    for name, excerts in components.items():
        final_components[name] =(FinalComponent(name, excerts))

    responce = Response.get_json_responce_from_text(text, final_components)
    with open("out\\2\\test_responce", "w", encoding="utf-8") as file:
        json.dump(responce, file, ensure_ascii=False, cls=MyJSONEncoder)