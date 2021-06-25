import json

from file_processing.json_processing import read_json_directory

comments = dict()
comments["name"] = "Согласие на обработку персональных данных"
comments["purpose"] = " Обработка персональных данных осуществляется в целях ___"
comments["time"] = "  Я даю согласие на обработку моих персональных данных в течение ___ лет "
comments["subject"] = "Я, ________ФИО________________________________________________________________ указываются данные заявителя  _____________________________ серия___________№_______________________ данные российского паспорта"
comments["will"] = " и даю согласие на их обработку свободно, своей волей и в своем интересе на обработку персональных данных"
comments["operator"] = "_______________, с местом нахождения по адресу: _____________________________ стр. 1 (далее – «Оператор персональных данных») "
comments["common_data"] = " согласие дается в отношении следующих персональных данных: фамилия, имя, отчество, дата рождения, данные документа, удостоверяющего личность, пол, семейный статус, адрес, номер контактного телефона, сведения о трудовой/учебной деятельности"
comments["data_action"] = "согласие дается на следующие действия с персональными данными: сбор, систематизация, накопление, хранение, уточнение (обновление, изменение), извлечение, использование, передача (предоставление, доступ), обезличивание, блокирование, удаление, уничтожение персональных данных "
comments["processing_method"] = "путем смешанной обработки персональных данных"
comments["recall"] = "согласие может быть отозвано путем направления письменного уведомления Оператору персональных данных"
comments["assign"] = "________________________(фамилия, имя, отчество полностью)  _________________(подпись) "


def read_static_data():
    input_ = dict()
    address = "in\\necessary_categories.json"
    with open(address, "r", encoding="utf-8") as file:
        necessary_categories = json.load(file)
    input_["necessary_categories"] = necessary_categories

    global_borders_address = "in\\global_borders"
    names, borders = (read_json_directory(global_borders_address))
    category_left_borders = dict()
    for name, border in zip(names, borders):
        category_left_borders[name] = border["left"]
    input_["category_left_borders"] = category_left_borders

    return input_


class UnfoundComponent:

    input_static_data = read_static_data()
    category_left_borders = input_static_data["category_left_borders"]
    necessary_categories = input_static_data["necessary_categories"]

    def __init__(self, component_name, index):
        self.component_name = component_name
        self.index = index
        self.text = comments[component_name]

    @classmethod
    def get_unfound_components(cls, found_components):

        unfound_components = []
        found_categories = [found_component.component_name for found_component in found_components]
        remaining_categories = [cat for cat in UnfoundComponent.necessary_categories if cat not in found_categories]

        for category in remaining_categories:
            start_index = UnfoundComponent._get_start_index(category, found_components)
            unfound_components.append(UnfoundComponent(component_name=category, index=start_index))
        return unfound_components

    @staticmethod
    def _get_start_index(category, found_components):
        if category == "name":
            start_index = 0
            return start_index
        else:
            left_found_components = UnfoundComponent._get_left_found_components(category, found_components)
            start_index = UnfoundComponent._find_last_components_end(left_found_components)
            return start_index


    @staticmethod
    def _find_last_components_end(left_found_components):
        last_components_end = -1
        for found_component in left_found_components:
            component_end = max(indices.stop_index for indices in found_component.indices)
            last_components_end = max(last_components_end, component_end)
        return last_components_end

    @staticmethod
    def _get_left_found_components(category, found_components):
        left_categories = UnfoundComponent.category_left_borders[category]
        left_found_components = []
        for found_component in found_components:
            if found_component.component_name in left_categories:
                left_found_components.append(found_component)
        return left_found_components



if __name__ == '__main__':

    name = "time"
    index = 126
    comment = "Действует со дня его подписания в течение 10 лет"
    unfound_component = UnfoundComponent(component_name = name, index=index)
