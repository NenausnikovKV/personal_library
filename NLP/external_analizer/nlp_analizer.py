import natasha

from NLP.external_analizer.morph_dictionaries.pymorphy_morph_dictionary import PymorphyMorphDictionary
from NLP.external_analizer.syntax_analizer.syntax_analyzer import SyntaxAnalizer


class NLPAnalyzer():

    # создаем классы для анализа текста предложения для всего проекта
    segmenter = natasha.Segmenter()
    morph_dict = PymorphyMorphDictionary()
    # morph_dict = MaruMorphDictionary()
    syntax_analizer = SyntaxAnalizer()


    @staticmethod
    def change_morph_dictionary_to_maru():
        from NLP.external_analizer.morph_dictionaries.maru_morph_parsing import MaruMorphDictionary
        global morph_dict
        morph_dict = MaruMorphDictionary()



    @classmethod
    def divide_text_to_natasha_sents(cls, text):
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


        def correct_token_position_conserning_sentence(sent_tokens, sentence_start):
            for num, token in enumerate(sent_tokens):
                token.start = token.start - sentence_start
                token.stop = token.stop - sentence_start
            return sent_tokens

        doc = natasha.Doc(text)
        doc.segment(cls.segmenter)
        doc.tag_morph(cls.syntax_analizer.morph_tagger)
        doc.parse_syntax(cls.syntax_analizer.syntax_parser)

        sents = list(doc.sents)
        for sent in sents:
            sent.tokens = correct_token_id(sent.tokens)
            sent.tokens = correct_token_position_conserning_sentence(sent.tokens, sentence_start=sent.start)
        return sents

