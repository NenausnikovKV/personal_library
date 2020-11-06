import maru

from NLP.token_stage.word import Word


class Maru():

    def parse(self, word_list):
        analyzed = self.analyzer.analyze(word_list)
        normal_words = [morph for morph in analyzed]
        return normal_words

    def __init__(self):
        self.analyzer = maru.get_analyzer(tagger='crf', lemmatizer='pymorphy')