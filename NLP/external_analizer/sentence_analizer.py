import natasha

from NLP.external_analizer.nlp_analizer import NLPAnalyzer



class natasha_sentence:


    def get_sent_from_sentence_text(sen_text):
        sents = NLPAnalyzer.divide_text_to_sents(sen_text)
        sent = sents[0]
        return sent


    def divide_text_to_sentence_plain_texts(text):
        sents = NLPAnalyzer.divide_text_to_sents(text)
        return [sentence.text for sentence in sents]


    def divide_sentence_text_to_tokens(sentence_text):
        sentence_text = sentence_text.replace('\n', ' ')
        doc = natasha.Doc(sentence_text)
        doc.segment(NLPAnalyzer.segmenter)
        sent = doc.sents[0]
        return list(sent.syntax.tokens)