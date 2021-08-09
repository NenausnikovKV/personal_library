import copy
from collections import namedtuple, defaultdict
from operator import attrgetter

from legal_tech.components.component import Component
from legal_tech.components.rule import Rule
from legal_tech.excerts.rated_sentence import RatedSentence
from legal_tech.excerts.relevant_to_sentence_rules import RelevantRules
from legal_tech.excerts.vivo_sentence import VivoSentence

from legal_tech.structural_sample.structural_list import StructuralList


class ResultComponent(Rule):

    def __init__(self, name, rule, rated_sentences, necessity=True):

        self.name = name
        self.rule = rule
        self.relevant_sentences = {}
        for rated_sentence in rated_sentences:
            self.add_rated_sentence(rated_sentence)

    def __str__(self):
        return self.name + " - " + self.relevant_sentences.__len__()

    def __repr__(self):
        return self.name

    def check_sentence(self, sentence_text):
        return hash(sentence_text) in self.relevant_sentences

    def find_sentence(self, sentence_text):
        return self.relevant_sentences[hash(sentence_text)]

    def get_max_relevant_sentence(self):
        return max(self.relevant_sentences.values(), key=attrgetter('relevance'))

    def reduce_sentences(self):
        max_relevant_sentences = max(self.relevant_sentences.values(), key=attrgetter("relevance"))
        max_relevance = max_relevant_sentences.relevance
        threshold = max_relevance/3
        for sentence_hash, rated_sentence in copy.copy(self.relevant_sentences).items():
            if rated_sentence.relevance < threshold:
                self.relevant_sentences.pop(sentence_hash)


    @classmethod
    def compute_result_components(cls, relevant_to_sentences_rules):  # tuple, tuple

        """
            определяем компоненты по вхождению правила в предложение с выситанием правила из предложения
        """

        #  работаем с копиями, т.к. изменяется vivos предложений и компонентов в процессе сравнения
        relevant_to_sentences_rules = copy.deepcopy(relevant_to_sentences_rules)


        # свободные предложения - по ним определяется конец цикла, когда они заканчиваются
        copy_relevant_to_sentences_rules = copy.deepcopy(relevant_to_sentences_rules)
        free_sentence_texts = set(sentence.sentence.text for sentence in copy_relevant_to_sentences_rules.values())
        result_components = {}
        relevant_to_sentences_rules = sorted(relevant_to_sentences_rules.values(),
                                             key=attrgetter('max_relevance'),
                                             reverse=True)
        # выделение результирующих компонент
        while True:
            win_relevant_to_sentence_rule = relevant_to_sentences_rules[0]

            # точка выхода из цикла, потенциально перебор всех предложений
            if win_relevant_to_sentence_rule.max_relevance < 0.02:
                    break

            # уменьшаем количество свободных предложений
            if win_relevant_to_sentence_rule.sentence.text in free_sentence_texts:
                free_sentence_texts.remove(win_relevant_to_sentence_rule.sentence.text)



            max_relevant_rule = win_relevant_to_sentence_rule.max_relevance_rule

            win_rated_sentence = RatedSentence(sentence=copy.deepcopy(win_relevant_to_sentence_rule).sentence,
                                               rule_vivo=max_relevant_rule.vivo,
                                               relevance=max_relevant_rule.relevance)


            if max_relevant_rule.name not in result_components.keys():
                result_components[max_relevant_rule.name] = ResultComponent(max_relevant_rule.name,
                                                                            copy.deepcopy(max_relevant_rule),
                                                                            [win_rated_sentence])
            else:
                result_components[max_relevant_rule.name].add_rated_sentence(rated_sentence=win_rated_sentence,
                                                                             current_rule_vivo=max_relevant_rule.vivo)

            # вырезаем из виво предложения виво правила
            sentence_vivo = win_relevant_to_sentence_rule.vivo
            win_relevant_to_sentence_rule.vivo = sentence_vivo.cut_other_vivo(max_relevant_rule.vivo)

            # перепись релевантности
            # перепись релевантностей отставшейся части виво рассматриваемого предложения ко всем правилам
            for rule_name, rule in win_relevant_to_sentence_rule.rated_rules.items():
                new_relevance = rule.vivo.part_of(win_relevant_to_sentence_rule.vivo)
                win_relevant_to_sentence_rule.rated_rules[rule_name].relevance = new_relevance

            # перечсет максимальной релевантности ко всем компонентам для всех предложений
            for relevant_to_sentence_rules in relevant_to_sentences_rules:
                relevant_to_sentence_rules.max_relevance = 0
                relevant_to_sentence_rules.define_max_relevance()
            # сортировка всех предложений на основе максимальной релевантности
            relevant_to_sentences_rules = sorted(relevant_to_sentences_rules, key=attrgetter('max_relevance'), reverse=True)

        return result_components


    @classmethod
    def define_result_components(cls, relevant_to_rules_sentences, relevant_to_sentences_rules):  # tuple, tuple

        """
        На основании рейтинга получение списка результирующих компонентов и принадлежщим им предложений
        ставится гипотеза что каждое предложение принадлежит какому либо компоненту
        все полетит в тартарары, если это будет не так
        """

        #  работаем с копиями, т.к. изменяется vivos предложений и компонентов в процессе сравнения
        relevant_to_rules_sentences = copy.deepcopy(relevant_to_rules_sentences)
        relevant_to_sentences_rules = copy.deepcopy(relevant_to_sentences_rules)


        # свободные предложения - по ним определяется конец цикла, когда они заканчиваются
        copy_relevant_to_sentences_rules = copy.deepcopy(relevant_to_sentences_rules)
        free_sentence_texts = set(sentence.sentence.text for sentence in copy_relevant_to_sentences_rules.values())
        result_components = {}
        relevant_to_sentences_rules = sorted(relevant_to_sentences_rules.values(),
                                             key=attrgetter('max_relevance'),
                                             reverse=True)
        # выделение результирующих компонент
        while True:
            win_relevant_to_sentence_rules = relevant_to_sentences_rules[0]

            # точка выхода из цикла, потенциально перебор всех предложений
            if free_sentence_texts.__len__() == 0 and  win_relevant_to_sentence_rules.max_relevance < 0.02:
                    break

            # уменьшаем количество свободных предложений
            if win_relevant_to_sentence_rules.sentence.text in free_sentence_texts:
                free_sentence_texts.remove(win_relevant_to_sentence_rules.sentence.text)

            max_rel_rule_name = win_relevant_to_sentence_rules.max_relevance_rule_name
            max_relevant_rule = relevant_to_rules_sentences[max_rel_rule_name]


            #  Для записи берем оригинальные компоненты и предложения
            rule_vivo = copy.deepcopy(relevant_to_rules_sentences[max_rel_rule_name].rule_vivo)
            if max_rel_rule_name not in result_components.keys():
                result_components[max_rel_rule_name] = ResultComponent(max_rel_rule_name,
                                                           rule_vivo,
                                                           copy.deepcopy(win_relevant_to_sentence_rules)
                                                           )
            else:
                result_components[max_rel_rule_name].add_rated_sentence(copy.deepcopy(win_relevant_to_sentence_rules),
                                                                        current_rule_vivo=rule_vivo)

            # перерасчет виво
            max_relevant_rule.vivo = max_relevant_rule.vivo.cut_other_vivo(win_relevant_to_sentence_rules.vivo)
            sentence_vivo = win_relevant_to_sentence_rules.vivo
            rule_vivo = max_relevant_rule.rule_vivo
            win_relevant_to_sentence_rules.vivo = sentence_vivo.cut_other_vivo(rule_vivo)

            # перепись релевантности
            # перепись релевантностей отставшейся части виво рассматриваемого предложения ко всем компонентам
            for current_component_name in win_relevant_to_sentence_rules.component_relevance:
                new_relevance = win_relevant_to_sentence_rules.vivo.sum_compare(relevant_to_rules_sentences[current_component_name].vivo)
                win_relevant_to_sentence_rules.component_relevance[current_component_name] = new_relevance
            # перпись релевантности предложений к отставшейся части виво рассматриваемого компонентпа
            for sentence in relevant_to_sentences_rules:
                new_relevance = sentence.vivo.sum_compare(max_relevant_rule.vivo)
                sentence.component_relevance[max_rel_rule_name] = new_relevance

            # сортировка по новой максимальной релевантности
            # перечсет максимальной релевантности ко всем компонентам для всех предложений
            for win_relevant_to_sentence_rules in relevant_to_sentences_rules:
                win_relevant_to_sentence_rules.max_relevance = 0
                win_relevant_to_sentence_rules.define_max_relevance()
            # сортировка всех предложений на основе максимальной релевантности
            relevant_to_sentences_rules = sorted(relevant_to_sentences_rules, key=attrgetter('max_relevance'), reverse=True)

        return result_components

    @classmethod
    def define_estimated_components(cls, component_sentences, text_components):  # tuple, tuple
        # todo прописать заново для обработки результатов порядка в виде да и нет
        
        """
        На основании рейтинга получение списка результирующих компонентов и принадлежщим им предложений
        определяется входимость компонента в предложение
        """

        text_components = {component.name: component for component in text_components}

        #  работаем с копиями, т.к. изменяется vivos предложений и компонентов в процессе сравнения
        components = copy.deepcopy(text_components)
        sentences = copy.deepcopy(list(component_sentences))

        # свободные предложения - по ним определяется конец цикла, когда они заканчиваются
        free_sentences = set(component_sentence.sentence.text for component_sentence in copy.copy(sentences))
        # выделение результирующих компонент
        estimated_components = {}
        sentences = sorted(sentences, key=attrgetter('max_relevance'), reverse=True)
        while True:
            winning_sentence = sentences[0]

            #  точка выхода, если рассмотрены все предложения или близость ниже порога
            #  в теории порог можно не устанавливать
            if free_sentences.__len__()==0 or winning_sentence.max_relevance < 0.02:
                    break

            # счетчик по нерасмотренным предложениям
            if winning_sentence.sentence.text in free_sentences:
                free_sentences.remove(winning_sentence.sentence.text)

            #  работаем с самым релевантным к предложению компонентом
            max_rel_component_name = winning_sentence.max_relevance_element_name
            max_relevant_component = components[max_rel_component_name]

            #  Для записи берем оригинальные компоненты и предложения
            component_vivo = copy.deepcopy(text_components[max_rel_component_name].vivo)
            component_excert = copy.deepcopy(winning_sentence)
            if not estimated_components.get(max_rel_component_name):
                result_component = ResultComponent(name=max_rel_component_name,
                                                   vivo=component_vivo,
                                                   necessity=True,
                                                   excerts=tuple([component_excert])
                                                   )
                estimated_components[max_rel_component_name] = result_component
            else:
                estimated_components[max_rel_component_name].add_rated_sentence(component_excert, component_vivo)

            # перерасчет виво для компонента и предложения
            # из каждого предложенрия и компонента вырезается та часть. которая присутствует в другом
            # надеемся, что таким образом удалится одна из составных частей компонента и предложения
            # так как компонент может отображатьяс в тексте несколькими предложениями
            # и предложение можзет содержать несколько компонентов или их частей
            # вырезается только общая часть
            vivo_intersection = max_relevant_component.vivo.intersection(winning_sentence.vivo)
            new_component_vivo = max_relevant_component.vivo.cut_other_vivo(vivo_intersection)
            winning_sentence.vivo = winning_sentence.vivo.cut_other_vivo(vivo_intersection)
            max_relevant_component.vivo = new_component_vivo

            # перепись релевантности
            # перепись релевантностей отставшейся части виво рассматриваемого предложения ко всем компонентам
            for current_component_name in winning_sentence.component_relevance:
                new_relevance = winning_sentence.vivo.part_of(components[current_component_name].vivo)
                winning_sentence.component_relevance[current_component_name] = new_relevance

            # перпись релевантности предложений к отставшейся части виво рассматриваемого компонентпа
            for sentence in sentences:
                new_relevance = sentence.vivo.part_of(max_relevant_component.vivo)
                sentence.component_relevance[max_rel_component_name] = new_relevance

            # сортировка по новой максимальной релевантности
            # перечсет максимальной релевантности ко всем компонентам для всех предложений
            for winning_sentence in sentences:
                winning_sentence.max_relevance = 0
                winning_sentence.define_max_relevance()
            # сортировка всех предложений на основе максимальной релевантности
            sentences = sorted(sentences, key=attrgetter('max_relevance'), reverse=True)

        return estimated_components

    @classmethod
    def collate_sentences_and_components(cls, component_sentence_list, rule_components, threshold=0.1):  # tuple, tuple

        """
        На основании рейтинга получение списка результирующих компонентов и принадлежщим им предложений
        определяется входимость компонента в предложение
        """

        #  работаем с копиями, т.к. изменяется vivos предложений и компонентов в процессе сравнения
        components = copy.deepcopy(rule_components)
        sentences = copy.deepcopy(list(component_sentence_list))

        # свободные предложения - по ним определяется конец цикла, когда они заканчиваются
        free_sentences = set(component_sentence.sentence.text for component_sentence in copy.copy(sentences))
        # выделение результирующих компонент
        result_components = {}
        structural_components = StructuralList()
        sentences = sorted(sentences, key=attrgetter('max_relevance'), reverse=True)
        while True:
            winning_sentence = sentences[0]

            #  в теории порог можно не устанавливать
            if winning_sentence.max_relevance < threshold:
                break

            #  точка выхода, если рассмотрены все предложения
            #  необходимо учитывать случай, когда последнее предложение сожержит несколько компонентов, поэтому недльзя раньше времени выходить
            # if free_sentences.__len__() == 0:
            #     break

            #  работаем с самым релевантным к предложению компонентом
            max_rel_component_name = winning_sentence.max_relevance_element_name
            max_relevant_component = components[max_rel_component_name]

            # если соответствует структурному положению
            # if structural_components.check_one_component_possibility_order(category=max_rel_component_name, category_num=winning_sentence.sentence.num):
            # if (True):
                # счетчик по нерасмотренным предложениям

            if winning_sentence.sentence.text in free_sentences:
                free_sentences.remove(winning_sentence.sentence.text)

            #  Для записи берем оригинальные компоненты и предложения
            component_vivo = copy.deepcopy(rule_components[max_rel_component_name].vivo)
            # todo осторожно, не смотря на заявление берется не оригинал предложения, а копия возможно отредактированного
            component_sentence = copy.deepcopy(winning_sentence)
            if not result_components.get(max_rel_component_name):
                result_component = ResultComponent(name=max_rel_component_name, vivo=component_vivo,
                                       necessity=True, excerts=[component_sentence])
                result_components[max_rel_component_name] = result_component
            else:
                result_components[max_rel_component_name].add_rated_sentence(component_sentence, component_vivo)

            # пополняем структурные элементы
            # structural_components.add_element(max_rel_component_name, winning_sentence.sentence.num)

            # убираем из предложения vivos близкого компонента
            # winning_sentence.vivos = winning_sentence.vivos - vivo_intersection
            winning_sentence.vivo = winning_sentence.vivo.cut_other_vivo(max_relevant_component.vivo)

            # перепись релевантности
            # перепись релевантностей виво  отставшейся части рассматриваемого предложения ко всем компонентам
            for current_component_name in winning_sentence.component_relevance:
                new_relevance = components[current_component_name].vivo.part_of(winning_sentence.vivo)
                winning_sentence.component_relevance[current_component_name] = new_relevance

            # else:
                # так как решиили, что vivos остаются статичны в процессе обработки, то ручное обнуление
                # релевантности предложения к данному компоненту не будет переписано при обработке (нет итерационной переписи)
                # поэтому можем просто обнулить этот рейтинг как несостояшийся
                # todo при смене парадигмы на нечеткое ограничение по структуре не забыть убрать весь блок
                # winning_sentence.component_relevance[winning_sentence.max_relevance_element_name] = 0
                # pass

            # сортировка по новой максимальной релевантности
            # перечсет максимальной релевантности ко всем компонентам для всех предложений
            for sentence in sentences:
                sentence.max_relevance = 0
                sentence.define_max_relevance()

            # сортировка всех предложений на основе максимальной релевантности
            sentences = sorted(sentences, key=attrgetter('max_relevance'), reverse=True)

        return result_components

    @classmethod
    def get_max_relevant_components(cls, relevant_to_rules_sentences):  # tuple, tuple
        """
        Берем предложение с максимальным рейтингом для каждого праивла
        """


        result_components = dict()
        for rule_name, rule_sentences in relevant_to_rules_sentences.items():
            max_relevance_sentence = rule_sentences.get_max_relevant_sentence()

            result_component = ResultComponent(name=rule_name,
                                   rule=rule_sentences.rule,
                                   rated_sentences=[max_relevance_sentence])

            result_components[rule_name] = result_component

        return result_components

    def _get_max_relevant_excert(self):
        max_relevance_excert =  max((excert for excert in self.relevant_sentences), key=attrgetter("relevance"))
        return max_relevance_excert

    # ------------------------------------------------------------------------------------------------------------------
    def add_rated_sentence(self, rated_sentence, current_rule_vivo=None):
        self.relevant_sentences[hash(rated_sentence.sentence.text)] = rated_sentence

    def delete_excert(self, sentence):
        for excert in self.relevant_sentences.values():
            # if hasattr(sentence, "sentence"):
            #     sentence = sentence.sentence
            text_hash = hash(sentence.text)
            if self.relevant_sentences.get(text_hash):
                self.vivo = self.vivo - excert.component_vivo
                self.relevant_sentences.pop(hash(sentence.text))
                break

    def filter_inconsistent_sentences(self):
        # гипотеза, что нельзя разорвать блок,
        # несколько предложений, относящихся к одному блоку
        # должны находится в тексте последовательно
        relevant_sentences = list(copy.copy(list(self.relevant_sentences.values())))
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
            while all([sentence_index > 0, sentence_index < relevant_sentences.__len__()]):
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
        self.relevant_sentences = {hash(sentence.sentence.text):sentence for sentence in new_sentences}

    @staticmethod
    def find_sentence_repeat(probably_components, all_sentences):
        """
        поиск повторов предложений среди результирующих компонентов
        """
        sentence_component_names = defaultdict(list)
        all_sentences = dict()
        for category, component in probably_components.items():
            for rated_sentence in component.rated_sentences.values():
                sentence_hash = hash(rated_sentence.sentence.text)
                sentence_component_names[sentence_hash].append(category)
                all_sentences[sentence_hash] = VivoSentence(rated_sentence.sentence, rated_sentence.vivo)

        repeat_component_sentence = {}
        for sentence_hash, category in sentence_component_names.items():
            if sentence_component_names[sentence_hash].__len__() > 1:
                components = {}
                for component_name in sentence_component_names[sentence_hash]:
                    components[component_name] = probably_components[component_name]
                vivo_sentence = all_sentences[sentence_hash]
                if len(vivo_sentence.sentence.word_list) > 2:
                    repeat_component_sentence[sentence_hash] = RelevantRules(vivo_sentence, components.values())

        return repeat_component_sentence
    # ------------------------------------------------------------------------------------------------------------------

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
                                                               rated_sentences=result_sentences)
        return other_components



