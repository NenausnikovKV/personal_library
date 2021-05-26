import copy

from legal_tech.excerts.vivo_sentence import VivoSentence


class RatedSentence(VivoSentence):
    """ Предложение, его виво-представление и их рейтинги """

    def __init__(self, sentence, component_vivo):
        
        # получение виво в случае работы с полносвязной растопыркой
        # sentence_vivo = get_sentence_vivo(sentence, segmenter, morph_tagger, syntax_parser)
        # vivos = VivoSentence.build_sentence_vivo(sentence)
        
        VivoSentence.__init__(self, sentence=sentence, vivo=sentence.vivo)
        self.relevance = component_vivo.part_of(self.vivo)

    def __str__(self):
        return "{0} - {1}".format(str(self.relevance), self.sentence.text)
