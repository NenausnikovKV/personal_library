from operator import attrgetter

import natasha

from NLP.external_analizer.nlp_analizer import NLPAnalyzer
from NLP.sentence_stage.sentence import Sentence
from NLP.token_stage.personal_token import SentenceToken, Token
from graph_representation.vivo.relation import Relation
from graph_representation.vivo.vivo import Vivo


class natasha_sent:

    @staticmethod
    def get_sent_from_sentence_text(sen_text):
        sents = NLPAnalyzer.divide_text_to_sents(sen_text)
        sent = sents[0]
        return sent


    def divide_text_to_sentence_plain_texts(text):
        sents = NLPAnalyzer.divide_text_to_sents(text)
        return [sentence.text for sentence in sents]

    @staticmethod
    def divide_sentence_text_to_tokens(sentence_text):
        sentence_text = sentence_text.replace('\n', ' ')
        doc = natasha.Doc(sentence_text)
        doc.segment(NLPAnalyzer.segmenter)
        sent = doc.sents[0]
        return list(sent.syntax.tokens)

    @classmethod
    def initial_from_natasha_sent(cls, sent, sentence_start_in_text=-1, number=-1):

        def get_tokens(sent_tokens, sentence_start):
            sen_tokens = []
            for num, token in enumerate(sent_tokens):
                sen_tokens.append(SentenceToken(token.text, Token.define_type(token.text), num=num,
                                            start=token.start, stop=token.stop))
            return sen_tokens

        def get_syntax_vivo(sent_tokens, sentence_tokens):
            """
            переписываем связанные слова после работы синтаксического анализитора
            """

            head_id_sorted_tokens = sorted(sent_tokens, key=attrgetter("head_id"))
            token_dict = {token.id: token for token in sent_tokens}

            # syn_vivo = Vivo()
            relations = []
            for token in head_id_sorted_tokens:
                # 0 связан с корнем древа
                if token.head_id == 0:
                    continue

                # смещение на 1 так как 0 - это корень синтаксического древа
                token1 = token
                text1 = SentenceToken.find_normal_token_text(sentence_tokens[token1.id - 1], normal_tokens)
                token2 = token_dict[token.head_id]
                text2 = SentenceToken.find_normal_token_text(sentence_tokens[token2.id - 1], normal_tokens)
                if all([Token.define_type(text1) == "word", Token.define_type(text2) == "word",
                        token1.id != token2.id]):
                    relations.append(Relation(text1, text2, rating=1))
            syn_vivo = Vivo(relations=relations)
            syn_vivo.normal_relations()
            return syn_vivo

        # sent.syntax.print()
        sen_text =
        sen_tokens =
        syn_vivo = get_syntax_vivo(sent.tokens, sen_tokens)

        sent_data = dict()
        sentence_tokens = get_tokens(sent.tokens, sent.start)
        sent_data["syn_vivo"] = get_syntax_vivo(sent_tokens=sent.tokens, sentence_tokens=sent_data["sen_tokens"])
        sentence = Sentence(sent.text, sentence_tokens, normal_tokens, word_list, words, syn_vivo, num=number,
                       start=sentence_start_in_text)
        return

    @staticmethod
    def _get_normal_tokens_and_words(sen_tokens, sentence_text):
        """список слов в родном порядке"""

        word_tokens = [sen_token for sen_token in sen_tokens if sen_token.type == "word"]

        word_texts = [word_token.text for word_token in word_tokens]
        normal_words = SentenceAnalyzer.morph_dict.parse(word_texts)

        """список токенов в родном порядке"""
        normal_tokens = []
        counter = 0
        for num, sen_token in enumerate(sen_tokens):
            if counter < word_tokens.__len__() and sen_token.text == word_tokens[counter].text:
                normal_token = SentenceToken(normal_words[counter], type="word", num=num,
                                             start=sen_token.start, stop=sen_token.stop)
                normal_tokens.append(normal_token)
                counter = counter + 1
            else:
                normal_tokens.append(copy.deepcopy(sen_token))

        """список слов в родном порядке"""
        sentence_words = []
        for i in range(word_texts.__len__()):
            sen_token = word_tokens[i]
            normal_word = normal_words[i]
            sen_word = SentenceWord(
                sen_token, normal_word,
                rating=1, num=i, source_sentence_text=sentence_text)
            sentence_words.append(sen_word)

        return normal_tokens, sentence_words
