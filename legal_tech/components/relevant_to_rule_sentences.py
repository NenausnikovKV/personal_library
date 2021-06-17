import copy
from operator import attrgetter

from legal_tech.components.rule import Rule
from legal_tech.excerts.rated_sentence import RatedSentence


class RelevantToRuleSentences(Rule):

    """
       добавляется максимальный рейтинг отрывка и его хэш
    """

    def __init__(self, rule_name, rated_sentences):
        self.rule_name = rule_name
        self.relevant_sentences = rated_sentences

        try:
            self.max_sentence_relevance = self.get_max_sentence_relevance()
            # self.max_relevant_sentence_hash = hash(self.max_sentence_relevance.sentence.text)
            self.max_relevance = self.relevant_sentences[self.max_relevant_sentence_hash].relevance
        except KeyError:
            self.max_relevance = -1


    @classmethod
    def get_from_text_object(cls, rule_component, text_object):
        sample_vivo = copy.deepcopy(rule_component.vivo)
        rated_sentences = {}
        for sentence in text_object.sentences.values():
            rated_sentences[hash(sentence.text)] = RatedSentence(sentence, sample_vivo)
        return cls(rule_component.name, rated_sentences)

    def get_max_sentence_relevance(self):
        return max(self.relevant_sentences.values(), key=attrgetter('relevance'))
