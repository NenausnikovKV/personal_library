import copy
import json
import os
from math import sqrt
from operator import attrgetter

from NLP.token_stage.personal_token import Token
from file_processing.file_processing import get_general_address
from graph_representation.relation import Relation


class Vivo:

    def __init__(self, nodes=None, relations=None):
        if nodes == None and relations == None:
            self.nodes = {}
            self.relations = {}
            return
        elif nodes == None:
            nodes = Vivo.__get_nodes_from_relations(relations)
        elif relations == None:
            relations = self.__get_relations_from_nodes(nodes)
        self.nodes = dict([hash(node), node] for node in nodes)
        self.relations = dict([hash(relation.text), relation] for relation in relations)

    def __add__(self, other):
        result = copy.deepcopy(self)
        for node_hash in other.nodes:
            node = other.nodes[node_hash]
            if not result.nodes.get(node_hash):
                result.nodes[node_hash] = node
        for relation_hash in other.relations:
            relation = other.relations[relation_hash]
            if relation.rating == 0:
                print("vivo" + str(45))
            if not result.relations.get(relation_hash):
                result.relations[relation_hash] = relation
            else:
                result.relations[relation_hash].rating = result.relations[relation_hash].rating + relation.rating
        result.normal_relations()
        return result

    def excise_vivo(self, other):
        result = copy.deepcopy(self)
        for relation_key in other.relations:
            if result.relations.get(relation_key):
                    result.relations.pop(relation_key)
        result.nodes = result.extract_nodes_from_relations()
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
        result.nodes = result.extract_nodes_from_relations()
        result.normal_relations()
        return result

    def substract_without_removing(self, other):
        result = copy.deepcopy(self)
        for relation_key in other.relations:
            relation = other.relations[relation_key]
            if result.relations.get(relation_key):
                result.relations[relation_key].rating = result.relations[relation_key].rating - relation.rating
        result.nodes = result.extract_nodes_from_relations()
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

    def extract_nodes_from_relations(self):
        nodes = {}
        for key in self.relations:
            relation = self.relations[key]
            node1 = relation.text1
            node2 = relation.text2
            if not nodes.get(node1):
                nodes[hash(node1)] = node1
            if not nodes.get(node2):
                nodes[hash(node2)] = node2
        return nodes

    @staticmethod
    def __get_relations_from_nodes(nodes):
        # Получение связей
        relations = {}
        if nodes.__len__() == 1:
            node1 = nodes[0]
            plug = "[plug]"
            text = Relation.get_relation_text(node1, plug)
            relations[hash(text)] = Relation(text, rating=1)
        for node1 in nodes:
            for node2 in nodes:
                if node1 != node2:
                    text = Relation.get_relation_text(node1, node2)
                    relations[hash(text)] = Relation(text, rating=1)
        return list(relations.values())

    @staticmethod
    def __get_nodes_from_relations(relations):
        nodes = {}
        for relation in relations:
            node1 = relation.text1
            node2 = relation.text2
            if not nodes.get(hash(node1)):
                nodes[hash(node1)] = node1
            if not nodes.get(hash(node2)):
                nodes[hash(node2)] = node2
        return list(nodes.values())

    def remove_relation(self, index):
        self.relations.pop(index)
        self.nodes = self.extract_nodes_from_relations()
        self.normal_relations()

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

    def reduce_relation(self):
        all_relation_rating = 0
        for relation in self.relations.values():
            all_relation_rating += relation.rating
        average_relation_rating = all_relation_rating / (20 * self.relations.__len__())
        copy_relations = copy.deepcopy(self.relations)
        for key in copy_relations.keys():
            relation = self.relations[key]
            relation.rating = relation.rating - average_relation_rating
            if relation.rating <= 0:
                self.relations.pop(key)
        self.nodes = self.extract_nodes_from_relations()
        self.normal_relations()

    def clear_punctuation_marks(self):
        punctuation_list = Token.punctuation_list
        tmp_relations = copy.deepcopy(self.relations)
        for index, relation in tmp_relations.items():
            if relation.text1 in punctuation_list or relation.text2 in punctuation_list:
                self.relations.pop(index)
        self.nodes = self.extract_nodes_from_relations()
        self.normal_relations()


    def carve_vivo_part(self, other):
        """вырезать повторяющиеся узлы и связи"""
        result = copy.deepcopy(self)
        for node_hash in other.nodes:
            if result.nodes.get(node_hash):
                result.nodes.pop(node_hash)
        result.__clean_ecxcess_relations()
        return result

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

    def __clean_ecxcess_relations(self):
        new_relations = {}
        for relation in self.relations.values():
            text1 = relation.text1
            text2 = relation.text2
            if self.nodes.get(hash(text1)) and self.nodes.get(hash(text2)):
                new_relations[hash(relation.text)] = relation
        self.relations = new_relations

    def normal_relations(self):
        general_rating = 0

        for key in self.relations:
            relation = self.relations[key]
            general_rating += relation.rating
        key_list = self.relations.keys()
        # tmp_vivo  = copy.deepcopy(self)
        for key in key_list:
            relation = self.relations[key]
            relation.rating = relation.rating / general_rating



    def filter_relations(self):

        relation_list = list(self.relations.values())
        relation_list = sorted(relation_list, key=attrgetter('rating'), reverse=True)

        relation_list = [relation for relation in relation_list if relation.rating > pow(10, -10)]
        self.relations = dict([hash(relation.text), relation] for relation in relation_list)
        self.nodes = self.extract_nodes_from_relations()
        self.normal_relations()

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
                vivo.nodes = vivo.extract_nodes_from_relations()
                vivo.normal_relations()



    def check_empty_relations(self):
        for relation in self.relations.values():
            if relation.rating == 0:
                print("vivo 3")

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

    def union_part_of(self, other):
        """вырезать повторяющиеся узлы и связи"""
        # result = copy.deepcopy(self)
        nodes = {}

        for node_hash in self.nodes:
            if other.nodes.get(node_hash):
                nodes[node_hash] = self.nodes[node_hash]
        relations = {}
        for relation_hash in self.relations:
            relation = self.relations[relation_hash]
            text1 = relation.text1
            text2 = relation.text2
            if nodes.get(hash(text1)) and nodes.get(hash(text2)):
                relations[hash(relation.text)] = Relation(relation.text, relation.rating)
        return Vivo(tuple(nodes.values()), tuple(relations.values()))

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
    def get_text_vivo(text_object):
        all_relations = {}
        for sentence_hash in text_object.sentences:
            sentence = text_object.sentences[sentence_hash]
            word_texts = tuple([word.text for word in sentence.words.values()])
            vivo = Vivo(word_texts)
            for key in vivo.relations:
                relation = vivo.relations[key]
                if not all_relations.get(key):
                    all_relations[key] = Relation(relation.text, relation.rating)
                else:
                    all_relations[key].rating += relation.rating
        global_vivo = Vivo(relations=tuple(all_relations.values()))
        global_vivo.normal_relations()
        return global_vivo

    @staticmethod
    def get_vivo_from_json_file(node_list, relation_list):
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
        return Vivo(tuple(nodes.values()), tuple(relations.values()))

    @staticmethod
    def read_vivo(directory):
        json_file_names = filter(lambda x: x.endswith('.json'), os.listdir(directory))
        vivos = {}
        for json_file_name in json_file_names:
            json_file_full_address = directory + "/" + json_file_name
            with open(json_file_full_address, "r", encoding="utf-8") as read_file:
                json_object = json.load(read_file)
            vivo = Vivo.get_vivo_from_json_file(json_object["nodes"], json_object["relations"])
            vivos[json_file_name] = vivo
        return vivos