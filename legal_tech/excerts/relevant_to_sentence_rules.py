from collections import defaultdict
from operator import attrgetter

from legal_tech.components.rated_rule import RatedRule
from legal_tech.excerts.vivo_sentence import VivoSentence


class RelevantRules(VivoSentence):

    """
    Предложение и релевантные ему правила
    А также максимально и максимально релевантное
    """



    # предложение, виво и словрь подходящих правил с их релевантностью
    def __init__(self, vivo_sentence, components):
        VivoSentence.__init__(self, vivo_sentence.sentence, vivo_sentence.vivo)
        self.rated_rules = dict()
        self.max_relevance_rule = None
        self.max_relevance = -1
        self._get_rated_rules(components)

    def add_rated_rule(self, rule, relevance):
        if rule.name not in self.rated_rules:
            rated_rule = RatedRule(rule, relevance)
            self.rated_rules[rule.name] = rated_rule
            if relevance > self.max_relevance:
                self._update_max_relevance(rated_rule)

    def define_max_relevance(self):
        for component_name in self.rated_rules:
            # self.max_relevance = 0
            if self.rated_rules[component_name].relevance >= self.max_relevance:
                self.max_relevance = self.rated_rules[component_name].relevance
                self.max_relevance_rule = self.rated_rules[component_name]

    def get_max_relevance_rule(self):
        return max(self.rated_rules, key=attrgetter(""))

    @classmethod
    def get_from_components(cls, components):
        relevant_to_sentence_rules = {}
        for component in components.values():
            for sentence_hash, relevant_sentence in component.relevant_sentences.items():
                if not relevant_to_sentence_rules.get(sentence_hash):
                    relevant_rules = RelevantRules(relevant_sentence,[component])
                    relevant_to_sentence_rules[sentence_hash] = relevant_rules
                else:
                    rule = component.rule
                    relevance = component.relevant_sentences[sentence_hash].relevance
                    relevant_to_sentence_rules[sentence_hash].add_rated_rule(rule, relevance)
        return relevant_to_sentence_rules


    # -----------------------------------------------------------------------------------------------------------------

    def _get_rated_rules(self, components):
        for component in components:
            rule = component.rule
            relevance = component.relevant_sentences[hash(self.sentence.text)].relevance
            self.add_rated_rule(rule, relevance)

    def _update_max_relevance(self, rated_rule):
        self.max_relevance = rated_rule.relevance
        self.max_relevance_rule = rated_rule