"""Предложения согласия и входящих в него объектов"""
import copy

from yargy.tokenizer import MorphTokenizer

from NLP.dictionary_library.morphDictionary import MorphDictionary
from NLP.token_stage.word import Word, SentenceWord
from NLP.token_stage.personal_token import SentenceToken, Token


class Sentence:
    """Предложение"""

    def __init__(self, text, tokens, normal_tokens, word_list, sentence_words, num=-1, start=-1):

        self.text = text
        self.num = num

        self.start = start
        self.stop = start + self.text.__len__()

        self.tokens = tokens
        #
        self.normal_tokens = normal_tokens
        self.word_list = word_list
        self.words = sentence_words

    def __add__(self, other):

        result = copy.deepcopy(self)
        result.text = result.text + " \n" + other.text
        result.tokens.extend(other.tokens)
        result.word_list.extend(other.word_list)
        for key in other.words.keys():
            if not result.words.get(key):
                result.words[key] = other.words[key]

        result.start = None
        result.num = None
        result.stop = None
        return result

    # Перегруженные стандартные методы
    def __str__(self):
        return self.text

    # Перегруженные стандартные методы
    def __repr__(self):
        return self.text

    def __eq__(self, other):
        return self.text == other.text

    @staticmethod
    def get_token_normal_form(self, token_num):
        start = self.tokens[token_num].start
        for norm_token in self.normal_tokens:
            if norm_token.start == start:
                return norm_token.text
        return None
        # count = 0
        # for self_token in self.tokens:
        #     if self_token.text == token.text:
        #         count += 1
        # for i in range(count):

        #
        # count = self.normal_tokens.count(token)
        # if count>1:
        #     self.normal_tokens.index(token)


    def compare(self, other):
        max_len = max(self.words.__len__(), other.words.__len__())
        counter = 0
        for word in self.words.values():
            counter = counter + 1 if other.words.get(hash(word.text)) else counter
        proximity = counter / max_len
        return proximity

    @staticmethod
    def get_words(word_list):
        words = {}
        for word in word_list:
            if not words.get(hash(word.text)):
                words[hash(word.text)] = copy.deepcopy(word)
            else:
                words[hash(word.text)].rating += word.rating
        return words

    @staticmethod
    def recognise_tokens(sentence_text, tokenizer):
            """Выделение токенов из предложенного текста"""

            def define_type(word_text):
                if word_text in list(Token.punctuation_list):
                    python_type = "punctuation"
                elif word_text.isdigit():
                    python_type = "digit"
                else:
                    python_type = "word"
                return python_type

            sentence_text = sentence_text.replace('\n', ' ')
            tokens = []
            for token in tokenizer(sentence_text):
                tokens.append(SentenceToken(token.value, define_type(token.value), start=token.span.start, stop=token.span.stop))
            return tokens

    @staticmethod
    def get_normal_elements(sen_tokens, morph, sentence_text):
            """список слов в родном порядке"""
            word_tokens = [sen_token for sen_token in sen_tokens if sen_token.type == "word"]

            word_texts = [word_token.text for word_token in word_tokens]
            normal_words = morph.parse(word_texts)

            """список токенов в родном порядке"""
            normal_tokens = []
            counter = 0
            for sen_token in sen_tokens:
                if counter < word_tokens.__len__() and sen_token.text == word_tokens[counter].text:
                    normal_token = SentenceToken(normal_words[counter].lemma, type="word",
                                                 start=sen_token.start, stop=sen_token.stop)
                    normal_tokens.append(normal_token)
                    counter = counter+1
                else:
                    normal_tokens.append(copy.deepcopy(sen_token))

            """список слов в родном порядке"""
            sentence_words = []
            for i in range(word_texts.__len__()):
                sen_token = word_tokens[i]
                normal_word = normal_words[i]
                sen_word = SentenceWord(
                    sen_token, normal_word.lemma, speech_part=normal_word.tag.pos, grammemes=normal_word.tag,
                    rating=1, num=i, source_sentence_text=sentence_text)
                sentence_words.append(sen_word)

            return normal_tokens, sentence_words

    def remove_word(self, word_text):

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
                    self.text = self.text[:token.start] + self.text[token.stop:]
                    self.stop = self.stop - word_text.__len__()

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

        # удаляем все повторения  из списка слов
        word_list_nums = remove_from_word_list()
        # удаляем все повторения из списка токенов
        starts, token_nums = remove_from_token_list()

        # удаляем из словаря
        if self.words.get(hash(word_text)):
            self.words.pop(hash(word_text))

        return starts, token_nums, word_list_nums

    def add_words(self, text, starts, word_list_nums, token_nums):

        def correct_nums_and_positions(num):
            while num < token_nums.__len__():
                if starts[num] > start:
                    starts[num] += text.__len__()
                    token_nums[num] +=1
                    word_list_nums[num] += 1
                num += 1

        def correct_next_tokens(j):
            text_len = text.__len__()-1
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
            new_sen_token = SentenceToken(text, type="word", start=start, stop=stop)
            self.tokens.insert(token_num, new_sen_token)
            self.normal_tokens.insert(token_num, new_sen_token)

            # встраиваем слово в список слов
            sen_word = SentenceWord(new_sen_token, text, num=word_list_num, rating=1)
            self.word_list.insert(word_list_num, sen_word)

            # вписывани е слова в предложение
            self.text = self.text[:start] + text + self.text[start:]



            # корректируем следующие слова для вставки
            j = i+1
            correct_nums_and_positions(j)
            j = token_num + 1
            correct_next_tokens(j)
            #  корректируем длину предложения
            self.stop = self.stop + text.__len__()-1
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
            return sen_word

    @staticmethod
    def initial_sentence(sentence_text, number=-1, start=-1, tokenizer=MorphTokenizer(), morph=MorphDictionary()):
        sen_tokens = Sentence.recognise_tokens(sentence_text, tokenizer)  # {}
        normal_tokens, word_list = Sentence.get_normal_elements(sen_tokens, morph, sentence_text)
        words = Sentence.get_words(word_list)
        return Sentence(sentence_text, sen_tokens, normal_tokens, word_list, words, number, start)


if __name__ == "__main__":
    text = "Привет, поговорим."
    sentence = Sentence.initial_sentence(text)
    sentence.remove_word(".")
    a=0

