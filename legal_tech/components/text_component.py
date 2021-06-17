import copy
from operator import attrgetter

from legal_tech.components.component import Component
from legal_tech.excerts.rated_sentence import RatedSentence


class TextComponent(Component):

    """
       добавляется максимальный рейтинг отрывка и его хэш
    """

    def __init__(self, name, vivo, necessity, sentence_collations):
        Component.__init__(self, name, vivo, necessity)

        self.sentence_relevances = dict(sentence_collations)

        self.max_sentence_relevance = self.get_max_sentence_relevance()
        self.max_relevant_sentence_hash = hash(self.max_sentence_relevance.sentence.text)

        try:
            self.max_rating = self.sentence_relevances[self.max_relevant_sentence_hash].relevance
        except KeyError:
            self.max_rating = -1

    def __repr__(self):
        if self.max_relevant_sentence_hash != 0:
            max_rating = self.sentence_relevances[self.max_relevant_sentence_hash].rating
            return self.name + " - " + str(max_rating)
        else:
            return self.name + " - " + str(0)

    @classmethod
    def get_text_component_from_text_object(cls, rule_component, text_object):
        sample_vivo = copy.deepcopy(rule_component.vivo)
        rated_sentences = {}
        for sentence in text_object.sentences.values():
            rated_sentences[hash(sentence.text)] = RatedSentence(sentence, sample_vivo)
        return cls(rule_component.name, sample_vivo, rule_component.necessity, rated_sentences)

    def get_max_sentence_relevance(self):
        return max(self.sentence_relevances.values(), key=attrgetter('relevance'))

    #  outdated
    def _get_max_relevance_sentence(self):
        max_relevance = -1
        max_relevant_sentence = None
        for sentence_hash in self.sentence_relevances:
            if self.sentence_relevances[sentence_hash].relevance > max_relevance:
                max_relevance = self.sentence_relevances[sentence_hash].relevance
                max_relevant_sentence = self.sentence_relevances[sentence_hash]
        return max_relevant_sentence


