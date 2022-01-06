from legal_tech.components.rule import Rule


class RatedRule(Rule):

    """
        правило и его релевантность
    """

    def __init__(self, rule, relevance):
        Rule.__init__(self, rule.name, rule.vivo)
        self.relevance = relevance


    def get_rule_relevance_to_sentence(self, sentence_vivo):
        """
        ядро  сравнения
        """
        # todo тут находится ядро  сравнения выбирается как именно сравниваются компоненты с предложениями
        return self.vivo.part_of(sentence_vivo)

    def __repr__(self):
        return f"{self.name} - {str(self.relevance)}"