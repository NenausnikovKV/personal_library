import copy

from graph_representation.vivo import Vivo


class VivoSentence():
    """
    предложение и его граф
    """

    def __init__(self, sentence=None, vivo=None):
        self.vivo = vivo
        self.sentence = sentence

    def __add__(self, other):
        result = copy.deepcopy(self)
        result.vivo = self.vivo + other.vivo
        result.sentence = self.sentence + other.sentence
        return result

    def __repr__(self):
        return self.sentence.text

    def normal(self):
        self.vivo.normal_relations()

    def compare(self, other):
        return self.vivo.multiplication_compare(other.vivo)

    @staticmethod
    def build_sentence_vivo(sentence):
        word_texts = tuple([word.text for word in sentence.words.values()])
        vivo = Vivo(nodes=word_texts)
        vivo.normal_relations()
        return vivo

    @staticmethod
    def init(sentence):
        vivo = VivoSentence.build_sentence_vivo(sentence)
        return VivoSentence(sentence, vivo)


class RatedSentence(VivoSentence):
    """ Предложение, его виво-представление и их рейтинги """

    def __init__(self, sentence, component_vivo):
        # sentence_vivo = get_sentence_vivo(sentence, segmenter, morph_tagger, syntax_parser)
        # vivo = VivoSentence.build_sentence_vivo(sentence)
        normal_sentence_vivo = copy.deepcopy(sentence.vivo)
        normal_sentence_vivo.normal_relations()
        super().__init__(sentence, normal_sentence_vivo)
        self.relevance = component_vivo.sum_compare(self.vivo)

    def __str__(self):
        return str(self.relevance) + " - " + self.sentence.text


class ComponentSentence(VivoSentence):
    # предложение, виво и словрь подходящих правил с их релевантностью
    def __init__(self, vivo_sentence, text_components):
        super().__init__(vivo_sentence.sentence, vivo_sentence.vivo)
        self.component_relevance = {}
        try:
            for component in text_components:
                self.component_relevance[component.name] = component.excerts[hash(self.sentence.text)].relevance
        except:
            print("component_sentence 1")
        self.max_relevance_element_name = ""
        self.max_relevance = -1
        self.define_max_relevance()

    def add_component(self, text_component):
        if not self.component_relevance.get(text_component.name):
            relevance = text_component.excerts[hash(self.sentence.text)].relevance
            self.component_relevance[text_component.name] = relevance
            if relevance > self.max_relevance:
                self.max_relevance = relevance
                self.max_relevance_element_name = text_component.name

    def define_max_relevance(self):
        for component_name in self.component_relevance:
            # self.max_relevance = 0
            if self.component_relevance[component_name] >= self.max_relevance:
                self.max_relevance = self.component_relevance[component_name]
                self.max_relevance_element_name = component_name



class RelevantExcert(VivoSentence):

    def __init__(self, vivo_sentence, component_vivo, relevance):
        super().__init__(vivo_sentence.sentence, vivo_sentence.vivo)
        self.component_vivo = component_vivo  # каждое предложение релевантно определенному виво, для этого и хранится
        self.relevance = relevance

    def __repr__(self):
        sentence_start_length = 0
        i = 0
        for token in self.sentence.tokens:
            sentence_start_length += (token.text.__len__())
            if self.sentence.text.__len__() - sentence_start_length > 1:
                sentence_start_length += 1
            if i == 3: break
            i = i+1
        return self.sentence.text[0:sentence_start_length] + " - " + str(self.relevance)
