import copy
from operator import attrgetter

from legal_tech.components.rule import Rule
from legal_tech.excerts.rule_sentence_relevance import RuleSentenceRelevance


class Component(Rule):

    """
       Правило и релевантные ему предложения c оценкой
    """

    def __init__(self, rule_name, rule_vivo, rule_sentence_relevances):
        self.name = rule_name
        self.rule = Rule(rule_name, rule_vivo)
        self.relevant_sentences = rule_sentence_relevances


    @staticmethod
    def get_all_components(agreement, rules):
        components = dict()
        for rule_name, rule in rules.items():
            components[rule_name] = Component.get_component(rule, agreement.vivo_sentences)
        return components

    @staticmethod
    def get_component(rule, vivo_sentences):
        rule_copy = copy.deepcopy(rule)
        relevant_sentence = {}
        for sent_key, vivo_sentence in vivo_sentences.items():
            vivo_sentence_copy = copy.deepcopy(vivo_sentence)
            relevant_sentence[sent_key] = RuleSentenceRelevance(vivo_sentence_copy, rule_copy)
        return Component(rule_copy.name, rule_copy.vivo, relevant_sentence)


    def get_max_relevant_sentence(self):
        return max(self.relevant_sentences.values(), key=attrgetter('relevance'))

    