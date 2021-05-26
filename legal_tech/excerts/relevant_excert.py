from legal_tech.excerts.vivo_sentence import VivoSentence


class RelevantExcert(VivoSentence):

    def __init__(self, vivo_sentence, component_vivo, relevance):
        super().__init__(vivo_sentence.sentence, vivo_sentence.vivo)
        self.component_vivo = component_vivo  # каждое предложение релевантно определенному виво, для этого и хранится
        self.relevance = relevance

    def __repr__(self):
        sentence_start_length = 0
        i = 0
        for token in self.sentence.tokens:
            sentence_start_length += (token.text.__len__())
            if self.sentence.text.__len__() - sentence_start_length > 1:
                sentence_start_length += 1
            if i == 3: break
            i = i+1
        return self.sentence.text[0:sentence_start_length] + " - " + str(self.relevance)
