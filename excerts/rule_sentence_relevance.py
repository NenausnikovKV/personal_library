from components.get_relevance import get_rule_sentence_relevance


class RuleSentenceRelevance():
    """ Предложение, его виво-представление и его релевантность одному компоненту """

    def __init__(self, vivo_sentence, rule, relevance=None):
        self.vivo_sentence = vivo_sentence 
        self.rule = rule
        self.relevance = self._check_relevance(relevance)

    def _check_relevance(self, relevance):
        if relevance is not None:
            pass
        else:
            relevance = get_rule_sentence_relevance(self.vivo_sentence.vivo, self.rule.vivo)
        return relevance


