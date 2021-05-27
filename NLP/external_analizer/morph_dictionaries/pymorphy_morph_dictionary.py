from NLP.external_analizer.morph_dictionaries.morph_dictionary import MorphDictionary


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


if __name__=="__main__":
    morph_dict = PymorphyMorphDictionary()
    word_list = ['Согласие', 'на', 'обработку', 'персональных', 'данных']
    normal_word_list = morph_dict.parse(word_list)
    print(normal_word_list)