from legal_tech.excerts.vivo_sentence import VivoSentence


class RatedSentence(VivoSentence):
    """ Предложение, его виво-представление и их рейтинги """

    def __init__(self, sentence, rule_vivo):
        
        # получение виво в случае работы с полносвязной растопыркой
        # sentence_vivo = get_sentence_vivo(sentence, segmenter, morph_tagger, syntax_parser)
        # vivos = VivoSentence.build_sentence_vivo(sentence)

        VivoSentence.__init__(self, sentence=sentence, vivo=sentence.vivo)
        self.relevance = self.get_sentence_relevance_to_rule(rule_vivo)

    def __str__(self):
        return "{0} - {1}".format(str(self.relevance), self.sentence.text)

    def get_sentence_relevance_to_rule(self, rule_vivo):
        """
        ядро  сравнения 
        """
        # todo тут находится ядро  сравнения выбирается как именно сравниваются компоненты с предложениями
        return rule_vivo.part_of(self.vivo)