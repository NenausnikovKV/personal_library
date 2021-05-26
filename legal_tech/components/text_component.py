import copy
from operator import attrgetter

from legal_tech.components.component import Component
from legal_tech.excerts.rated_sentence import RatedSentence


class TextComponent(Component):

    """
       добавляется максимальный рейтинг отрывка и его хэш
    """

    def __init__(self, name, vivo, necessity, rated_excerts):
        Component.__init__(self, name, vivo, necessity)
        self.excerts = dict(rated_excerts)
        if self.excerts.__len__() > 0:
            self.max_rating_excert = self._get_max_relevance_ecxert()
            self.max_rating_excert_hash = hash(self.max_rating_excert.sentence.text)
            if self.max_rating_excert_hash != 0:
                self.max_rating = self.excerts[self.max_rating_excert_hash].relevance
            else:
                self.max_rating = -1

    @classmethod
    def get_text_component(cls, rule_component, text_object):
        sample_vivo = copy.deepcopy(rule_component.vivo)
        rated_sentences = {}
        for sentence in text_object.sentences.values():
            rated_sentences[hash(sentence.text)] = RatedSentence(sentence, sample_vivo)
        return cls(rule_component.name, sample_vivo, rule_component.necessity, rated_sentences)
    
    def __repr__(self):
        if self.max_rating_excert_hash != 0:
            max_rating = self.excerts[self.max_rating_excert_hash].rating
            return self.name + " - " + str(max_rating)
        else:
            return self.name + " - " + str(0)

    def _get_max_relevance_ecxert(self):
        max_relevance = -1
        max_relevant_excert = None
        for sentence_hash in self.excerts:
            if self.excerts[sentence_hash].relevance > max_relevance:
                max_relevance = self.excerts[sentence_hash].relevance
                max_relevant_excert = self.excerts[sentence_hash]
        return max_relevant_excert


    def get_max_relevant_excert(self):
        max_relevance_excert =  max((excert for excert in self.excerts.values()), key=attrgetter("relevance"))
        return max_relevance_excert
