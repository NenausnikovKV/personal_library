"""Предложения согласия и входящих в него объектов"""




import copy
from operator import attrgetter

from natasha import Doc

from NLP.syntax_analyzer import SyntaxAnalyzer
from NLP.token_stage.word import SentenceWord
from NLP.token_stage.personal_token import SentenceToken, Token
from graph_representation.relation import Relation
from graph_representation.vivo import Vivo


class Sentence:
    def __init__(self, sen_text, tokens, normal_tokens, word_list, sen_words, syn_vivo=None, num=-1, start=-1):
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
    def initial_from_text(cls, sentence_text, number=-1, start=-1, ):
        sent = SyntaxAnalyzer.get_sent_from_sentence_text(sentence_text)
        sen_tokens = cls._recognise_tokens(sentence_text)  # {}
        normal_tokens, word_list = cls.get_normal_elements(sen_tokens, sentence_text)
        words = cls.get_words(word_list)
        return cls(sen_text=sentence_text, tokens=sen_tokens, normal_tokens=normal_tokens, word_list=word_list,
                   sen_words=words, num=number, start=start)

    @classmethod
    def initial_from_sentence_text(cls, sentence_text, number=-1, start=-1, ):
        sent = SyntaxAnalyzer.get_sent_from_sentence_text(sentence_text)
        sentence = cls.initial_from_natasha_sent(sent, number)
        # todo перепись переменной start неочевидн, прописать более очевидный способ записи
        sentence.start = start
        return sentence

    @classmethod
    def initial_from_natasha_sent(cls, sent, number=-1):

        def get_tokens(sent_tokens, sentence_start):
            tokens = []
            for num, token in enumerate(sent_tokens):
                tokens.append(SentenceToken(token.text, Token.define_type(token.text), num=num,
                                            start=token.start - sentence_start, stop=token.stop - sentence_start))
            return tokens

        def get_syntax_vivo(sent_tokens, sentence_tokens):
            """
            переписываем связанные слова после работы синтаксического анализитора
            """

            head_id_sorted_tokens = sorted(sent_tokens, key=attrgetter("head_id"))
            token_dict = {token.id: token for token in sent_tokens}

            relations = []
            for token in head_id_sorted_tokens:
                # 0 связан с корнем древа
                if token.head_id == 0:
                    continue

                # смещение на 1 так как 0 - это корень синтаксического древа
                token1 = token
                text1 = Sentence.find_normal_token_text(sentence_tokens[token1.id - 1], normal_tokens)
                token2 = token_dict[token.head_id]
                text2 = Sentence.find_normal_token_text(sentence_tokens[token2.id - 1], normal_tokens)
                if all([Token.define_type(text1) == "word", Token.define_type(text2) == "word", token1.id != token2.id]):
                    relations.append(Relation(text1, text2, rating=1))
            return Vivo(relations=relations)

        # sent.syntax.print()
        sentence_tokens = get_tokens(sent.tokens, sent.start)
        normal_tokens, word_list = Sentence.get_normal_elements(sentence_tokens, sentence_text=sent.text)
        words = Sentence.get_words(word_list)
        syn_vivo = get_syntax_vivo(sent.tokens, sentence_tokens)
        sentence = cls(sent.text, sentence_tokens, normal_tokens, word_list, words, syn_vivo, num=number,
                                  start=sent.start)
        return sentence


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
        try:
            result.vivo = result.vivo + other.vivo
        except:
            pass

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
        return Sentence.initial_from_text(new_text)

    def __str__(self):
        return self.text

    def __eq__(self, other):
        return self.text == other.text

    def get_token_normal_form(self, token_num):
        start = self.tokens[token_num].start
        for norm_token in self.normal_tokens:
            if norm_token.start == start:
                return norm_token.text
        return None


    @staticmethod
    def find_normal_token_text(token, normal_tokens):
        start = token.start
        for norm_token in normal_tokens:
            if norm_token.start == start:
                return norm_token.text
        return None

    @staticmethod
    def old_find_token_normal_forms(tokens, normal_tokens, token_num):
        start = tokens[token_num].start
        for norm_token in normal_tokens:
            if norm_token.start == start:
                return norm_token.text
        return None

    def part_of(self, other):
        """
        self является частью other
        ноль получается при условии, что other не содержит ни одного слова из self
        единица - если все слова self присутствуют в other
        """
        general_rating =  sum(word.rating for word in self.words.values())
        coincedence = float(0)
        for word in self.words.values():
            if other.words.get(hash(word.text)):
                coincedence += word.rating/general_rating
        return coincedence

    def word_sum_compare(self, other):
        self_coincidence = self.part_of(other)
        other_coincidence = other.part_of(self)
        # general_rating = sqrt(other_coincidence * self_coincidence)
        general_rating = (other_coincidence + self_coincidence)/2
        return general_rating

    def compare(self, other):
        if any([self.vivo is None, other.vivo is None]):
            return self.word_sum_compare(other)
        else:
            return self.vivo.sum_compare(other.vivo)


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
    def define_type(word_text):
        if word_text in list(Token.punctuation_list):
            token_type = "punctuation"
        elif word_text.isdigit():
            token_type = "digit"
        else:
            token_type = "word"
        return token_type

    @classmethod
    def _recognise_tokens(cls, sentence_text):
        """Выделение токенов из предложенного текста"""
        sen_tokens = SyntaxAnalyzer.divide_sentence_text_to_tokens(sentence_text)
        tokens = []
        stop = 0
        for token_num, token in enumerate(sen_tokens):
            start = sentence_text.find(token.text, stop)
            stop = start + len(token.text)
            sen_token = SentenceToken(token.text, Token.define_type(token.text), num=token_num, start=start, stop=stop)
            tokens.append(sen_token)
        return tokens

    @staticmethod
    def convert_token_to_my_view(analizer_tokens, sentence_start):
        tokens = []
        for num, token in enumerate(analizer_tokens):
            tokens.append(SentenceToken(token.text, Token.define_type(token.text), num=num,
                                        start=token.start-sentence_start, stop=token.stop-sentence_start))
        return tokens

    @staticmethod
    def get_normal_elements(sen_tokens, sentence_text):
            """список слов в родном порядке"""
            word_tokens = [sen_token for sen_token in sen_tokens if sen_token.type == "word"]

            word_texts = [word_token.text for word_token in word_tokens]
            normal_words = SyntaxAnalyzer.morph_dict.parse(word_texts)


            """список токенов в родном порядке"""
            normal_tokens = []
            counter = 0
            for num, sen_token in enumerate(sen_tokens):
                if counter < word_tokens.__len__() and sen_token.text == word_tokens[counter].text:
                    normal_token = SentenceToken(normal_words[counter].lemma, type="word", num=num,
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
            new_sen_token = SentenceToken(text, type="word", num=token_num,  start=start, stop=stop)
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

    def get_sentence_vivo(self):

        copy_sentence = copy.deepcopy(self)
        # copy_sentence.clear_puctuations()

        # обработка поступившего текста
        doc = Doc(copy_sentence.text)
        doc.segment(SyntaxAnalyzer.segmenter)
        doc.tag_morph(SyntaxAnalyzer.morph_tagger)
        doc.parse_syntax(SyntaxAnalyzer.syntax_parser)
        sent = doc.sents[0]


        tokens = list(sent.syntax.tokens)
        for token in tokens:
            token.head_id = int(str(token.head_id).split("_")[1])
            token.id = int(str(token.id).split("_")[1])
        head_id_tokens = sorted(tokens, key=attrgetter("head_id"))
        token_dict = dict([token.id, token] for token in tokens)

        relations = []
        count = 0
        for token in head_id_tokens:
            count += 1
            # смещение на 1 так как 0 - это корень
            token1 = token
            text1 = Sentence.get_token_normal_form(copy_sentence, token1.id - 1)
            # 0 связан с корем древа
            if token.head_id == 0:
                continue
            token2 = token_dict[token.head_id]
            text2 = Sentence.get_token_normal_form(copy_sentence, token2.id - 1)

            relation = Relation(text1, text2, rating=1)
            relations.append(relation)
        sentence_vivo = Vivo(relations=relations)
        sentence_vivo.clear_punctuation_marks()
        self.vivo = sentence_vivo


if __name__ == "__main__":
    text1 = "я люблю есть сыр"
    text2 = "я люблю сыр с плесенью"

    sentence1 = Sentence.initial_from_text(text1)
    sentence2 = Sentence.initial_from_text(text2)

    # sentence1.get_sentence_vivo()
    # sentence2.get_sentence_vivo()

    proximity = sentence1.compare(sentence2)

    pass
    # sentence1.remove_word(".")

