from abc import abstractmethod

import maru


@abstractmethod
class MorphDictionary:
    def __init__(self):
        """
            загрузка внешнего морфологического словаря
        """
        pass
    def parse(self, word_list):
        pass

class MaruMorphDictionary(MorphDictionary):

    def __init__(self):
        """
            Maru() - словарь на основе обучения нейронных сетей, работает при подачи списка слов предложения
        """
        self.dictionary = Maru()

    def parse(self, word_list):
            return self.dictionary.parse(word_list)

class PymorphyMorphDictionary(MorphDictionary):
    def __init__(self):
        """
            pymorphy2.MorphAnalyzer() - словарь на основе лексических правил, работает при подачи одного слова
        """
        import pymorphy2
        self.morph_dictionary = pymorphy2.MorphAnalyzer()

    def parse(self, word_list):
        # из списка слов получение списка слов в нормальной форме, выбор выполняется без контекста
        normal_words = []
        for word in word_list:
            possible_normal_form_words = self.morph_dictionary.parse(word)
            normal_words.append(possible_normal_form_words[0].normal_form)
        return normal_words

if __name__ == '__main__':
    word_list = ["стали","продукты"]
    morph = PymorphyMorphDictionary()
    print(morph.parse(word_list))