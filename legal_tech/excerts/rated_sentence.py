from collections import defaultdict

from legal_tech.excerts.vivo_sentence import VivoSentence


class RatedSentence(VivoSentence):
    """ Предложение, его виво-представление и их рейтинги """

    def __init__(self, sentence, rule_vivo, relevance=None):
        
        # получение виво в случае работы с полносвязной растопыркой
        # sentence_vivo = get_sentence_vivo(sentence, segmenter, morph_tagger, syntax_parser)
        VivoSentence.__init__(self, sentence=sentence, vivo=sentence.vivo)

        if relevance != None:
            self.relevance = relevance
        else:
            self.relevance = self.get_sentence_relevance_to_rule(rule_vivo)
        # каждое предложение релевантно определенному виво
        # (одна из моделей предполагает динамическое изменение этого виво),
        self.rule_vivo = rule_vivo

    def __str__(self):
        return "{0} - {1}".format(str(self.relevance), self.sentence.text)

    def get_sentence_relevance_to_rule(self, rule_vivo):
        """
        ядро  сравнения 
        """
        # todo тут находится ядро  сравнения выбирается как именно сравниваются компоненты с предложениями
        return rule_vivo.part_of(self.vivo)
    
    # @staticmethod
    # def collect_all_rated_sentences(components):
    #     component_sorted_sentences = defaultdict(list) 
    #     for component_name, component in components.items():
    #         for sen_hash, rel_sentence in component.relevant_sentences.items():
    #             component_sorted_sentences[sen_hash].append(rel_sentence)
    #             
            
        