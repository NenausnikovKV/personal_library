"""Предложения согласия и входящих в него объектов"""

import copy
from operator import attrgetter

from NLP.external_analizer.nlp_analizer import NLPAnalyzer
from NLP.external_analizer.natasha_sent import NatashaSent
from NLP.token_stage.word import SentenceWord
from NLP.token_stage.personal_token import SentenceToken, Token
from graph_representation.vivo.relation import Relation
from graph_representation.vivo.vivo import Vivo


class Sentence:

    def __init__(self, sen_text, tokens, normal_tokens, word_list, sen_words, syn_vivo, num=-1, start=-1):
        # 
        self.text = sen_text
        self.num = num
        # 
        self.start = start
        self.stop = start + self.text.__len__()
        # 
        self.tokens = tokens
        # 
        self.normal_tokens = normal_tokens
        self.word_list = word_list
        self.words = sen_words
        self.vivo = syn_vivo

    @classmethod
    def initial_from_sentence_text(cls, sentence_text, number=-1, start=-1, ):

        sent = NatashaSent._get_sent_from_sentence_text(sentence_text)
        # todo перепись переменной start неочевидн, прописать более очевидный способ записи
        sentence = NatashaSent._get_sentence_from_natasha_sent(sent, start, number)

        sentence.start = start
        return sentence


    # ------------------------------------------------------------------------------------------------------------------

    def __add__(self, other):

        result = copy.deepcopy(self)

        result.text = result.text + " \n" + other.text

        result.tokens.extend(other.tokens)
        result.normal_tokens.extend(other.normal_tokens)
        result.word_list.extend(other.word_list)

        for key in other.words.keys():
            if not result.words.get(key):
                result.words[key] = other.words[key]
            else:
                result.words[key].rating += other.words[key].rating

        result.vivo = result.vivo + other.vivo
        result.num = None
        result.start = None
        result.stop = None

        return result

    def __sub__(self, other):
        #  определить кусок, который надо вычесть
        #  кусок должен быть цельным, не рваным, по крайней мере пока
        other_text = other.text.rstrip('.').rstrip()
        if self.text.find(other_text) < 0:
            return None
        new_text = self.text.replace(other_text, "")
        return Sentence.initial_from_sentence_text(new_text)

    def __str__(self):
        return self.text

    def __eq__(self, other):
        return self.text == other.text

    # Изменение содержания предложений
    # ------------------------------------------------------------------------------------------------------------------

    def remove_word(self, word_text):
        """
        удаление слова из предложения
        """

        def remove_from_word_list():
            # удаляем слово из списка слов и отмечаем места удаления
            word_list_nums = []
            i = 0
            while i < self.word_list.__len__():
                word = self.word_list[i]
                if word.text == word_text:
                    self.word_list.pop(i)
                    word_list_nums.append(i)
                    i -= 1
                i += 1
            return word_list_nums

        def remove_from_token_list():
            starts = []
            token_nums = []
            i = 0
            while i < self.normal_tokens.__len__():
                normal_token = self.normal_tokens[i]
                if normal_token.text == word_text:
                    token_nums.append(i)
                    token = self.tokens[i]
                    starts.append(token.start)
                    token_len = self.tokens[i].text.__len__()
                    token_num = i + 1
                    # смещение токенов расположенных за удаленным
                    while token_num < self.tokens.__len__():
                        token = self.tokens[token_num]
                        normal_token = self.normal_tokens[token_num]
                        token.start -= token_len
                        token.stop -= token_len
                        normal_token.start = token.start
                        normal_token.stop = token.stop
                        token_num += 1
                    # удаление токенов
                    self.normal_tokens.pop(i)
                    self.tokens.pop(i)
                    i -= 1
                i += 1
            return starts, token_nums

        def remove_from_sentence_text():
            # удаляем из текста предложения
            for start in starts:
                stop = start + len(word_text)
                self.text = self.text[:start] + self.text[stop:]
                # корректируем конец предложения
                self.stop = self.stop - word_text.__len__()

        def remove_from_word_dict():
            # удаляем из словаря
            if self.words.get(hash(word_text)):
                self.words.pop(hash(word_text))

        # удаляем все повторения  из списка слов
        word_list_nums = remove_from_word_list()
        # удаляем все повторения из списка токенов
        starts, token_nums = remove_from_token_list()
        # удадляем из текста предложения
        remove_from_sentence_text()
        # удаляем из словаря
        remove_from_word_dict()
        return starts, token_nums, word_list_nums

    def add_words(self, text, starts, word_list_nums, token_nums):

        # вставка слова в заданные места

        def correct_nums_and_positions(num):
            while num < token_nums.__len__():
                if starts[num] > start:
                    starts[num] += text.__len__()
                    token_nums[num] += 1
                    word_list_nums[num] += 1
                num += 1

        def correct_next_tokens(j):
            text_len = text.__len__() - 1
            while j < self.tokens.__len__():
                token = self.tokens[j]
                normal_token = self.normal_tokens[j]
                token.start += text.__len__()
                token.stop += text.__len__()
                normal_token.start = token.start
                normal_token.stop = token.stop
                j += 1

        sen_word = None
        for i in range(word_list_nums.__len__()):
            start = starts[i]
            word_list_num = word_list_nums[i]
            token_num = token_nums[i]
            stop = start + text.__len__()

            # встраиваем слово в токены
            new_sen_token = SentenceToken(text, type="word", num=token_num, start=start, stop=stop)
            self.tokens.insert(token_num, new_sen_token)
            self.normal_tokens.insert(token_num, new_sen_token)

            # встраиваем слово в список слов
            sen_word = SentenceWord(new_sen_token, text, num=word_list_num, rating=1)
            self.word_list.insert(word_list_num, sen_word)

            # вписывани е слова в предложение
            self.text = self.text[:start] + text + self.text[start:]

            # корректируем следующие слова для вставки
            j = i + 1
            correct_nums_and_positions(j)
            j = token_num + 1
            correct_next_tokens(j)
            #  корректируем длину предложения
            self.stop = self.stop + text.__len__() - 1
        return sen_word

    def replace_word(self, text1, text2):
        # удаляем все прошлые слова в предложении
        starts, token_nums, word_list_nums = self.remove_word(text1)
        # добавляем новые слова во все удаленные пробелы
        sen_word = self.add_words(text2, starts, word_list_nums, token_nums)
        # отмечаем добавленные слова в словаре
        if self.words.get(hash(text2)):
            self.words[hash(text2)].rating += 1
        else:
            self.words[hash(text2)] = copy.deepcopy(sen_word)

        #  correct_vivo
        relation_dict = copy.deepcopy(self.vivo.relations)
        for relation_name in self.vivo.relations.keys():
            relation = relation_dict[relation_name]
            if relation.text1 == text1:
                relation_dict.pop(relation_name)
                new_relation = Relation(relation.text2, text2.upper(), rating=1)
                relation_dict[Relation.get_relation_text(relation.text2, text2.upper())] = new_relation
            elif relation.text2 == text1:
                relation_dict.pop(relation_name)
                new_relation = Relation(relation.text1, text2.upper(), rating=1)
                relation_dict[Relation.get_relation_text(relation.text1, text2.upper())] = new_relation
        self.vivo = Vivo(relations=relation_dict.values())
        return sen_word

    def clear_puctuation_marks(self):
        punctuation_list = Token.punctuation_list
        normal_token_dict = dict([hash(token.text), token] for token in self.normal_tokens)
        for mark in punctuation_list:
            if normal_token_dict.get(hash(mark)):
                self.remove_word(mark)

    # ------------------------------------------------------------------------------------------------------------------

    #  Сравнения с другими предложениями
    # ------------------------------------------------------------------------------------------------------------------

    def part_of(self, other):
        """
        self является частью other
        ноль получается при условии, что other не содержит ни одного слова из self
        единица - если все слова self присутствуют в other
        """
        general_rating = sum(word.rating for word in self.words.values())
        coincedence = float(0)
        for word in self.words.values():
            if other.words.get(hash(word.text)):
                coincedence += word.rating / general_rating
        return coincedence

    def word_compare(self, other):
        self_coincidence = self.part_of(other)
        other_coincidence = other.part_of(self)
        # general_rating = sqrt(other_coincidence * self_coincidence)
        general_rating = (other_coincidence + self_coincidence) / 2
        return general_rating

    def compare(self, other):
        if any([self.vivo is None, other.vivo is None]):
            return self.word_compare(other)
        else:
            return self.vivo.sum_compare(other.vivo)

    # ------------------------------------------------------------------------------------------------------------------

    # получение компонентов из предложения
    # ------------------------------------------------------------------------------------------------------------------
    def get_normal_form_token(self, token_num):
        start = self.tokens[token_num].start
        for norm_token in self.normal_tokens:
            if norm_token.start == start:
                return norm_token.text
        return None

    # ------------------------------------------------------------------------------------------------------------------

    # внутренние операции
    # ------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def _recognise_tokens(sentence_text):
        """Выделение токенов из предложенного текста"""
        tokens = NatashaSent.divide_sentence_text_to_tokens(sentence_text)
        return tokens

    # ------------------------------------------------------------------------------------------------------------------


if __name__ == "__main__":
    text1 = "я люблю есть сыр"
    text2 = "я люблю сыр с плесенью"

    sentence1 = Sentence.initial_from_sentence_text(text1)
    sentence2 = Sentence.initial_from_sentence_text(text2)
    proximity = sentence1.compare(sentence2)

    pass
    # sentence1.remove_word(".")
