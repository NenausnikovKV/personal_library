
from natasha import NewsEmbedding, NewsMorphTagger, NewsSyntaxParser, Doc

from NLP.external_analizer.morph_dictionaries.external_morph_dictionary.maru_morph_parsing import MaruMorphDictionary
from NLP.external_analizer.morph_dictionaries.external_morph_dictionary.pymorphy_morph_dictionary import \
    PymorphyMorphDictionary
from NLP.external_analizer.syntax_analyzer import SyntaxAnalizer



class SentenceAnalyzer(morph_dict = PymorphyMorphDictionary()):

    # синтаксическая разметка и морфология с учетом синтаксиса
    syntax_analizer = SyntaxAnalizer()
    morph_dict = PymorphyMorphDictionary()
    # morph_dict = MaruMorphDictionary()


    @classmethod
    def divide_text_to_sents(cls, text):

        from natasha import Doc


        def correct_token_id(sent_tokens):
            """
            Расшифровываем строковое представление нумерации в синтаксическом дереве.
            Преобразуем строку в число для id и head_id.
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
        doc.tag_morph(cls.syntax_analizer.morph_tagger)
        try:
            doc.parse_syntax(cls.syntax_analizer.syntax_parser)
            for sent in doc.sents:
                sent.tokens = correct_token_id(sent.tokens)

        except Exception:
            print(Exception)
        return list(doc.sents)

    @staticmethod
    def get_sent_from_sentence_text(sen_text):
        sents = SentenceAnalyzer.divide_text_to_sents(sen_text)
        sent = sents[0]
        return sent

    @staticmethod
    def divide_sentence_text_to_tokens(sentence_text):
        sentence_text = sentence_text.replace('\n', ' ')
        doc = Doc(sentence_text)
        doc.segment(SentenceAnalyzer.segmenter)
        sent = doc.sents[0]
        return list(sent.syntax.tokens)

    @staticmethod
    def divide_text_to_sentence_plan_texts(text):
        sents = SentenceAnalyzer.divide_text_to_sents(text)
        return [sentence.text for sentence in sents]
