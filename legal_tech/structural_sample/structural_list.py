import json
import os

from file_processing.file_processing import get_general_address
from legal_tech.structural_sample.gears.borders import Borders
from legal_tech.structural_sample.gears.order_categories import OrderedCategories

"""
Не знаю что это, но было бы неплохо просмотреть и, при необходимости вписать в обзую структуру
"""


def read_config_borders():
    borders = {}
    directory = "in\\global_borders"
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
        self.ordered_categories = []

    def add_element(self, category, num):
        new_ordered_component = OrderedCategories(category, num)
        try:
            new_category_index = self.ordered_categories.index(new_ordered_component)
            self.ordered_categories[new_category_index].add_num(num)
        except ValueError:
            self.ordered_categories.append(new_ordered_component)

    def check_one_component_possibility_order(self, category, category_num):

        #  собираем порядок в текущих ужу записанных элементах
        exist_left = []
        exist_right = []
        for ordered_component in self.ordered_categories:
            for num in ordered_component.nums:
                if num < category_num:
                    exist_left.append(ordered_component.name)
                elif num > category_num:
                    exist_right.append(ordered_component.name)
                elif num == category_num:
                    pass
                    # exist_left.append(ordered_component.name)
                    # exist_right.append(ordered_component.name)

        #  если хотя бы один из вариантов выбивается из общей структуры - ругаемся что низя
        for sample_left_category in self.borders[category].left:
            if sample_left_category == "start":
                continue
            if all([sample_left_category in exist_right]):
                return False
        for sample_right_category in self.borders[category].right:
            if sample_right_category == "end":
                continue
            if all([sample_right_category in exist_left]):
                return False
        return True

    @classmethod
    def check_two_component_orders(cls, category1, category2):
        """
        Проверяем моржет ли быть category 1 раньше category 2
        """
        if any([category1 in cls.borders[category2].right, category2 in cls.borders[category1].right]):
            return False
        return True


    @staticmethod
    def check_all_component_possibility_order(categories, sentence_nums):
        structural_list = StructuralList.get_structural_list(categories, sentence_nums)
        return structural_list.check_structural_list()


    @classmethod
    def get_structural_list(cls, categories, sentence_nums):
        structural_list = StructuralList()
        for category, sentence_num in zip(categories, sentence_nums):
            if sentence_num < 0:
                continue
            structural_list.add_element(category, sentence_num)
        return structural_list


    def check_structural_list(self):
        for ordered_category in self.ordered_categories:
            for num in ordered_category.nums:
                if not self.check_one_component_possibility_order(category=ordered_category.name,
                                                                  category_num=num):
                    return False
        return True

if __name__ == "__main__":
    structural_components = StructuralList()
    categories = ["name", "subject", "will", "purpose", "operator", "common_data", "data_action", "processing_method",
                  "time", "recall", "assign"]
    sentence_nums = list(range(11))

    categories[5] = "empty"
    sentence_nums[5] = -1

    struct_list = StructuralList.get_structural_list(categories, sentence_nums)
    print(struct_list.check_structural_list())

    # for num, category in enumerate(categories):
    #     if structural_components.check_one_component_possibility_order(category=category, category_num=num):
    #         structural_components.add_element(category, num)

    a = 90
