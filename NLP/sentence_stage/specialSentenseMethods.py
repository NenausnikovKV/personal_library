# методы сравнения, разделения и сложения
def compare(self, other_sentence):
    """Сравнивает 2 предложения на основе входящизх в него слов"""

    def filter_function(candidate_word):
        if candidate_word not in self.word_collection.dictionary.object:
            return 1
        else:
            return 0

    rating = 0
    for word in self.words.word_dictionary:
        if word in other_sentence.words.dictionary:
            rating += (word.rating + other_sentence.words.dictionary[word.normal_form].rating) % 2
    valuation = rating / len(other_sentence.words.dictionary)
    other_words = list(filter(filter_function, other_sentence.words))  # оставшиеся, не совпавшие слова
    return valuation


def part_of(self, other_sentence):
    """Определяет насколько одно предложение входит (повторяется в другом) в другое"""

    rating = 0
    for word in self.words.word_dictionary:
        if word in other_sentence.words.dictionary:
            rating += 1
    valuation = rating / len(self.words.word_dictionary)

    return valuation


def can_be_share(self, other_sentence):
    def filter_function(candidate_word):
        if candidate_word not in self.words.word_dictionary:
            return 1
        else:
            return 0

    valuation = self.part_of(other_sentence)
    if valuation < 0.8:
        return False
    other_words = dict(filter(filter_function, other_sentence.words.dictionary))  # оставшиеся, не совпавшие слова


def sentence_share_attempt(self, words, other_words):
    # проверка на пересечение слов
    word_flag = False
    other_word_flag = False
    result = -1
    for word in self.word_list:
        if word.normal_form in words:
            word_flag = True
            if other_word_flag:
                other_word_flag = False
                result += 1
        elif word.normal_form in other_words and not word_flag:
            other_word_flag = True
            if word_flag:
                word_flag = False
                result += 1
    return bool(result)

#
# def divide_into_two_parts(self):
#     """Разделение текста на 2 части"""
#     token_first_part = self.tokens[:int(len(self.tokens) / 2)]
#     token_second_part = self.tokens[int(len(self.tokens) / 2):]
#     new_first_sentence = Sentence(self.agreement, token_first_part)
#     new_second_sentence = Sentence(self.agreement, token_second_part)
#     return new_first_sentence, new_second_sentence
#
