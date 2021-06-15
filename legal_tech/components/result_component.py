import copy
from collections import namedtuple
from operator import attrgetter


from legal_tech.components.component import Component
from legal_tech.excerts.component_sentence import ComponentSentence
from legal_tech.excerts.relevant_excert import RelevantExcert
from legal_tech.structural_sample.structural_sample import StructuralList


class ResultComponent(Component):

    def __init__(self, name, vivo, excerts, necessity=True):
        Component.__init__(self, name, vivo, necessity)
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

    @classmethod
    def define_result_components(cls, component_sentences, text_components):  # tuple, tuple
        """
        На основании рейтинга получение списка результирующих компонентов и принадлежщим им предложений
        ставится гипотеза что каждое предложение принадлежит какому либо компоненту
        все полетит в тартарары, если это будет не так
        """
        text_components = {component.name: component for component in text_components}

        #  работаем с копиями, т.к. изменяется vivos предложений и компонентов в процессе сравнения
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
                result_component = cls(name=max_rel_component_name,
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
            new_component_vivo = relevant_component.vivo.cut_other_vivo(component_sentence.vivo)
            component_sentence.vivo = component_sentence.vivo.cut_other_vivo(relevant_component.vivo)
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
                result_component = cls(name=max_rel_component_name,
                                                   vivo=component_vivo,
                                                   necessity=True,
                                                   excerts=tuple([component_excert])
                                                   )
                estimated_components[max_rel_component_name] = result_component
            else:
                estimated_components[max_rel_component_name].add_excerts(component_excert, component_vivo)

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
                result_component = cls(name=max_rel_component_name, vivo=component_vivo,
                                       necessity=True, excerts=[component_sentence])
                result_components[max_rel_component_name] = result_component
            else:
                result_components[max_rel_component_name].add_excerts(component_sentence, component_vivo)

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
    def get_max_result_component(cls, text_components):  # tuple, tuple
        """
        Берем максимум для каждого элемента
        """
        result_components = []
        for text_component in text_components.values():
            max_relevance_excert = text_component.get_max_relevant_excert()
            result_component = cls(name=text_component.name, vivo=text_component.vivo, excerts= [max_relevance_excert] )
            result_components.append(result_component)
        return result_components

    def _get_max_relevant_excert(self):
        max_relevance_excert =  max((excert for excert in self.excerts), key=attrgetter("relevance"))
        return max_relevance_excert





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
        self.excerts = {hash(sentence.sentence.text):sentence for sentence in new_sentences}


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


