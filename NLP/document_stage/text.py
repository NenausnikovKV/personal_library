# coding: utf-8

"""Модуль хранения согласия и входящих в него объектов"""
import copy

import razdel
from yargy.tokenizer import MorphTokenizer

from NLP.dictionary_library.morphDictionary import MorphDictionary
from NLP.sentence_stage.sentence import Sentence
from NLP.token_stage.word import TextWord


class Text:
    """
    Текст целиком, предложения, слова, токены
    и методы их получения и обработки в контексте целого текста
    """
    number = 0

    def __init__(self, text, sentences, words, number=0, corpus_source=None):
        self.text = text
        self.sentences = sentences
        self.words = words
        self.number = number
        self.corpus = corpus_source

    def __str__(self):
        return "text " + str(self.number)

    def __lt__(self, other):
        return len(self.sentences) < len(other.sentences)

    @staticmethod
    def preprocessing(text):
        i = 2
        while i < text.__len__():
            if text[i - 1] == "\n" and text[i].isupper():
                text = text[:i -1] + ". " + text[i:]
            i += 1
        text = text.replace("\n", " ")
        text = text.replace("Ф.И.О.", "ФИО")
        return text

    def remove_word(self, text):
        self.words.pop(hash(text))
        for sentence in self.sentences.values():
            if sentence.words.get(hash(text)):
                start, stop = sentence.remove_word(text)
                for i in range(start.__len__()):
                    text_start = sentence.start + start[i]
                    text_stop = sentence.start + stop[i]
                    self.text=self.text[:text_start]+self.text[text_stop:]


    def replace_word(self, text1, text2):
        # удаляем перове слово из словаря
        self.words.pop(hash(text1))
        sen_num = 0
        for sentence in self.sentences.values():
            if sentence.words.get(hash(text1)):
                # удаляем первое слово, получаем положение и заполняем его новым словом
                sen_word = sentence.replace_word(text1, text2)

                # отмечаем изменения в словаре
                if self.words.get(hash(text2)):
                    word = self.words.get(hash(text2))
                    word.rating += 1
                else:
                    self.words[hash(text2)] = TextWord(sen_word)

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




    @staticmethod
    def get_words_of_all_sentences(sentences):
        all_sentences_words = {}
        for sentence_hash in sentences:
            sentence = sentences[sentence_hash]
            for key in sentence.words:
                sen_word = sentence.words[key]
                if not all_sentences_words.get(key):
                    all_sentences_words[key] = TextWord(sen_word)
                else:
                    all_sentences_words[key].involve_new_source(sentence.words[key])
        return all_sentences_words



    @staticmethod
    def recognise_sentences(file_text, tokenizer, morph):
        """Синтаксическое выделение предложений из текста"""
        sentences = {}
        num = 0
        for sentence in razdel.sentenize(file_text):
            key = hash(sentence.text)
            sentences[key] = Sentence.initial_sentence(sentence.text, num, sentence.start, tokenizer, morph)
            num += 1
        return sentences

    @staticmethod
    def get_text_object(file_text, number=0, corpus_source=None, tokenizer=MorphTokenizer(), morph=MorphDictionary()):
        sentences = Text.recognise_sentences(file_text, tokenizer, morph)
        words = Text.get_words_of_all_sentences(sentences)
        return Text(file_text, sentences, words, number, corpus_source)

