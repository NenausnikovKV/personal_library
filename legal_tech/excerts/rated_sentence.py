from legal_tech.components.get_relevance import get_sentence_relevance_to_rule
from legal_tech.excerts.vivo_sentence import VivoSentence


class RatedSentence(VivoSentence):
    """ Предложение, его виво-представление и его релевантность одному компоненту """

    def __init__(self, sentence, rule_vivo, relevance=None):
        VivoSentence.__init__(self, sentence=sentence, vivo=sentence.vivo)
        self.rule_vivo = rule_vivo
        self.relevance = self.check_relevance(relevance)

    def __str__(self):
        return "{0} - {1}".format(str(self.relevance), self.sentence.text)


    def check_relevance(self, relevance):
        if relevance is not None:
            pass
        else:
            relevance = get_sentence_relevance_to_rule(self.vivo, self.rule_vivo)
        return relevance


