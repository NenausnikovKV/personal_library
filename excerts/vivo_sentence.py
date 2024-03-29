import copy
from graph_representation import Vivo


class VivoSentence():
    """
    Предложение и его графическое представление
    Соответствует интерфейсу элемента кластера
    дает возможность легко изменять метод получения виво предложения и метод сравнения
    """

    def __init__(self, sentence=None, vivo=None):
        self.sentence = sentence
        self.vivo = vivo

    def __add__(self, other):
        result = copy.deepcopy(self)
        result.vivo = self.vivo + other.vivo
        result.sentence = self.sentence + other.sentence
        return result

    def __repr__(self):
        return self.sentence.text

    # -----------------------------------------------------------------------------------------------------------------

    def normal_vivo(self):
        self.vivo.normal_relations()

    def compare(self, other):
        return self.vivo.sum_compare(other.vivo)

    def cut_off_vivo(self):
        # получаем общий рейтинг кластера
        self.vivo.discard_nodes_over_limit()

    # -----------------------------------------------------------------------------------------------------------------

    @classmethod
    def get_syntactical_vivo_sentence_from_sentence(cls, sentence):
        assert sentence.vivo != None, "Синтаксический виво предложения не обнаружен"
        vivo = sentence.vivo
        return cls(sentence, vivo)

    @classmethod
    def get_fully_connected_vivo_sentence_from_sentence(cls, sentence):
        vivo = cls._get_fully_connected_vivo_from_sentence(sentence)
        return cls(sentence, vivo)


    # -----------------------------------------------------------------------------------------------------------------

    @staticmethod
    def _get_fully_connected_vivo_from_sentence(sentence):
        word_texts = tuple([word.text for word in sentence.words.values()])
        vivo = Vivo(nodes=word_texts)
        vivo.normal_relations()
        return vivo


