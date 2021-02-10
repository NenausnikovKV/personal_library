import copy
from filecmp import cmp

from word_stage.nlp_exceptions import IncorrectSumAttributes


class RelatedPoint():
    def __init__(self, text, rating):
        self.text = text
        self.rating = rating

    def __add__(self, other):
        result = copy.copy(self)
        if result.text != other:
            raise IncorrectSumAttributes()
        result.rating = result.rating + other.rating

class Point:
    def __init__(self, main_word_text, related_points):
        self.text = main_word_text
        self.related_points = related_points

    def __add__(self, other):
        result = copy.copy(self)
        if result.text != other:
            raise IncorrectSumAttributes()
        for key in other.related_points:
            related_point = other.related_points[key]
            if not result.related_points.get(key):
                result.related_points[key] = related_point
            else:
                result.related_points[key] = result.related_points[key] + related_point

    @staticmethod
    def get_point_from_relations(main_word_text, relations):
        related_points = {}
        for relation in relations:
            rating = relation["rating"]
            word_text1 = relation["node1"]
            word_text2 = relation["node2"]
            if word_text1 == main_word_text:
                related_points[hash(word_text2)] = RelatedPoint(word_text2, rating)
            if word_text2 == main_word_text:
                related_points[hash(word_text1)] = RelatedPoint(word_text1, rating)
        return Point(main_word_text, related_points)

    @staticmethod
    def get_point_from_sentence(main_word_text, sentence):
        text = main_word_text
        related_words = {}
        for word_hash in sentence.words:
            word = sentence.words[word_hash]
            if word.text is not main_word_text:
                related_words[hash(word.text)] = RelatedPoint(word.text, 1)
        return Point(text, related_words)

    def __eq__(self, other):
        if isinstance(other, Point):
            return self.text == other.text and cmp(self.related_word_ratings, other.related_word_ratings)
        elif isinstance(other, str):
            return self.text == other
        else:
            return None
