import copy
import re
from collections import namedtuple

from NLP import processing_plain_text
from NLP.text_stage.text import Text
from NLP.processing_plain_text import safe_preprocessing
from file_processing.file_processing import get_general_address, get_anthology_elements
from legal_tech.excerts.vivo_sentence import VivoSentence


class Agreement(Text):

    def __init__(self, text_object):
        super().__init__(text_object.text, text_object.sentences, text_object.words, number=0)
        # превращение предложений в виво предложения     
        self.vivo_sentences = dict()
        for sentence_key, sentence in self.sentences.items():
            self.vivo_sentences[sentence_key] = VivoSentence.get_syntactical_vivo_sentence_from_sentence(sentence)
        del self.sentences


    @classmethod
    def get_agreement_from_text(cls, text):
        # text = Agreement.preprocessing(text)
        text_object = Text.get_text_object_from_text(text)
        agreement = Agreement(text_object)
        # agreement.replace_elements()
        return agreement

    @staticmethod
    def get_agreement_texts(file_text):
        """
        Получение соглашений из текста на основе шаблона их названий
        """
        agrement_start_sample = r"\wогласие\b\s+\d+"
        agreement_texts = re.split(agrement_start_sample, file_text)
        agreement_texts = [text for text in agreement_texts if text != ""]

        return agreement_texts

    def replace_element_list(self, elements, replacement_word):
        for element_text in elements:
            if self.words.get(hash(element_text)):
                self.replace_word(element_text, replacement_word)


    @staticmethod
    def preprocessing(text):
        """
        Простейшее изменение, использую для заглушки, только те которые легко откатить, но которые необходимы для
        деления текста
        """
        text = text.replace("\n", " ")
        text = text.replace("..", ".")
        return text

    @staticmethod
    def safe_preprocessing(text):
        """
        Предобработка без изменения длины текста
        """
        # удаляем переносы строк
        text = text.replace("\n", " ")
        # выравниваем регистр
        return text

    def replace_elements(self):
        address = get_general_address("in/anthology/countries")
        countries = get_anthology_elements(address)
        address = get_general_address("in/anthology/data")
        datas = get_anthology_elements(address)

        # при применении данного метода становится необходимо изменять его синтаксическую структуру,
        # а пока я этого не далаю
        # self.replace_element_list(countries, "[страна]")
        # self.replace_element_list(datas, "[данные]")



if __name__ == "__main__":


    # text = "фамилия, имя"
    text = "Перечень персональных данных, на обработку которых дается согласие субъекта персональных данных.  " \
           "Фамилия / фамилия при рождении, имя, отчество; дата рождения; место рождения; государство рождения. " \
           "Гражданство/гражданство при рождении; пол; семейное положение; для несовершеннолетних: фамилия, имя. " \
           "Отчество, адрес и гражданство опекуна/законного представителя; домашний адрес; сведения о регистрации. " \
           "Номер телефона; адрес электронной почты; паспортные данные: серия, номер кем выдан, дата выдачи; данные. " \
           "Внутреннего паспорта; данные свидетельства о рождении; данные о документе на пребывание в РФ; профессия.  " \
           "Доходы; название и адрес места работы/ учебного заведения; рабочий телефон; фамилия и имя приглашающего. " \
           "Лица; название приглашающей фирмы/организации/учебного заведения; название гостиницы; адрес приглашающей. " \
           "Стороны; номер телефона, факса, адрес электронной почты приглашающей стороны; биометрические данные: " \
           "Фотография, отпечатки пальцев."

    text_object =  Text.get_text_object_from_text(text)
    agreement = Agreement(text_object)
    agreement.replace_elements()
    a=9



