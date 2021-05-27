
import natasha

from NLP.external_analizer.nlp_analizer import NLPAnalyzer
from NLP.external_analizer.sentence_analizer import natasha_sent_adapter
from NLP.token_stage.personal_token import SentenceToken, Token


class NatashaSent:

    """
    Методы обработки текста предложения
    """

    @classmethod
    def _get_sent_from_sentence_text(cls, sentence_text):
        sents = NLPAnalyzer.divide_text_to_natasha_sents(sentence_text)
        sent = sents[0]
        return sent


    @staticmethod
    def get_sentence_from_sentence_text(sentence_text, sentence_num=-1, sentence_start=-1):
        """
        Получение экземпляра класса Sentence из предложения тексте (plain_text)
        """
        natasha_sent = NatashaSent._get_sent_from_sentence_text(sentence_text)
        sentence = natasha_sent_adapter.get_sentence_from_natasha_sent(natasha_sent, sentence_num, sentence_start)
        return sentence


    @staticmethod
    def divide_sentence_text_to_tokens(sentence_text):
        """
        Разделение предложения на токены библиотеки NAtasha
        """
        def get_natasha_sent_tokens(sentence_text):
            # Получение natasha sent tokens
            sentence_text = sentence_text.replace('\n', ' ')
            doc = natasha.Doc(sentence_text)
            doc.segment(NLPAnalyzer.segmenter)
            sent = doc.sents[0]
            sent_tokens = list(sent.syntax.tokens)
            return sent_tokens

        def get_personal_tokens_from_sent_token(sent_tokens, sentence_text):
            # Преобразование natasha sent tokens в мои токены Token
            tokens = list()
            stop = 0
            for token_num, token in enumerate(sent_tokens):
                start = sentence_text.find(token.text, stop)
                stop = start + len(token.text)
                sentence_token = SentenceToken(token.text, Token.define_type(token.text), token_num, start=start,
                                               stop=stop)
                tokens.append(sentence_token)
            return tokens

        sent_tokens = get_natasha_sent_tokens(sentence_text)
        tokens = get_personal_tokens_from_sent_token(sent_tokens, sentence_text)

        return tokens


    @staticmethod
    def divide_text_to_sentences(text):
        sents = NLPAnalyzer.divide_text_to_natasha_sents(text)
        sentences = list()
        for num, sent in enumerate(sents):
            sentence = natasha_sent_adapter.get_sentence_from_natasha_sent(sent, sent.start, num)
            sentences.append(sentence)
        return sentences

    @staticmethod
    def divide_text_to_sentence_plain_texts(text):
        """
        Разделение текста на предложения в plain_text
        """
        sents = NLPAnalyzer.divide_text_to_natasha_sents(text)
        return [sentence.text for sentence in sents]


    # ------------------------------------------------------------------------------------------------------------------


    #-------------------------------------------------------------------------------------------------------------------





if __name__ == "__main__":
    sentence_text = "я люблю есть сыр"
    file_text = "я люблю сыр с плесенью. В этом есть что-то благородное."

    tokens = NatashaSent.divide_sentence_text_to_tokens(sentence_text)
    sentence = NatashaSent.get_sentence_from_sentence_text(sentence_text)


    sentence_text_list = NatashaSent.divide_text_to_sentence_plain_texts(file_text)
    sentences = NatashaSent.divide_text_to_sentences(file_text)
    a = 90
