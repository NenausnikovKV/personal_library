import copy
from collections import namedtuple
from operator import attrgetter

from NLP.token_stage.word import SentenceWord
from legal_tech.components.result_component import ResultComponent
from NLP.sentence_stage.sentence import Sentence
from graph_representation.vivo.vivo import Vivo
from legal_tech.excerts.relevant_excert import RelevantExcert
from legal_tech.excerts.vivo_sentence import VivoSentence


class Suspect:
    """
    подозреваемый
    """
    def __init__(self, component, feature, rating):
        self.component = component
        self.feature = feature
        self.rating = rating


Couple = namedtuple("Couple", ["first", "second"])
ComponentAndSentence = namedtuple("ComponentAndSentence", ["component", "relevant_sentence"])


# выделение списков слов со смещением
def devide_into_two_parts(word_list, displacement):
    word_list_middle = int(word_list.__len__() / 2)
    word_list_middle += displacement
    first = word_list[:word_list_middle]
    second = word_list[word_list_middle:]
    word_list_couple = Couple(first, second)
    return word_list_couple

# Выделение - выделение предложений с максимальным рейтингом
def get_max_rating_word_list(components, sentence_part_word_lists):
    ratings = {}
    max_rating = -1
    part_num = 0
    max_component_name = ""
    for component_name in components:
        for i in range(sentence_part_word_lists.__len__()):
            sentence_part_words = dict([hash(word.text), word] for word in sentence_part_word_lists[i])
            text_words = tuple([word.text for word in sentence_part_words.values()])
            sentence_vivo = Vivo(text_words)
            sentence_vivo.normal_relations()
            sample_vivo = components[component_name].vivo
            # определение рейтинга
            ratings[component_name + "-" + str(i)] = sentence_vivo.sum_compare(sample_vivo)
            if ratings[component_name + "-" + str(i)] > max_rating:
                max_rating = ratings[component_name + "-" + str(i)]
                max_component_name = component_name
                part_num = i
    if max_rating <=0:
        a=0

    component_word_list_and_rating = Suspect(component=components[max_component_name],
                                             feature=sentence_part_word_lists[part_num],
                                             rating=max_rating)
    return component_word_list_and_rating

# определение оптимальной середины предложения
def define_sentence_parts(origin_sentence, suspect_couple):
    """
    делим предложение на 2 части
    в случае если предложение не делится возвращает None
    """

    # смещение от середины предложения
    displacement = 0
    # направление смещения по предложению
    # положительный вправо, отрицательный влево
    direct = 1
    # подсчет количества повторов по смещению
    displacement_places = {}

    previous_word_list_suspects = []
    while True:

        # получаем части со смещением
        word_list_couple = devide_into_two_parts(origin_sentence.word_list, displacement)
        # определяем рейтинг компонентов для частей и записываем в порядкае убывания
        component_dict = dict([suspect.component.name, suspect.component] for suspect in suspect_couple)
        word_list_suspect_couple = []
        while True:
            word_list_suspect = get_max_rating_word_list(component_dict, word_list_couple)
            word_list_suspect_couple.append(word_list_suspect)
            component_dict.pop(word_list_suspect.component.name)
            if component_dict.__len__() == 0:
                break
        # Если если они претендуют на одну и ту же часть, то возвращеаем None
        first_word_num = origin_sentence.word_list[0].num
        last_word_num = origin_sentence.word_list[-1].num
        try:
            if (word_list_suspect_couple[0].feature[0].num == first_word_num and
                word_list_suspect_couple[1].feature[0].num == first_word_num) or \
                (word_list_suspect_couple[0].feature[-1].num == last_word_num and
                word_list_suspect_couple[1].feature[-1].num == last_word_num):
                # Если пара не удалась, то выбираем кого-то одного
                new_suspect_couple = get_best_suspect(suspect_couple)
                return new_suspect_couple
        except:
            a =899

        # сравниваем с предидущим проходом и определяем дальнейшее направление
        # Если это не первый проход определяется разница
        if previous_word_list_suspects.__len__() > 0:
            old_general_rating = 0
            new_general_rating = 0
            num = 0
            while num < word_list_suspect_couple.__len__():
                old_general_rating += previous_word_list_suspects[num].rating / \
                                      previous_word_list_suspects.__len__()
                new_general_rating += word_list_suspect_couple[num].rating / word_list_suspect_couple.__len__()
                num += 1
            if new_general_rating < old_general_rating:
                direct *= -1

        # сохраняем текущее состояние для дальнейшего сравнения
        previous_word_list_suspects.clear()
        for word_list_suspect in word_list_suspect_couple:
            previous_word_list_suspects.append(word_list_suspect)

        # отмечаем количество нахождений - ищем экстремум
        if not displacement_places.get(displacement):
            displacement_places[displacement] = 1
        else:
            displacement_places[displacement] += 1

        # выходим если нашли оптимум, точка в которую попадаем третий раз
        if displacement_places[displacement] > 2:
            break
        # смещаемся на единцу 
        displacement += direct

    # Исключаем увеличение рейтинга за счет исключения одной из частей предложения
    for word_list_suspect in word_list_suspect_couple:
        if word_list_suspect.rating == 0:
            # Если пара не удалась, то выбираем кого-то одного
            new_suspect_couple = get_best_suspect(suspect_couple)
            return new_suspect_couple


    # располагаем по порядку
    first_num = origin_sentence.word_list[0].num
    last_word_num = origin_sentence.word_list[-1].num
    if word_list_suspect_couple[1].feature[0].num == first_num:
        word_list_suspect_couple[0], word_list_suspect_couple[1] = word_list_suspect_couple[1], \
                                                                   word_list_suspect_couple[0]
    # оборачиваю в tuplenamed, оставляю возможную проюлему недо или переполнения в этой функции
    word_list_suspect_couple = Couple(first=word_list_suspect_couple[0], second=word_list_suspect_couple[1])
    return word_list_suspect_couple

# Для двух списков слов выделяются и оформляются предложения
def get_sentences_from_word_list(origin_sentence, word_list_suspect_couple):
    # определяем кто первы кто второй

    # 2 списка слов
    first_word_list = word_list_suspect_couple[0].feature
    second_word_list = word_list_suspect_couple[1].feature

    if first_word_list.__len__() > 0:
        border_word = first_word_list[-1]
    else:
        border_word = second_word_list[0]


    # cлово на границе и его количество
    border_word_num = first_word_list.count(border_word)

    # определяем местоположение нормализованного токена
    normal_tokens = origin_sentence.normal_tokens
    count = normal_tokens.count(border_word)

    index_border_normal_tokens = -1
    for token_index in range(normal_tokens.__len__()):
        border_normal_token = normal_tokens[token_index]
        if border_normal_token.start == border_word.token.start:
            index_border_normal_tokens = token_index
            break
    if index_border_normal_tokens == -1:
        raise Exception()

    first_normal_tokens = normal_tokens[:index_border_normal_tokens + 1]
    second_normal_tokens = origin_sentence.normal_tokens[index_border_normal_tokens + 1:]
    text_border = first_normal_tokens[first_normal_tokens.__len__() - 1].stop
    first_text = origin_sentence.text[:text_border]
    second_text = origin_sentence.text[text_border:]

    # Определяем токены предложений
    first_token_list = []
    second_token_list = []
    for element in first_normal_tokens:
        if element.type != "word":
            first_token_list.append(element)
    for element in second_normal_tokens:
        if element.type != "word":
            second_token_list.append(element)

    first_words = SentenceWord.get_word_dict_from_word_list(first_word_list)
    second_words = SentenceWord.get_word_dict_from_word_list(second_word_list)

    # разделение виво
    first_relations = []
    second_relations = []

    for relation_name in origin_sentence.vivo.relations.keys():
        relation = origin_sentence.vivo.relations[relation_name]
        text1 = relation.text1
        text2 = relation.text2
        if first_words.get(hash(text1)) and first_words.get(hash(text2)):
            first_relations.append(copy.deepcopy(relation))
        if second_words.get(hash(text1)) and second_words.get(hash(text2)):
            second_relations.append(copy.deepcopy(relation))
    first_vivo = Vivo(relations=first_relations)
    second_vivo = Vivo(relations=second_relations)

    # наконец собираем предложения
    first_sentence = Sentence(sen_text=first_text, tokens=first_token_list, normal_tokens=first_normal_tokens,
                              word_list=first_word_list, sen_words=second_words, syn_vivo=first_vivo)
    second_sentence = Sentence(sen_text=second_text, tokens=second_token_list, normal_tokens=second_normal_tokens,
                               word_list=second_word_list, sen_words=first_words, syn_vivo=second_vivo)

    sentence_couple = Couple(first=first_sentence, second=second_sentence)

    # получаем виво для каждого предложения
    component_and_sentence_couple = []
    ComponentAndSentence = namedtuple("ComponentAndSentence", "component relevant_sentence")
    for i in range(sentence_couple.__len__()):
        sentence = sentence_couple[i]
        vivo_sentence = VivoSentence.init(sentence)
        relevant_sentence = RelevantExcert(vivo_sentence, word_list_suspect_couple[i].component.vivo, word_list_suspect_couple[i].rating)
        component_and_sentence = ComponentAndSentence(component=word_list_suspect_couple[i].component,
                                                 relevant_sentence=relevant_sentence)
        component_and_sentence_couple.append(component_and_sentence)

    component_and_sentence_couple = Couple(first=component_and_sentence_couple[0], second=component_and_sentence_couple[1])
    return component_and_sentence_couple

# создание пар подозреваемых для попарной проверки
def create_suspect_cupples(suspects):
    # раскидываем по парам, где каждый подозреваемый ставится в пару с другим
    suspect_couples = []
    for i in range(suspects.__len__()):
        first_suspect = suspects[i]
        for j in range(i + 1, suspects.__len__()):
            second_suspect = suspects[j]
            suspect_couple = Couple(first_suspect, second_suspect)
            suspect_couples.append(suspect_couple)
    return suspect_couples

# создание подозреваемых
def create_suspects(sentence_component_relevance, result_components):
    """
    Оформляем каждый из из предполагаемых компонентов в подозреваемых
    """
    # текст предложения
    origin_sentence_text = sentence_component_relevance.sentence.text
    # словарь относящихся к предложению компонентов и их релевантоность
    component_relevances = sentence_component_relevance.component_relevance

    suspects = []  # component, sentence и ratings - основной класс с которым буду работать
    for component_name in component_relevances:
        component = result_components.get(component_name)
        for excerpt in component.excerts.values():
            if excerpt.sentence.text == origin_sentence_text:
                suspect = Suspect(component=component, feature=excerpt.sentence.word_list, rating=excerpt.relevance)
                suspects.append(suspect)

    # сортируем подозреваемых по релевантности
    suspects = sorted(suspects, key=attrgetter("rating"), reverse=True)
    return suspects

def get_best_suspect(suspect_couple):
        # Если пара не удалась, то выбираем одно предложение
        # Пара не удается если оба претендуют на одну сторону предложения
        # Или одно предложение полностью подавляет другое
        if suspect_couple.first.rating > suspect_couple.second.rating:
            second = Suspect(component=suspect_couple.first.component, feature=[], rating=0)
            new_suspect_couple = Couple(suspect_couple.first, second)
        else:
            first = Suspect(component=suspect_couple.second.component, feature=[], rating=0)
            new_suspect_couple = Couple(first, suspect_couple.second)
        return new_suspect_couple

# разделение предложения
def divide_sentence(sentence_component_relevance, result_components):

    """
    Рзделение предложений на участки самые близкие к шаблону
    """


    origin_sentence = sentence_component_relevance.sentence
    # получаем подозреваемых
    suspects = create_suspects(sentence_component_relevance, result_components)
    # получаем пары подозреваемых
    suspect_couples = create_suspect_cupples(suspects)

   # для каждой пары определяется доля каждого в предложении
    new_suspect_couples = []
    for suspect_couple in suspect_couples:
        # определяем оптимальное положения центра предложения
        new_suspect_couple = define_sentence_parts(origin_sentence, suspect_couple)
        new_suspect_couples.append(new_suspect_couple)

    win_couple = None
    max_rating = -1
    for couple in new_suspect_couples:
        general_rating = (couple.first.rating + couple.second.rating)/2
        if general_rating>max_rating:
            max_rating = general_rating
            win_couple = couple



    # на основании разбора победителя строятся предложения
    component_and_sentence_couple = get_sentences_from_word_list(origin_sentence, win_couple)


    #  отбрасывыаем пустые предложения
    #  появляется, когда предложение одно
    component_and_sentence_list = []
    sentences = []
    for element in component_and_sentence_couple:
        if element.relevant_sentence.relevance != 0:
            component_and_sentence_list.append(element)


    # формируем компонент с предложением
    result_component_and_origin_sentence = []
    for element in component_and_sentence_list:
        name = element.component.name
        vivo = element.component.vivo
        necessity = element.component.necessity
        relevant_sentence = [element.relevant_sentence]
        result_component = ResultComponent(name, vivo, necessity, relevant_sentence)
        component_and_sentence = ComponentAndSentence(component=result_component, relevant_sentence=origin_sentence)
        result_component_and_origin_sentence.append(component_and_sentence)

    return result_component_and_origin_sentence



    # result_component_sentences.append(
    #     ComponentAndSentence(sentence=origin_sentence, components_of_texts=result_component_list))
    #     result_component = ResultComponent(win_suspect.component.name, win_suspect.component.vivos,
    #                                        win_suspect.component.necessity, [win_suspect.feature])
    #     result_component_sentences.append(ComponentAndSentence(sentence=origin_sentence, components_of_texts=[result_component]))
    #
    # return result_component_sentences
    #
    #














# sentennce_len1 = relevant_sentences[0].sentence.word_list.__len__()
# sentennce_len2 = relevant_sentences[1].sentence.word_list.__len__()
# len = max(sentennce_len1, sentennce_len2)
#
# # сравнение по смещению
# d1s = relevant_sentences[0].sentence.word_list[0].num
# d1e = relevant_sentences[0].sentence.word_list[-1].num
#
# d2s = relevant_sentences[1].sentence.word_list[0].num
# d2e = relevant_sentences[1].sentence.word_list[-1].num
# difference = (abs(d1s - d2s) + abs(d1e - d2e)) / len
# proximity = relevant_sentences[0].graph_representation.compare(relevant_sentences[1].graph_representation)
