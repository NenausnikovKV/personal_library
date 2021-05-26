import copy
import math


class NodeDictionary:
    def __init__(self, text, number=0):
        self.node_dictionary = copy.copy(text.word_dictionary)
        self.number = number
        keys = text.word_dictionary.keys()
        for key in keys:
            self.node_dictionary[key].object = Node(text.word_dictionary.get(key).object, text)
        for key in self.node_dictionary.keys():
            self.node_dictionary[key].object.insert_into_map(self.node_dictionary)
        a = 9


def __str__(self):
    return "список номер " + str(self.number) + " содержит " + str(self.node_dictionary.__len__()) + " узлов"

class Node:

    def __init__(self, main_word, text_object):

        def extract_sentences(text_sentences, main_word):
            """Выделяются все предложения текста, содержащие рассматриваемое слово
                а также предложения между ними
            """

            def define_excerpt_sentences(text_sentences, main_word):
                excerpt_sentences = []
                for excerpt_sentence in text_sentences:
                    if main_word.text in excerpt_sentence.word_dictionary:
                        excerpt_sentences.append(excerpt_sentence)
                return excerpt_sentences

            def addAdditionalSentences(excerpt_sentences, text_sentences):
                for i in range(1, excerpt_sentences.__len__()):
                    average_sentence_number = math.fabs(excerpt_sentences[i].number - excerpt_sentences[i - 1].number)
                    if average_sentence_number == 2:  # если идут через одно, то включить предложение между ними
                        excerpt_sentences.part_of(i, text_sentences[excerpt_sentences[i].number + 1])
                        i += 2
                return excerpt_sentences

            excerpt_sentences = define_excerpt_sentences(text_sentences, main_word)
            excerpt_sentences = addAdditionalSentences(excerpt_sentences, text_sentences)
            return excerpt_sentences

        def define_text_excerpts(sentences, main_word):
            """"""
            temp_sentences = []
            text_excerpts = []
            if sentences.__len__() > 0:
                temp_sentences.append(sentences[0])

            for i in range(1, sentences.__len__()):
                if math.fabs(sentences[i].number - sentences[i - 1].number) == 1:
                    temp_sentences.append(sentences[i])
                else:
                    text_excerpts.append(TextExcerpt(temp_sentences, main_word))
                temp_sentences.clear()
                temp_sentences.append(sentences[i])

            return text_excerpts

        def combine_excerpt_related_words(text_excerpts, main_word):
            """Объединение связанных слов первого уровня"""
            general_related_word_dictionary = {}
            for text_excerpt in text_excerpts:
                keys = text_excerpt.related_word_dictionary.keys()
                for key in keys:
                    if key != main_word.text:
                        if key in general_related_word_dictionary:
                            general_related_word_dictionary[key] = general_related_word_dictionary[key] + \
                                                                   text_excerpt.related_word_dictionary[key]
                        else:
                            general_related_word_dictionary[key] = text_excerpt.related_word_dictionary[key]
            return general_related_word_dictionary

        self.main_word = main_word
        self.text = main_word.text
        self.source = text_object
        self.sentences = extract_sentences(text_object.sentences, self.main_word)
        self.text_excerpts = define_text_excerpts(self.sentences, self.main_word)
        self.related_word_dictionary = combine_excerpt_related_words(self.text_excerpts, self.main_word)
        self.related_node_dictionary = {}  # переменнафя для будущих связанных узлов

    # def insert_into_map(self, node_dictionary):
    #     for key in self.related_word_dictionary.keys():
    #         self.related_node_dictionary[key] = Dictionary(node_dictionary.get(key).object,
    #                                                        self.related_word_dictionary.get(key).rating)
    def __str__(self):
        return self.text + " - " + str(self.related_word_dictionary.__len__()) + " связанных слов"

    def __add__(self, other):
        result = copy.copy(self)
        if result.text == other.text:
            result.rating = result.rating + other.rating
            combined_related_words = {}
            for related_word in result.related_word_dictionary:
                if related_word in other.relate_words:
                    combined_related_words[related_word.text] = related_word + other.relate_words[related_word.text]
                else:
                    combined_related_words[related_word.text] = related_word
        else:
            raise Exception('Для сложения текст двух элементов должен быть одинаковым')
        return result


class TextExcerpt:
    def __init__(self, sentences, main_word):

        """
        отрывок содержащий
        Получаем предложения содержащие искомое слово и предложения, находящиеся в области поиска
        Не доказанная эвристика нахождения связей в предложении, находящемся двумя предложениями
        содержащими исследуемоет слово
        """

        def define_word_dictionary(sentences):
            word_dictionary = {}
            for sentence in sentences:
                keys = sentence.word_dictionary.keys()
                for key in keys:
                    if word_dictionary.get(key):
                        word_dictionary[key] = word_dictionary[key] + sentence.word_dictionary[key]
                    else:
                        word_dictionary[key] = sentence.word_dictionary[key]
            return word_dictionary

        def define_related_words(excerpt_word_dictionary, main_word):
            related_words_dictionary = copy.copy(excerpt_word_dictionary)
            related_words_dictionary.pop(main_word.text)
            return related_words_dictionary

        def define_relations(excerpt_word_dictionary, main_word):
            """определяем связи первого уровня"""
            word_relations = []
            keys = excerpt_word_dictionary.keys()
            for key in keys:
                if key != main_word.text:
                    word_relations.append(WordRelation(main_word, key, excerpt_word_dictionary.get(key)))
            return word_relations

        self.sentences = sentences  # пердложения отрывка
        self.word_dictionary = define_word_dictionary(self.sentences)
        self.related_word_dictionary = define_related_words(self.word_dictionary, main_word)
        # self.word_relation = define_relations(self.word_dictionary, main_word)


class WordRelation:
    def __init__(self, word1, word2, rating):
        if word1 < word2:
            self.word1 = word1
            self.word2 = word2
        else:
            self.word1 = word2
            self.word2 = word1

        self.rating = rating
        self.text = self.word1.text + "-" + self.word2.text


if __name__ == "__main__":
    pass
