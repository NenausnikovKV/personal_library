import os
import re

from NLP.token_stage.personal_token import Token




def simple_preprocessing(text):
    i = 2
    while i < text.__len__():
        if text[i - 1] == "\n" and text[i].isupper():
            text = text[:i - 1] + ". " + text[i:]
        i += 1
    text = text.replace("\n", " ")
    text = text.replace("Ф.И.О.", "ФИО")
    text = text.replace("..", ".")
    return text

def hard_preprocessing(text):
    # убираем предложения написанные капсом - во все словах все кроме первой буквы переводятся в нижний регистр
    # буква остается в верхнем регистре только в  случае если она первая слове и уже была в верхнем регистре
    # text = correct_register(text)
    # очищаем большие буквы внутри предложений
    # все, кроме первой буквы и буквы после перепноса строки переводятся в нижний регистр
    # буква остается в верхнем регистре только в  случае если она первая в предложении или строке и уже была в верхнем регистре

    # удаляем переносы строк
    # matches = re.findall(r'^[^\w+]', text)
    # for match in matches:
    #     text = text.replace(match, " ")

    text = text.replace("Ф.И.О.", "фио")
    text = text.replace("ФИО", "фио")
    # text = correct_plan_text_list(text)
    text = text.replace("\n", " ")
    # text = _line_break_processing(text)
    # text = re.sub(r"\d\.")
    # sentence_texts = SyntaxAnalyzer.divide_text_to_sentence_plan_texts(text)
    # sentence_texts = unit_upper_case_register_sequence_sentence(sentence_texts)
    # sentence_texts = [_correct_sentence_register(sentence) for sentence in sentence_texts]
    # text = " ".join(sentence_texts)
    text = text.replace("..", ".")
    return text

def clear_puctuations(sentence):
    """
    Удаляем все знаки препинания
    """
    punctuation_list = Token.punctuation_list
    normal_token_dict = dict([hash(token.text), token] for token in sentence.normal_tokens)
    for mark in punctuation_list:
        if normal_token_dict.get(hash(mark)):
            sentence.remove_word(mark)

def unit_upper_case_register_sequence_sentence(sentence_texts):
    num = 1
    while num < len(sentence_texts):
        sentence_text1 = sentence_texts[num]
        sentence_text2 = sentence_texts[num - 1]
        if sentence_text1.isupper() and sentence_text2.isupper():
            sentence_texts.pop(num)
            sentence_texts[num-1] = sentence_text1 + sentence_text2
        num+=1
    return sentence_texts


def correct_register(text):
    # все слова в верзнем регистре переводятся в верхний регистр первая буква слова
    lines = text.split("\n")
    new_lines = []
    for line in lines:
        words = []
        for word in line.split(" "):
            if len(word)>1:
                word = word[0] + word[1:].lower()
            words.append(word)
        new_lines.append(" ".join(words))
    text = "\n".join(new_lines)
    return text

def _correct_sentence_register(sen_text):
    # делим предложения если есть переносы строк
    lines = sen_text.split("\n")

    # Склеиваем строки, если они целиком в верхнем регистре
    num = 1
    while num < len(lines):
        sentence_text1 = lines[num-1]
        sentence_text2 = lines[num]
        if sentence_text1.isupper() and sentence_text2.isupper():
            lines[num - 1] = sentence_text1 + " " + sentence_text2
            lines.pop(num)
            continue
        num+=1

    for num, line in enumerate(lines):
        if(len(line)):
            text1 = line[0]
            text2 = line[1:].lower()
            lines[num] = line[0] + line[1:].lower()
    text = "\n".join(lines)
    return text

def _line_break_processing(text):
    # определение переноса строки, как конец предложения по трем символам
    #  после переноса строки проверяем наличие верхнего решистра и его отсутствие во втором символе
    i = 3
    while i < text.__len__():
        if all([text[i-2] == "\n", text[i-1].isupper(), not text[i].isupper()]):
            text1 = text[:i - 2]
            text2 = text[i-1:]
            text = text[:i - 2] + ". " + text[i-1:]
        i+=1
    #  удаление переносов не удовлетворивших условию
    text = text.replace("\n", " ")
    return text

def correct_plan_text_list(text):
    # 1) or 1.
    matches = list(re.findall(r"\d\).*\n", text)) + list(re.findall(r"\d\..*\n", text))
    for element in set(matches):
        new_element = element[2:-1]
        text = text.replace(element, new_element)
    return text

def remove_punctuatin_mark(text):
    punctuation_list = Token.punctuation_list
    for mark in punctuation_list:
        index = text.find(mark)
        if index>=0:
           text = text[0, index] + text[index+1, -1]
    return text

def safe_remove_digital(text):
    new_text = re.sub('\d', ' ', text)
    return new_text

def safe_preprocessing(text):
    """
    Предобработка без изменения длины текста
    """
    # удаляем цифры
    text = safe_remove_digital(text)
    # удаляем переносы строк
    text = text.replace("\n", " ")
    # выравниваем регистр
    return text

if __name__ == "__main__":
    print(os.path.abspath("test1"))
    with open("test", "r", encoding="utf-8") as file:
        text = file.read()
    text = safe_preprocessing(text)
    print(text)



def get_agreements(file_text):
    agrement_start_sample = r"\wогласие\b\s+\d+"
    agreement_texts = re.split(agrement_start_sample, file_text)
    i = 0
    for text in agreement_texts:
        if text == "":
            agreement_texts.pop(i)
        i += 1
    return agreement_texts