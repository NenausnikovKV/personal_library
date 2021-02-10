import copy
from operator import attrgetter
from natasha import Segmenter, NewsEmbedding, NewsMorphTagger, NewsSyntaxParser, Doc
from yargy.tokenizer import MorphTokenizer

from NLP.dictionary_library.morphDictionary import MorphDictionary
from NLP.document_stage.text import Text
from NLP.sentence_stage.sentence import Sentence
from NLP.token_stage.personal_token import Token
from graph_representation.relation import Relation
from graph_representation.vivo import Vivo


def clear_puctuations(sentence):
    punctuation_list = Token.punctuation_list
    normal_token_dict = dict([hash(token.text), token] for token in sentence.normal_tokens)
    for mark in punctuation_list:
        if normal_token_dict.get(hash(mark)):
            sentence.remove_word(mark)

def get_text_relations(text, segmenter = Segmenter(),morph_tagger = NewsMorphTagger(NewsEmbedding()),
                       syntax_parser = NewsSyntaxParser(NewsEmbedding()), morph = MorphDictionary()):
    syn_analizer = "Возьми из основы"
    sentence_vivos = []
    text_object = Text.get_text_object_from_text(text, number=0, corpus_source=None, syn_analizer="Задолбался", morph=morph)
    for sentence in text_object.sentences.values():

        sentence_vivo = get_sentence_vivo(sentence, segmenter, morph_tagger, syntax_parser)
        sentence_vivos[hash(sentence.text)] = sentence_vivo
    return sentence_vivos

def get_sentence_vivo(sentence, segmenter = Segmenter(), morph_tagger = NewsMorphTagger(NewsEmbedding()),
                      syntax_parser = NewsSyntaxParser(NewsEmbedding())):


    copy_sentence = copy.deepcopy(sentence)
    clear_puctuations(copy_sentence)

    # обработка поступившего текста
    doc = Doc(copy_sentence.text)
    doc.segment(segmenter)
    doc.tag_morph(morph_tagger)
    doc.parse_syntax(syntax_parser)

    sent = doc.sents[0]
    # sent.syntax.print()

    tokens = list(sent.syntax.tokens)
    for token in tokens:
        token.head_id = int(str(token.head_id).split("_")[1])
        token.id = int(str(token.id).split("_")[1])
    head_id_tokens = sorted(tokens, key=attrgetter("head_id"))
    token_dict = dict([token.id, token] for token in tokens)

    relations = []
    for token in head_id_tokens:
        # смещение на 1 так как 0 - это корень
        token1 = token
        text1 = Sentence.get_normal_form_token(sentence, token1.id - 1)
        # 0 связан с корем древа
        if token.head_id == 0:
            continue
        token2 = token_dict[token.head_id]
        text2 = Sentence.get_normal_form_token(sentence, token2.id - 1)

        relation = Relation(text1, text2, rating=1)
        relations.append(relation)
    sentence_vivo = Vivo(relations=relations)
    return sentence_vivo

if __name__=="__main__":
    segmenter = Segmenter()
    text = "привет люди"
    doc = Doc(text)
    doc.segment(segmenter)
    sent = doc.sents[0]
    print(1)
