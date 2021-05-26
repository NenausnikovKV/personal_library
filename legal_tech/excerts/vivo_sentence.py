import copy
from clustering.cluster.element.cluster_element import ClusterElement
from graph_representation.vivo.vivo import Vivo


class VivoSentence(ClusterElement):
    """

    Предложение и его графическое представление
    Соответствует интерфейсу элемента кластера

    """

    def __init__(self, sentence=None, vivo=None):
        self.sentence = sentence
        self.vivo = vivo


    @classmethod
    def get_vivo_sentence_from_sentence(cls, sentence):
        vivo = cls.get_fully_connected_vivo_from_sentence(sentence)
        return cls(sentence, vivo)


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
        return self.vivo.sum_compare(other.vivo)

    @staticmethod
    def get_fully_connected_vivo_from_sentence(sentence):
        word_texts = tuple([word.text for word in sentence.words.values()])
        vivo = Vivo(nodes=word_texts)
        vivo.normal_relations()
        return vivo

    def cut_off(self):
        # получаем общий рейтинг кластера
        self.vivo.discard_nodes_over_limit()
       
