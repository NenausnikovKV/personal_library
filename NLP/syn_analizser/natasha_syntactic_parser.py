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
                       syntax_parser = NewsSyntaxParser(NewsEmbedding()), tokenizer = MorphTokenizer(),
                       morph = MorphDictionary()):
    sentence_vivos = []
    text_object = Text.get_text_object(text, tokenizer = tokenizer, morph = morph)
    for sentence in text_object.sentences.values():
        clear_puctuations(sentence)
        relations = get_sentence_relations(sentence, segmenter, morph_tagger, syntax_parser)
        sentence_vivo = Vivo(relations=relations)
        sentence_vivos[hash(sentence.text)] = sentence_vivo
    return sentence_vivos

def get_sentence_relations(sentence, segmenter = Segmenter(), morph_tagger = NewsMorphTagger(NewsEmbedding()),
                       syntax_parser = NewsSyntaxParser(NewsEmbedding()) ):

    # обработка поступившего текста
    doc = Doc(sentence.text)
    doc.segment(segmenter)
    doc.tag_morph(morph_tagger)
    doc.parse_syntax(syntax_parser)

    sent = doc.sents[0]
    sent.syntax.print()

    tokens = list(sent.syntax.tokens)
    for token in tokens:
        head_id = token.head_id
        head_id = head_id.split("_")[1]
        token.head_id = int(head_id)

        id = token.id
        id = id.split("_")[1]
        token.id = int(id)


    head_id_tokens = sorted(tokens, key=attrgetter("head_id"))
    token_dict = dict([token.id, token] for token in tokens)

    relations = []
    for token in head_id_tokens:
        # смещение на 1 так как 0 - это корень
        token1 = token
        text1 = Sentence.get_token_normal_form(sentence, token1.id - 1)
        # 0 связан с корем древа
        if token.head_id == 0:
            continue
        token2 = token_dict[token.head_id]
        text2 = Sentence.get_token_normal_form(sentence, token2.id - 1)

        relation = Relation(text1, text2, rating=1)
        relations.append(relation)
    return relations