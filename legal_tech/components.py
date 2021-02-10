import copy
import json
import os
from collections import namedtuple
from operator import attrgetter

from file_processing.file_processing import get_general_address
from legal_tech.component_sentence import RelevantExcert, RatedSentence, ComponentSentence
from graph_representation.vivo import Vivo


class Component:

    def __init__(self, name, vivo):
        self.name = name
        self.vivo = vivo

    @staticmethod
    def normal_vivo_relations(components):
        #  нормализация каждого элемента
        vivos = [component.vivo for component in components]
        [Vivo.normal_relations(vivo) for vivo in vivos]
        #  обработка повторов в различных виво
        # Vivo.redistribute_relation_repeat_rating(vivos)
        # [Vivo.normal_relations(vivo) for vivo in vivos]

class AgreementComponent(Component):

    """
    Добавляется пункт - обязательный или вариативный блок
    """

    def __init__(self, name, vivo, necessity=True):
        super().__init__(name, vivo)
        self.necessity = necessity

    def __repr__(self):
        return self.name + self.vivo

    @staticmethod
    def read_agreement_samples(directory= "in/current_rules/json"):
        """Получение элементов согласия"""
        directory = get_general_address(directory)
        json_file_names = filter(lambda x: x.endswith('.json'), os.listdir(directory))
        sample_components = {}
        for json_file_name in json_file_names:
            json_file_full_address = directory + "/" + json_file_name
            with open(json_file_full_address, "r", encoding="utf-8") as read_file:
                json_object = json.load(read_file)
                vivo = Vivo.get_vivo_from_json_file(json_object["nodes"], json_object["relations"])
                sample_components[json_file_name] = AgreementComponent(json_file_name, vivo, necessity=True)
        return sample_components

class TextComponent(AgreementComponent):

    """
       добавляется максимальный рейтинг отрывка и его хэш
    """

    def __init__(self, name, vivo, necessity, rated_excerts):
        super().__init__(name, vivo, necessity)
        self.excerts = dict(rated_excerts)
        if self.excerts.__len__() > 0:
            self.max_rating_excert = self.__get_max_relevance_ecxert()
            self.max_rating_excert_hash = hash(self.max_rating_excert.sentence.text)
            if self.max_rating_excert_hash != 0:
                self.max_rating = self.excerts[self.max_rating_excert_hash].relevance
            else:
                self.max_rating = -1
                self.max_rating_excert_hash = -1


    def __repr__(self):
        if self.max_rating_excert_hash != 0:
            max_rating = self.excerts[self.max_rating_excert_hash].rating
            return self.name + " - " + str(max_rating)
        else:
            return self.name + " - " + str(0)

    def __get_max_relevance_ecxert(self):
        max_relevance = -1
        max_relevant_excert = None
        for sentence_hash in self.excerts:
            if self.excerts[sentence_hash].relevance > max_relevance:
                max_relevance = self.excerts[sentence_hash].relevance
                max_relevant_excert = self.excerts[sentence_hash]
        return max_relevant_excert


    @staticmethod
    def get_text_component(sample_component, text_object):
        sample_vivo = copy.deepcopy(sample_component.vivo)
        rated_sentences = {}
        for sentence in text_object.sentences.values():
            rated_sentences[hash(sentence.text)] = RatedSentence(sentence, sample_vivo)
        return TextComponent(sample_component.name, sample_vivo, sample_component.necessity, rated_sentences)

class ResultComponent(AgreementComponent):

    def __init__(self, name, vivo, necessity, excerts):
        super().__init__(name, vivo, necessity)
        # component_sentences = list(component_sentences)
        self.excerts = {}
        for excert in excerts:
            relevance = -1
            if hasattr(excert, "max_relevance"):
                relevance = excert.max_relevance
            elif hasattr(excert, "relevance"):
                relevance = excert.relevance
            relevant_excert = RelevantExcert(excert, vivo, relevance)
            self.excerts[hash(relevant_excert.sentence.text)] = relevant_excert

    def __str__(self):
        return self.name + " - " + self.excerts.__len__()

    def __repr__(self):
        return self.name

    def add_excerts(self, relevant_excert, relevant_component_vivo):
        if not hasattr(relevant_excert, "component_vivo"):
            relevant_excert = RelevantExcert(relevant_excert, relevant_component_vivo, relevant_excert.max_relevance)
        if not self.excerts.get(hash(relevant_excert.sentence.text)):
            self.excerts[hash(relevant_excert.sentence.text)] = relevant_excert
            self.vivo = self.vivo + relevant_component_vivo

    def delete_excert(self, sentence):
        for excert in self.excerts.values():
            # if hasattr(sentence, "sentence"):
            #     sentence = sentence.sentence
            text_hash = hash(sentence.text)
            if self.excerts.get(text_hash):
                self.vivo = self.vivo - excert.component_vivo
                self.excerts.pop(hash(sentence.text))
                break

    def filter_inconsistent_sentences(self):
        # гипотеза, что нельзя разорвать блок,
        # несколько предложений, относящихся к одному блоку
        # должны находится в тексте последовательно
        relevant_sentences = list(copy.copy(list(self.excerts.values())))
        relevant_sentences = sorted(relevant_sentences, key=lambda relevant_sentence: relevant_sentence.sentence.num)

        #  определяем самое релевантное предложение
        index_max_relevance_sentence = -1
        max_relevance_sentence = None
        max_relevance = -1
        for i in range(relevant_sentences.__len__()):
            sentence = relevant_sentences[i]
            if sentence.relevance > max_relevance:
                max_relevance = sentence.relevance
                max_relevance_sentence = sentence
                index_max_relevance_sentence = i
        num = max_relevance_sentence.sentence.num

        #  генерируем словарь предложений
        # проверяем смещение по тексту
        def collect_sentence_from_side(side):
            new_sentences = []
            #  Определяем напрвление проверки
            if side=="right":
                side = 1
            elif side=="left":
                side = -1

            sentence_index = index_max_relevance_sentence + side
            displacement = side
            while sentence_index > 0 and sentence_index < relevant_sentences.__len__():
                sentence = relevant_sentences[sentence_index].sentence
                if sentence.num == num + displacement:
                    new_sentences.append(relevant_sentences[sentence_index])
                    displacement += side
                    sentence_index += side
                else:
                    break
            return new_sentences

        new_sentences = [max_relevance_sentence]
        right_side_sentence = collect_sentence_from_side("right")
        left_side_sentence = collect_sentence_from_side("left")
        new_sentences.extend(right_side_sentence)
        new_sentences.extend(left_side_sentence)
        #  записываем полученные предложения в рассматриваемый компонент
        self.excerts = dict([hash(sentence.sentence.text), sentence] for sentence in new_sentences)

    @staticmethod
    def define_result_components(component_sentences, text_components):  # tuple, tuple
        """
        На основании рейтинга получение списка результирующих компонентов и принадлежщим им предложений
        ставится гипотеза что каждое предложение принадлежит какому либо компоненту
        все полетит в тартарары, если это будет не так
        """
        text_components = {component.name: component for component in text_components}

        #  работаем с копиями, т.к. изменяется vivo предложений и компонентов в процессе сравнения
        components = copy.deepcopy(text_components)
        sentences = copy.deepcopy(list(component_sentences))

        # свободные предложения - по ним определяется конец цикла, когда они заканчиваются
        free_sentences = set(component_sentence.sentence.text for component_sentence in copy.copy(sentences))
        # выделение результирующих компонент
        result_components = {}
        sentences = sorted(sentences, key=attrgetter('max_relevance'), reverse=True)
        while True:
            component_sentence = sentences[0]
            # перебор всех предложений
            if free_sentences.__len__()==0 or sentences[0].max_relevance==0:
                # шанс на раздел
                if component_sentence.max_relevance < 0.02:
                    break


            # уменьшаем количество свободных предложений
            if component_sentence.sentence.text in free_sentences:
                free_sentences.remove(component_sentence.sentence.text)

            max_rel_component_name = component_sentence.max_relevance_element_name
            relevant_component = components[max_rel_component_name]

            # print(max_rel_component_name + " " + str(component_sentence.max_relevance))
            # if max_rel_component_name=="subject.json":
            #     a=5

            #  Для записи берем оригинальные компоненты и предложения
            component_vivo = copy.deepcopy(text_components[max_rel_component_name].vivo)
            component_excert = copy.deepcopy(component_sentence)
            if not result_components.get(max_rel_component_name):
                result_component = ResultComponent(name=max_rel_component_name,
                                                   vivo=component_vivo,
                                                   necessity=True,
                                                   excerts=tuple([component_excert])
                                                   )
                result_components[max_rel_component_name] = result_component
            else:
                result_components[max_rel_component_name].add_excerts(component_excert, component_vivo)

            # перерасчет виво для компонента и предложения
            # из каждого предложенрия и компонента вырезается та часть. которая присутствует в другом
            # надеемся, что таким образом удалится одна из составных частей компонента и предложения
            # так как компонент может отображатьяс в тексте несколькими предложениями
            # и предложение можзет содержать несколько компонентов или их частей
            new_component_vivo = relevant_component.vivo.excise_vivo(component_sentence.vivo)
            component_sentence.vivo = component_sentence.vivo.excise_vivo(relevant_component.vivo)
            relevant_component.vivo = new_component_vivo

            # перепись релевантности
            # перепись релевантностей отставшейся части виво рассматриваемого предложения ко всем компонентам
            for current_component_name in component_sentence.component_relevance:
                new_relevance = component_sentence.vivo.sum_compare(components[current_component_name].vivo)
                component_sentence.component_relevance[current_component_name] = new_relevance
            # перпись релевантности предложений к отставшейся части виво рассматриваемого компонентпа
            for sentence in sentences:
                new_relevance = sentence.vivo.sum_compare(relevant_component.vivo)
                sentence.component_relevance[max_rel_component_name] = new_relevance

            # сортировка по новой максимальной релевантности
            # перечсет максимальной релевантности ко всем компонентам для всех предложений
            for component_sentence in sentences:
                component_sentence.max_relevance = 0
                component_sentence.define_max_relevance()
            # сортировка всех предложений на основе максимальной релевантности
            sentences = sorted(sentences, key=attrgetter('max_relevance'), reverse=True)

        return result_components


    @staticmethod
    def define_estimated_components(component_sentences, text_components):  # tuple, tuple
        """
        На основании рейтинга получение списка результирующих компонентов и принадлежщим им предложений
        определяется входимость компонента в предложение
        """
        text_components = {component.name: component for component in text_components}

        #  работаем с копиями, т.к. изменяется vivo предложений и компонентов в процессе сравнения
        components = copy.deepcopy(text_components)
        sentences = copy.deepcopy(list(component_sentences))

        # свободные предложения - по ним определяется конец цикла, когда они заканчиваются
        free_sentences = set(component_sentence.sentence.text for component_sentence in copy.copy(sentences))
        # выделение результирующих компонент
        result_components = {}
        sentences = sorted(sentences, key=attrgetter('max_relevance'), reverse=True)
        while True:
            component_sentence = sentences[0]
            # перебор всех предложений
            if free_sentences.__len__()==0 or sentences[0].max_relevance==0:
                # шанс на раздел
                if component_sentence.max_relevance < 0.02:
                    break


            # уменьшаем количество свободных предложений
            if component_sentence.sentence.text in free_sentences:
                free_sentences.remove(component_sentence.sentence.text)

            max_rel_component_name = component_sentence.max_relevance_element_name
            relevant_component = components[max_rel_component_name]

            # print(max_rel_component_name + " " + str(component_sentence.max_relevance))
            # if max_rel_component_name=="subject.json":
            #     a=5

            #  Для записи берем оригинальные компоненты и предложения
            component_vivo = copy.deepcopy(text_components[max_rel_component_name].vivo)
            component_excert = copy.deepcopy(component_sentence)
            if not result_components.get(max_rel_component_name):
                result_component = ResultComponent(name=max_rel_component_name,
                                                   vivo=component_vivo,
                                                   necessity=True,
                                                   excerts=tuple([component_excert])
                                                   )
                result_components[max_rel_component_name] = result_component
            else:
                result_components[max_rel_component_name].add_excerts(component_excert, component_vivo)

            # перерасчет виво для компонента и предложения
            # из каждого предложенрия и компонента вырезается та часть. которая присутствует в другом
            # надеемся, что таким образом удалится одна из составных частей компонента и предложения
            # так как компонент может отображатьяс в тексте несколькими предложениями
            # и предложение можзет содержать несколько компонентов или их частей
            new_component_vivo = relevant_component.vivo.excise_vivo(component_sentence.vivo)
            component_sentence.vivo = component_sentence.vivo.excise_vivo(relevant_component.vivo)
            relevant_component.vivo = new_component_vivo

            # перепись релевантности
            # перепись релевантностей отставшейся части виво рассматриваемого предложения ко всем компонентам
            for current_component_name in component_sentence.component_relevance:
                new_relevance = component_sentence.vivo.sum_compare(components[current_component_name].vivo)
                component_sentence.component_relevance[current_component_name] = new_relevance
            # перпись релевантности предложений к отставшейся части виво рассматриваемого компонентпа
            for sentence in sentences:
                new_relevance = sentence.vivo.sum_compare(relevant_component.vivo)
                sentence.component_relevance[max_rel_component_name] = new_relevance

            # сортировка по новой максимальной релевантности
            # перечсет максимальной релевантности ко всем компонентам для всех предложений
            for component_sentence in sentences:
                component_sentence.max_relevance = 0
                component_sentence.define_max_relevance()
            # сортировка всех предложений на основе максимальной релевантности
            sentences = sorted(sentences, key=attrgetter('max_relevance'), reverse=True)

        return result_components

    @staticmethod
    def define_other_result_component(existence_components, sample_components, component_sentences):
        other_components = {}
        win_sentences = {}
        sentence_components = {}
        Characteristic = namedtuple("Characteristic", "component_name rating sentence")

        for component_name in sample_components:
            win_sentence = None
            if not existence_components.get(component_name):
                max_sentence_rating = 0
                for sentence in component_sentences.values():
                    # перезапись рейтинга, каждый раз перезаписывать риейтинг уже обработанных предложений
                    # не целесообразно, поэтому рейтинг перасчитывается здесь
                    new_rating = sample_components[component_name].vivo.sum_compare(sentence.vivo)
                    if new_rating > max_sentence_rating:
                        max_sentence_rating = new_rating
                        win_sentence = sentence
                if not win_sentences.get(hash(win_sentence.text)):
                    characteristic = Characteristic(component_name=component_name, rating=max_sentence_rating,
                                                    sentence=win_sentence)
                    win_sentences[hash(win_sentence.text)] = characteristic
                else:
                    if win_sentences[hash(win_sentence.text)].rating < max_sentence_rating:
                        characteristic = Characteristic(component_name=component_name, rating=max_sentence_rating,
                                                        sentence=win_sentence)
                        win_sentences[hash(win_sentence.text)] = characteristic
        for win_sentence in win_sentences.values():
            component_name = win_sentence.component_name
            new_sentence = win_sentence.sentence
            sentence_vivo = new_sentence.vivo
            result_sentences = {hash(new_sentence.text): new_sentence}
            other_components[component_name] = ResultComponent(component_name, sentence_vivo, necessity=True,
                                                               excerts=result_sentences)
        return other_components

    @staticmethod
    def find_sentence_repeat(result_components, all_sentences):
        """
        поиск повторов предложений среди результирующих компонентов
        """
        result_components = dict([component.name, component] for component in result_components)
        probably_repeat_sentence_components = {}
        for component in result_components.values():
            for component_sentences in component.excerts.values():
                if not probably_repeat_sentence_components.get(hash(component_sentences.sentence.text)):
                    probably_repeat_sentence_components[hash(component_sentences.sentence.text)] = [component.name]
                else:
                    probably_repeat_sentence_components[hash(component_sentences.sentence.text)].append(component.name)

        repeat_component_sentence = {}
        for sentence_hash in probably_repeat_sentence_components:
            if probably_repeat_sentence_components[sentence_hash].__len__() > 1:
                components = {}
                for component in probably_repeat_sentence_components[sentence_hash]:
                    components[component] = (result_components[component])
                sentence = all_sentences[sentence_hash]
                if len(sentence.sentence.word_list) > 2:
                    repeat_component_sentence[sentence_hash] = ComponentSentence(all_sentences[sentence_hash], components.values())
                else:
                    a=9
        return repeat_component_sentence

class FinalComponent():
    def __init__(self, name, excert, relevance):
        self.name = name
        self.excert = excert
        self.relevance = relevance

    def __str__(self):
        return self.name + " " + str(self.relevance) + " " + self.excert
