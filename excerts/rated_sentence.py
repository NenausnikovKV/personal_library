import copy
from operator import attrgetter


class RatedSentence():

    """
    Предложение и релевантные ему правила
    """

    # предложение, виво и словрь подходящих правил с их релевантностью
    def __init__(self, vivo_sentence, rule_sentence_relevances):
        self.vivo_sentence = vivo_sentence 
        # dict
        self.rule_sentence_relevances = rule_sentence_relevances
        a = 90

    @property
    def max_relevance(self):
        max_relevant_rule = max(self.rule_sentence_relevances.values(), key=attrgetter("relevance"))
        return max_relevant_rule.relevance

    @property
    def max_relevant_rule(self):
        max_relevant_rule = max(self.rule_sentence_relevances.values(), key=attrgetter("relevance"))
        return max_relevant_rule

    def add_rated_rule(self, rule, rule_sentence_relevance):
        self.rule_sentence_relevances[rule.name] = rule_sentence_relevance

    @classmethod
    def get_all_from_components(cls, components):
        relevant_rules = {}
        for component in components.values():
            for sentence_hash, rule_sentence_relevance in component.rule_sentence_relevance.items():
                if not relevant_rules.get(sentence_hash):
                    # имя rated sentence в виде vivo_sentence - должно отличаться от vivo_Sentence внутри rule_sentence_relevances
                    named_vivo_sentence = copy.deepcopy(rule_sentence_relevance.vivo_sentence)
                    relevant_rule = RatedSentence(named_vivo_sentence,
                                                  {component.name: rule_sentence_relevance})
                    relevant_rules[sentence_hash] = relevant_rule
                else:
                    relevant_rules[sentence_hash].add_rated_rule(component.rule, rule_sentence_relevance)
        return relevant_rules



    def _get_rated_rules(self, components):
        for component in components:
            rule = component.rule
            relevant_sentence_key = hash(self.vivo_sentence.sentence.text)
            relevance = component.rule_sentence_relevance[relevant_sentence_key].relevance
            self.add_rated_rule(rule, relevance)


