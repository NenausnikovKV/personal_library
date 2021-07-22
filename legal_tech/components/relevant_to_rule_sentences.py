import copy
from operator import attrgetter

from legal_tech.components.rule import Rule
from legal_tech.excerts.rated_sentence import RatedSentence


class RelevantToRuleSentences(Rule):

    """
       добавляется максимальный рейтинг отрывка и его хэш
    """

    def __init__(self, rule_name, rule_vivo, rated_sentences):

        self.rule = Rule(rule_name, rule_vivo)
        self.relevant_sentences = rated_sentences

        # try:
        #     max_relevant_sentence = self.get_max_relevant_sentence()
        #     self.max_relevance = max_relevant_sentence.relevance
        # except KeyError:
        #     self.max_relevance = -1
    
    @classmethod
    def get_relevant_to_rule_sentences(cls, agreement, rules):
        relevant_to_rule_sentences = dict()
        for sample_component_name, rule in rules.items():
            relevant_to_rule_sentences[sample_component_name] = RelevantToRuleSentences.get_from_text_object(rule,
                                                                                                             agreement)
        return relevant_to_rule_sentences

    @classmethod
    def get_from_text_object(cls, rule, text_object):
        sample_vivo = copy.deepcopy(rule.vivo)
        rated_sentences = {}
        for sentence in text_object.sentences.values():
            rated_sentences[hash(sentence.text)] = RatedSentence(sentence, sample_vivo)
        return RelevantToRuleSentences(rule.name, rule.vivo, rated_sentences)


        
    
    def get_max_relevant_sentence(self):
        return max(self.relevant_sentences.values(), key=attrgetter('relevance'))

    