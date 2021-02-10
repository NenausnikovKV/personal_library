from collections import defaultdict
from operator import attrgetter

from natasha import NewsEmbedding, Segmenter, NewsMorphTagger, NewsSyntaxParser, Doc
import yargy
from yargy.tokenizer import MorphTokenizer
from NLP.dictionary_library.maru_library import Maru

class MorphDictionary:
    def __init__(self, dictionary = Maru()):
        """
        загрузка внешнего морфологического словаря
        Maru() - словарь на основе обучения нейронных сетей, работает при подачи списка слов предложения
        pymorphy2.MorphAnalyzer() - словарь на основе лексических правил, работает при подачи одного слова
        """
        self.dictionary = dictionary

    def parse(self, word_list):
            return self.dictionary.parse(word_list)

class Yargy_tokenizer():
    def __init__(self):
        # yargy - токенизация по правилам синтаксиса
        tokenizer = yargy.tokenizer.MorphTokenizer()

class SyntaxAnalyzer():
    # разделение текста на предложения
    segmenter = Segmenter()
    # получение нормальной формы слова
    morph_dict = MorphDictionary()

    # инициализируем обученную по новостным текстам модель
    ebd = NewsEmbedding()
    # морфология по обученной модели
    morph_tagger = NewsMorphTagger(ebd)
    #  синтаксис по обученной модели
    syntax_parser = NewsSyntaxParser(ebd)


    @classmethod
    def divide_text_to_sents(cls, text):

        def correct_token_id(sent_tokens):
            """
            преобразуем строку в число для id и head_id
            """
            for token in sent_tokens:
                head_id = token.head_id
                head_id = head_id.split("_")[1]
                token.head_id = int(head_id)
                id = token.id
                id = id.split("_")[1]
                token.id = int(id)
            return sent_tokens

        doc = Doc(text)
        doc.segment(cls.segmenter)
        doc.tag_morph(cls.morph_tagger)
        try:
            doc.parse_syntax(cls.syntax_parser)
            for sent in doc.sents:
                sent.tokens = correct_token_id(sent.tokens)

        except Exception:
            print(Exception)
        return list(doc.sents)

    @staticmethod
    def get_sent_from_sentence_text(sen_text):
        sents = SyntaxAnalyzer.divide_text_to_sents(sen_text)
        sent = sents[0]
        return sent

    @staticmethod
    def divide_sentence_text_to_tokens(sentence_text):
        sentence_text = sentence_text.replace('\n', ' ')
        doc = Doc(sentence_text)
        doc.segment(SyntaxAnalyzer.segmenter)
        sent = doc.sents[0]
        return list(sent.syntax.tokens)

    @staticmethod
    def divide_text_to_sentence_plan_texts(text):
        sents = SyntaxAnalyzer.divide_text_to_sents(text)
        return [sentence.text for sentence in sents]

class SyntaxTree():

    def __init__(self, sent, vertices, token_dict):
        self.sent = sent
        self.vertices = vertices
        self.token_dict = token_dict


    @classmethod
    def create_tree_from_sents(cls, sent):
        token_dict = defaultdict(list)
        vertices = []
        for token in sent.tokens:
            token_dict[token.head_id].append(token)
            if token.head_id == 0:
                vertices.append(token.id)
        return cls(sent, vertices, token_dict)


    def _sentence_tree(self):
        for vertex in self.vertices:
            self.extract_tree_branch(self.token_dict[vertex])

        token_dict = {token.id: token for token in sent.tokens}
        head_id_dict = {token.head_id: token for token in sent.tokens}
        for token in sent.tokens:
            token1 = token
            token2 = token_dict[token.head_id]

    def extract_tree_branch(self, start):
        pass
