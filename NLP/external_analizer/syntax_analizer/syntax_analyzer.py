from collections import defaultdict
from natasha import NewsEmbedding, NewsMorphTagger, NewsSyntaxParser



class SyntaxAnalizer:

    def __init__(self):
        # инициализируем обученную по новостным текстам модель
        ebd = NewsEmbedding()
        # морфология по обученной модели
        self.morph_tagger = NewsMorphTagger(ebd)
        #  синтаксис по обученной модели
        self.syntax_parser = NewsSyntaxParser(ebd)



