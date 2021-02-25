import re
from collections import namedtuple

from natasha import NewsEmbedding, Segmenter, NewsMorphTagger, NewsSyntaxParser
from yargy.tokenizer import MorphTokenizer

from NLP.dictionary_library.morphDictionary import MorphDictionary
from NLP.document_stage.text import Text
from NLP.processing_plan_text import preprocessing
from file_processing.file_processing import get_general_address, get_anthology_elements


class Agreement(Text):

    def __init__(self, text_object):
        super().__init__(text_object.text, text_object.sentences, text_object.words, number=0)
    
    @classmethod
    def get_agreement_from_text(cls, text):
        text = preprocessing(text)
        text_object = Text.get_text_object_from_text(text)
        agreement = cls(text_object)
        agreement.replace_elements()
        return agreement

    @staticmethod
    def get_agreement_texts(file_text):
        """
        Получение соглашений из текста на основе шаблона их названий
        """
        agrement_start_sample = r"\wогласие\b\s+\d+"
        agreement_texts = re.split(agrement_start_sample, file_text)
        i = 0
        for text in agreement_texts:
            if text == "":
                agreement_texts.pop(i)
            i += 1
        return agreement_texts

    def replace_element_list(self, elements, replacement_word):
        for element_text in elements:
            if self.words.get(hash(element_text)):
                self.replace_word(element_text, replacement_word)



    def replace_elements(self):
        address = get_general_address("in/anthology/countries")
        countries = get_anthology_elements(address)
        address = get_general_address("in/anthology/data")
        datas = get_anthology_elements(address)

        self.replace_element_list(countries, "[страна]")
        self.replace_element_list(datas, "[данные]")
        a=0



if __name__ == "__main__":
    SynAnaliser = namedtuple("SynAnaliser", ["segmenter", "morph_tagger", "syntax_parser"])
    tokenizer = MorphTokenizer()
    morph = MorphDictionary()
    ebd = NewsEmbedding()
    syntax_analizer = SynAnaliser(segmenter=Segmenter(), morph_tagger = NewsMorphTagger(ebd),
                                         syntax_parser = NewsSyntaxParser(ebd) )


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

    text_object =  Text.get_text_object_from_text(text, syn_analizer=syntax_analizer, morph=morph)
    agreement = Agreement(text_object)
    agreement.replace_elements()
    a=9



