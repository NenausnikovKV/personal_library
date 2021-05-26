import maru
from NLP.morph_dictionary.morph_dictionary import MorphDictionary


class MaruMorphDictionary(MorphDictionary):

    def __init__(self):
        """
            Maru() - словарь на основе обучения нейронных сетей, работает при подачи списка слов предложения
        """
        self.dictionary = maru.get_analyzer(tagger='crf', lemmatizer='pymorphy')

    def parse(self, word_list):
        analyzed_lemmas = self.dictionary.analyze(word_list)
        normal_words = [lemma.word for lemma in analyzed_lemmas]
        return normal_words



if __name__=="__main__":
    morph_dict = MaruMorphDictionary()
    word_list = ['Согласие', 'на', 'обработку', 'персональных', 'данных']
    normal_word_list = morph_dict.parse(word_list)
    print(normal_word_list)