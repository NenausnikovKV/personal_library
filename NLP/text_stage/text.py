# coding: utf-8

"""Модуль хранения согласия и входящих в него объектов"""
from NLP.external_analizer.natasha_sent import NatashaSent
from NLP.sentence_stage.sentence import Sentence
from NLP.token_stage.word import TextWord



class Text:
    """
    Текст целиком, предложения, слова, токены
    и методы их получения и обработки в контексте целого текста
    """

    #  подтягиваем внешние библиотеки для обработки естественного языка

    def __init__(self, text, sentences, words, number=-1):
        self.text = text
        self.sentences = sentences
        self.words = words
        self.number = number


    @classmethod
    def get_text_object_from_text(cls, file_text, number=-1):
        """
        Дополнительный конструктор
        """
        sentences = cls.recognise_sentences(file_text)
        words = cls._get_words_of_all_sentences(sentences)
        return cls(file_text, sentences, words, number)


    def __str__(self):
        return "text " + str(self.number)

    def __lt__(self, other):
        return len(self.sentences) < len(other.sentences)


    def remove_word(self, text):
        self.words.pop(hash(text))
        for sentence in self.sentences.values():
            if sentence.words.get(hash(text)):
                start, stop = sentence.remove_word(text)
                for i in range(start.__len__()):
                    text_start = sentence.start + start[i]
                    text_stop = sentence.start + stop[i]
                    self.text=self.text[:text_start]+self.text[text_stop:]

    def replace_word(self, word_text1, word_text2):
        # удаляем перове слово из словаря
        self.words.pop(hash(word_text1))
        sen_num = 0
        for sentence in self.sentences.values():
            if sentence.words.get(hash(word_text1)):
                # удаляем первое слово, получаем положение и заполняем его новым словом
                sen_word = sentence.replace_word(word_text1, word_text2)
                # отмечаем изменения в словаре текста
                if self.words.get(hash(word_text2)):
                    word = self.words.get(hash(word_text2))
                    word.rating += 1
                else:
                    self.words[hash(word_text2)] = TextWord(sen_word)

                # корректировка смещения предложений при изменении внутри них слов
                sentence_keys = list(self.sentences.keys())
                j = sen_num + 1
                if j < self.sentences.__len__():
                    next_sentence =  self.sentences[sentence_keys[j]]
                    diff =  sentence.stop -(next_sentence.start-1)
                    while j < self.sentences.__len__():
                        sentence =  self.sentences[sentence_keys[j]]
                        sentence.start += diff
                        sentence.stop += diff
                        j += 1
            # наконец, вписываем текст
            sen_num += 1
        text = ""
        for sentence in self.sentences.values():
            text = text + sentence.text
        self.text = text

    @classmethod
    def _get_words_of_all_sentences(clc, sentences):
        all_sentences_words = {}
        for sentence in sentences.values():
            for word_hash, sen_word in sentence.words.items():
                if not all_sentences_words.get(word_hash):
                    all_sentences_words[word_hash] = TextWord(sen_word)
                else:
                    all_sentences_words[word_hash].involve_new_source(sentence.words[word_hash])
        return all_sentences_words


    @classmethod
    def recognise_sentences(clc, file_text):
        """
        Выделяем тексты предложений и создаем экземпляры предложений
        """
        natasha_sents = NatashaSent.divide_text_to_natasha_sents(file_text)
        sentences = {}
        for num, sent in enumerate(natasha_sents):
            key = hash(sent.text)
            sentences[key] = NatashaSent._get_sentence_from_natasha_sent(sent, sent.start, num)
        return sentences



