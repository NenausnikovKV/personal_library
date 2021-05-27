# coding: utf-8

"""Модуль хранения согласия и входящих в него объектов"""
from NLP.external_analizer.sentence_analizer.natasha_sent import NatashaSent
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



    # ------------------------------------------------------------------------------------------------------------------

    @classmethod
    def _recognise_sentences(clc, file_text):
        """
        Выделяем тексты предложений и создаем экземпляры предложений
        """
        sentences = NatashaSent.divide_text_to_sentences(file_text)
        return sentences

    @classmethod
    def _get_text_word_dict(clc, sentences):
        all_sentences_words = {}
        for sentence in sentences:
            for word_hash, sen_word in sentence.words.items():
                if not all_sentences_words.get(word_hash):
                    all_sentences_words[word_hash] = TextWord(sen_word)
                else:
                    all_sentences_words[word_hash].involve_new_source(sentence.words[word_hash])
        return all_sentences_words

    @classmethod
    def get_text_object_from_text(cls, file_text, number=-1):
        """
        Дополнительный конструктор
        """
        sentence_list = cls._recognise_sentences(file_text)
        words = cls._get_text_word_dict(sentence_list)
        sentence_dict = {hash(sentence.text): sentence for sentence in sentence_list}

        return cls(file_text, sentence_dict, words, number)

    # ------------------------------------------------------------------------------------------------------------------
    def __str__(self):
        return "text " + str(self.number)

    # ------------------------------------------------------------------------------------------------------------------
    def remove_word(self, word_text):
        self.words.pop(hash(word_text))
        for sentence in self.sentences.values():
            if sentence.words.get(hash(word_text)):
                start, stop = sentence.remove_word(word_text)
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

    # ------------------------------------------------------------------------------------------------------------------


if __name__ == "__main__":
    file_text = "Я люблю сыр с плесенью. В этом есть что-то благородное."
    text_objecct = Text.get_text_object_from_text(file_text)
    a = 89


