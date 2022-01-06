import copy
import json
import os
from math import sqrt
from operator import attrgetter

from NLP.token_stage.personal_token import Token
from graph_representation.vivo.relation import Relation
from graph_representation.vivo.vertice import Vertice


class Vivo:

    def __init__(self, nodes=None, relations=None):
        if nodes == None and relations == None:
            self.nodes = {}
            self.relations = {}
            return
        elif nodes == None:
            self.relations = relations
            self.nodes = self._get_nodes_from_relations()
        elif relations == None:
            self.nodes = nodes
            self.relations = self._get_relations_from_nodes()
        else:
            self.nodes = nodes
            self.relations = relations

        self.normal_relations()




    def __add__(self, other):
        result = copy.deepcopy(self)
        for node_hash in other.nodes:
            node = other.nodes[node_hash]
            if not result.nodes.get(node_hash):
                result.nodes[node_hash] = node
        for relation_hash in other.relations:
            relation = other.relations[relation_hash]
            if relation.rating == 0:
                print("vivos" + str(45))
            if not result.relations.get(relation_hash):
                result.relations[relation_hash] = relation
            else:
                result.relations[relation_hash].rating = result.relations[relation_hash].rating + relation.rating
        result.normal_relations()
        return result

    def __sub__(self, other):
        result = copy.deepcopy(self)
        for relation_key in other.relations:
            relation = other.relations[relation_key]
            if result.relations.get(relation_key):
                result.relations[relation_key].rating = result.relations[relation_key].rating - relation.rating
                if result.relations[relation_key].rating <= 0:
                    result.relations.pop(relation_key)
        result.nodes = result._get_nodes_from_relations()
        result.normal_relations()
        return result

    def __contains__(self, item):
        if isinstance(item, str):
            if item.find("-"):
                return item in self.relations
            else:
                return item in self.nodes
        else:
            return None

    # Взаимодействия
    # ------------------------------------------------------------------------------------------------------------------

    def cut_other_vivo(self, other):
        result = copy.deepcopy(self)
        for relation_key in other.relations:
            if result.relations.get(relation_key):
                    result.relations.pop(relation_key)
        result.nodes = result._get_nodes_from_relations()
        result.normal_relations()
        return result

    def cut_repeat_nodes(self, other):
        """
        вырезать повторяющиеся узлы и связи
        """
        def get_relation_having_nodes(relations, nodes):
            new_relations = {}
            for relation_hash in relations:
                relation = self.relations[relation_hash]
                text1 = relation.text1
                text2 = relation.text2
                if all([nodes.get(hash(text1)), nodes.get(hash(text2))]):
                    new_relations[hash(relation.text)] = Relation(relation.text, relation.rating)
            return new_relations

        # собираем повторяющиеся узлы
        nodes = {}
        for node_hash in self.nodes:
            if other.nodes.get(node_hash):
                nodes[node_hash] = self.nodes[node_hash]
        #  переносим связи, имеющие повторяющиеся узлы
        self_relations = get_relation_having_nodes(self.relations, nodes)
        other_relations = get_relation_having_nodes(other.relations, nodes)
        relations = dict(list(self_relations.items()) + list(other_relations.items()))

        return Vivo(nodes.values(), relations.values())

    def intersection(self, other):
        joint_relations_keys = self.relations.keys() & other.relations.keys()
        joint_relations = {}
        for key in joint_relations_keys:
            average_rating = (self.relations[key].rating + other.relations[key].rating)/2
            joint_relations[key] = Relation(self.relations[key].text, rating=average_rating)
        joint_nodes = Vivo._get_nodes_from_relations(joint_relations.values())
        return Vivo(nodes=joint_nodes, relations=joint_relations.values())

    def substract_without_removing(self, other):
        """
        Вычитание без удаление отрицательных и нулевых файлов
        Потенциальная возможность отрицательных виво
        """
        result = copy.deepcopy(self)
        for relation_key in other.relations:
            relation = other.relations[relation_key]
            if result.relations.get(relation_key):
                result.relations[relation_key].rating = result.relations[relation_key].rating - relation.rating
        result.nodes = result._get_nodes_from_relations()
        result.normal_relations()
        return result

    def add(self, vivo, relevance):
        """
        В отличии от простого сложения
        учитывается оценка близости методов при объединении
        """
        rated_vivo = copy.deepcopy(vivo)
        for relation in rated_vivo.relations.values():
            relation.rating = relation.rating * relevance
        result =  self + rated_vivo
        self.nodes = result.nodes
        self.relations = result.relations

# Сравнение
# ----------------------------------------------------------------------------------------------------------------------

    def multiplication_compare(self, other):
        self_coincidence = self.part_of(other)
        other_coincidence = other.part_of(self)
        general_rating = sqrt(other_coincidence * self_coincidence)
        # general_rating = (other_coincidence + self_coincidence)/2
        return general_rating

    def sum_compare(self, other):
        self_coincidence = self.part_of(other)
        other_coincidence = other.part_of(self)
        # general_rating = sqrt(other_coincidence * self_coincidence)
        general_rating = (other_coincidence + self_coincidence)/2
        return general_rating

    def part_of(self, other):
        """
        self является частью other
        ноль получается при условии, что other не содержит ни одной связи self
        единица - если все связи self присутствуют в other
        """
        coincedence = float(0)
        for relation in self.relations.values():
            if other.relations.get(hash(relation.text)):
                coincedence += relation.rating
        return coincedence


# Анализ связей
# ----------------------------------------------------------------------------------------------------------------------

    # мониторинг связей
    # ------------------------------------------------------------------------------------------------------------------

    def _get_general_relation_rating(self):
        sum =0
        for relation in self.relations.values():
            sum += relation.rating
        return sum

    def check_empty_relations(self):
        for relation in self.relations.values():
            if relation.rating == 0:
                return True

    # редактирование связей
    # ------------------------------------------------------------------------------------------------------------------
    def remove_relation(self, relation_name):
        self.relations.pop(hash(relation_name))
        self.nodes = self._get_nodes_from_relations()
        self.normal_relations()

    def normal_relations(self):
        general_rating = 0

        for key in self.relations.keys():
            relation = self.relations[key]
            general_rating += relation.rating
        key_list = self.relations.keys()
        # tmp_vivo  = copy.deepcopy(self)
        for key in key_list:
            relation = self.relations[key]
            relation.rating = relation.rating / general_rating

    # фильтрация связей
    # ------------------------------------------------------------------------------------------------------------------

    def reduce_relation(self):
        # todo мне не нравится такое вычленение -  постепенно отказаться
        """
        уменьшение количества связей на основе среднего арифметического и подборного коэффициента
        """
        all_relation_rating = sum([relation.rating for relation in self.relations.values()])

        #  получаем среднее значение рейтинга связи
        average_relation_rating = all_relation_rating / self.relations.__len__()
        # какая-то магия
        # todo почему именно 20? нет логического обоснования подобранного коэффициента, убрать бы весь метод
        average_relation_rating = average_relation_rating / 20

        copy_relations = copy.deepcopy(self.relations)
        for key, relation in copy_relations.items():
            relation.rating = relation.rating - average_relation_rating
            if relation.rating <= 0:
                self.relations.pop(key)
        self.nodes = self._get_nodes_from_relations()
        self.normal_relations()

    def cut_relation_rating(self, min_rating=0):
        """
        Удаление связей, чей рейтинг ниже заявленного
        """
        copy_relations = copy.deepcopy(self.relations)
        for key, relation in copy_relations.items():
            if relation.rating <= min_rating:
                self.relations.pop(key)
        self.nodes = self._get_nodes_from_relations()
        self.normal_relations()

    def cut_relation_limit(self, relation_limit):

        relation_list = sorted((relation for relation in self.relations.values()), key=attrgetter("rating"))
        # переписываем связи
        max_element_number = min([relation_limit, len(relation_list)])
        relation_list = relation_list[:max_element_number]
        self.relations = dict([hash(relation.text), relation] for relation in relation_list)
        node_list = self._get_nodes_from_relations()
        self.nodes = dict([hash(node), node] for node in node_list)
        self.normal_relations()

    # перераспределение рейтинга
    # ------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def redistribute_relation_repeat_rating(vivos):
        # подсчет общего рейтинга связей

        # определяем для каждой свяхи список виво в которых она присутствует
        relation_repeats = {}
        for vivo in vivos:
            for key in vivo.relations:
                relation = vivo.relations[key]
                if not relation_repeats.get(key):
                    relation_repeats[key] = [vivo]
                    break

        # перераспределяем рейтинг
        # связь и так имеющая наибольший рейтинг увеличивает его
        # остальные связи уменьшаются
        # на 10% от среднего значения рейтинга связей в различных виво
        for relation_key in relation_repeats:
            closed_vivos = relation_repeats[relation_key]
            general_relation_rating = 0
            for vivo in closed_vivos:
                rating = vivo.relations[relation_key].rating
                general_relation_rating += rating
            average_rating = general_relation_rating/closed_vivos.__len__()
            relations = list([vivo.relations[relation_key] for vivo in closed_vivos])
            max_rating_relation = max(relations, key = attrgetter("rating"))
            #  умноженное на 2 т.к. потом будет вычитание в общем цикле
            max_rating_relation.rating +=  2*(0.1*average_rating)
            for vivo in closed_vivos:
                relation = vivo.relations[relation_key]
                relation.rating -= 0.1*average_rating
            for vivo in closed_vivos:
                relation = vivo.relations[relation_key]
                if relation.rating <= 0:
                    vivo.relations.pop(relation_key)
                vivo.nodes = vivo._get_nodes_from_relations()
                vivo.normal_relations()

    @staticmethod
    def reduce_relation_repeat(vivos):

        # неверный метод

        # подсчет общего рейтинга связей
        relation_repeats = {}
        for vivo in vivos:
            for key in vivo.relations:
                if not relation_repeats.get(key):
                    relation_repeats[key] = 1
                else:
                    relation_repeats[key] += 1
        # запись оценки новых связейв в рейтинг старых
        for vivo in vivos:
            for key in vivo.relations:
                relation = vivo.relations[key]
                new_rating = relation.rating / relation_repeats[key]
                relation.rating = new_rating


# Редактрование узлов
# ------------------------------------------------------------------------------------------------------------------

    # фильтрация узлов
    # ------------------------------------------------------------------------------------------------------------------
    def discard_nodes_over_limit(self, node_limit=50):
        if len(self.nodes) <= 50:
            return self.nodes
        """
        Удаляем все узлы, в которых связь с максимальным рейтингом ("прима узла") имеет меньший рейтинг в сравнении с
        "примами" остальных узлов.
        Отмечаем рейтнги последеней примы удаленного узла и вычищаем все связи с рейтингом ниже
        """

        if node_limit > len(self.nodes)-1:
            return

        #  собираем для каждого узла его связи
        vertices = []
        for node in self.nodes.values():
            relation_list = [relation for relation in self.relations.values() if relation.have_node(node)]
            vertices.append(Vertice(node, relation_list))

        # обрезаем вершингы до заданног количества - отмечаем рейтинг связи
        sorted_vertices = sorted(vertices, key=attrgetter("max_rating"), reverse=True)
        border_relation_rating = sorted_vertices[node_limit].max_rating
        limited_vertices = sorted_vertices[:node_limit]

        # определяем оставшиеся узлы
        limited_nodes = [vertice.node for vertice in limited_vertices]

        # определяем оставшиеся связи
        limited_relations = set()
        for vertice in limited_vertices:
            for relation in vertice.relations:
                if relation.rating > border_relation_rating:
                    limited_relations.add(relation)

        self.nodes = dict([hash(node), node] for node in limited_nodes)
        self.relations = dict([hash(relation.text), relation] for relation in limited_relations)
        self.normal_relations()

    def clear_punctuation_marks(self):
        punctuation_list = Token.punctuation_list
        tmp_relations = copy.deepcopy(self.relations)
        for index, relation in tmp_relations.items():
            if relation.text1 in punctuation_list or relation.text2 in punctuation_list:
                self.relations.pop(index)
        self.nodes = self._get_nodes_from_relations()
        self.normal_relations()

# Интерфейсы ввода и вывода
# ----------------------------------------------------------------------------------------------------------------------

    def write_to_file(self, file_address=""):
        data = {}
        nodes = [self.nodes[key] for key in self.nodes]
        relations = [{"node1": self.relations[key].text1, "node2": self.relations[key].text2,
                      "rating": self.relations[key].rating} for key in self.relations]
        data["nodes"] = nodes
        data["relations"] = relations
        with open(file_address, "w", encoding="utf-8") as write_file:
            json.dump(data, write_file, ensure_ascii=False)

    @staticmethod
    def read_vivo_from_direcory(directory):
        json_file_names = filter(lambda x: x.endswith('.json'), os.listdir(directory))
        vivos = {}
        for json_file_name in json_file_names:
            json_file_full_address = directory + "/" + json_file_name
            with open(json_file_full_address, "r", encoding="utf-8") as read_file:
                json_object = json.load(read_file)
            vivo = Vivo.get_vivo_from_json_file(json_object["nodes"], json_object["relations"])
            vivos[json_file_name] = vivo
        return vivos

    @classmethod
    def get_vivo_from_json_file(cls, node_list, relation_list):
        # define nodes
        nodes = {}
        for node in node_list:
            if not nodes.get(node):
                nodes[hash(node)] = node
        # define relations
        relations = {}
        for relation in relation_list:
            text1 = relation["node1"]
            text2 = relation["node2"]
            rating = relation["rating"]
            text = Relation.get_relation_text(text1, text2)
            relations[hash(text)] = Relation(text, rating=rating)
        return cls(nodes, relations)


# Соответствие компонентов
# ----------------------------------------------------------------------------------------------------------------------

    def _get_relations_from_nodes(self):
        # Получение связей
        relations = set()
        for node1 in self.nodes:
            for node2 in self.nodes:
                if node1 != node2:
                    text = Relation.get_relation_text(node1, node2)
                    relations.add(Relation(text, rating=1))
        return {hash(relation.text):relation for relation in relations}

    def _get_nodes_from_relations(self):
        nodes = set()
        for relation in self.relations.values():
            nodes.add(relation.text1)
            nodes.add(relation.text2)
        return {hash(node):node for node in nodes}

# ----------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    nodes = ["1", "2", "5", "3", "4", "6"]
    relation1 = Relation("1", "2", rating=1)
    relation2 = Relation("2", "3", rating=5)
    relation3 = Relation("4", "6", rating=3)
    relation4 = Relation("5", "2", rating=3)
    vivo = Vivo(nodes=nodes, relations=[relation1, relation2, relation3, relation4])
    vivo.discard_nodes_over_limit(3)