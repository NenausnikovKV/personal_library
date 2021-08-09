import copy
from operator import attrgetter

from legal_tech.components.rule import Rule
from legal_tech.excerts.rated_sentence import RatedSentence


class Component(Rule):

    """
       Правило и релевантные ему предложения c оценкой
    """

    def __init__(self, rule_name, rule_vivo, rated_sentences):
        self.name = rule_name
        self.rule = Rule(rule_name, rule_vivo)
        self.relevant_sentences = rated_sentences


    @staticmethod
    def get_all_sentences_relevances_to_rules(agreement, rules):
        components = dict()
        for rule_name, rule in rules.items():
            components[rule_name] = Component.get_sentence_relevances_to_rule(rule, agreement.sentences)
        return components

    @staticmethod
    def get_sentence_relevances_to_rule(rule, sentences):
        rule_vivo = copy.deepcopy(rule.vivo)
        rated_sentences = {}
        for sentence in sentences.values():
            sentence_copy = copy.deepcopy(sentence)
            rated_sentences[hash(sentence_copy.text)] = RatedSentence(sentence_copy, rule_vivo)
        return Component(rule.name, rule.vivo, rated_sentences)


    def get_max_relevant_sentence(self):
        return max(self.relevant_sentences.values(), key=attrgetter('relevance'))

    