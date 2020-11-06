import maru
import tensorflow as tf

from NLP.dictionary_library.maru_library import Maru
from NLP.token_stage.word import Word

print(tf.__version__)



class MorphDictionary:
    def __init__(self, dictionary = Maru):
        self.dictionary = Maru()
        # self.morph = pymorphy2.MorphAnalyzer()

    def parse(self, word_list):
            return self.dictionary.parse(word_list)

