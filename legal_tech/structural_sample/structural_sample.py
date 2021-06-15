import json
import os
from operator import itemgetter

from file_processing.file_processing import get_general_address
from source.test_model.structural_sample.gears.borders import Borders
from source.test_model.structural_sample.gears.order_component import OrderedComponent

"""
Не знаю что это, но было бы неплохо просмотреть и, при необходимости вписать в обзую структуру
"""

def read_config_borders():
    borders = {}
    directory = get_general_address("in\\global_borders")
    files = os.listdir(directory)
    for file_name in files:
        file_address = "{0}\\{1}".format(directory, file_name)
        category = file_name
        with open(file_address, "r", encoding='utf-8') as file:
            json_data = json.load(file)
            category_global_border = Borders(left_categories=json_data["left"], right_categories=json_data["right"])
            borders[category] = category_global_border
    return borders


class StructuralList:

    # для каждого компонента представлены глобальные границы слева и справа (dict)
    borders = read_config_borders()

    def __init__(self, ):
        self.ordered_components = []



    def add_element(self, category, num):
        if not self.check_one_component_possibility_order(category=category, category_num=num):
            return False

        new_ordered_component = OrderedComponent(category, num)
        # это в конце добавление до финальной формы
        for component in self.ordered_components:
            if component.name == new_ordered_component:
                component.add.num()
                return True
        self.ordered_components.append(new_ordered_component)
        return True



    def check_one_component_possibility_order(self, category, category_num):

        #  собираем порядок в текущих ужу записанных элементах
        exist_left = []
        exist_right = []
        for ordered_component in self.ordered_components:
            for num in ordered_component.nums:
                if num < category_num: exist_left.append(ordered_component.name)
                elif num < category_num: exist_right.append(ordered_component.name)
                elif num == category_num:
                    exist_left.append(ordered_component.name)
                    exist_right.append(ordered_component.name)

        #  если хотя бы один из вариантов выбивается из общей структуры - ругаемся что низя
        for sample_left_category in StructuralList.borders[category].left:
            if all([sample_left_category not in exist_left, sample_left_category in exist_right]):
                return False
        for sample_right_category in self.borders[category].right:
            if all([sample_right_category not in exist_right, sample_right_category in exist_left]):
                return False
        return True


    @staticmethod
    def check_all_component_possibility_order(categories, sentence_nums):
        structural_list = StructuralList()
        for category, num in zip(categories, sentence_nums):
            structural_list.add_element(category, num)
        for category, num in zip(categories, sentence_nums):
            if not structural_list.check_one_component_possibility_order(category=category, category_num=num):
                return False
        return True

    @classmethod
    def check_two_component_orders(cls, category1, category2):
        """
        Проверяем моржет ли быть category 1 раньше category 2
        """
        if any ([category1 in cls.borders[category2].right, category2 in cls.borders[category1].right]):
             return False
        return True

if __name__=="__main__":
    structural_components = StructuralList()
    categories = ["name", "subject", "will", "purpose", "operator", "common_data", "data_action", "processing_method",
                "time", "recall", "assign"]
    for num, category in enumerate(categories):
        if structural_components.check_one_component_possibility_order(category=category, category_num=num):
           structural_components.add_element(category, num)
    a=90

