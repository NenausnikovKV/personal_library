from legal_tech.excerts.vivo_sentence import VivoSentence


class RelevantToSentenceRules(VivoSentence):
    # предложение, виво и словрь подходящих правил с их релевантностью
    def __init__(self, vivo_sentence, *text_components):

        VivoSentence.__init__(self, vivo_sentence.sentence, vivo_sentence.vivo)

        self.component_relevance = dict()
        self.max_relevance_element_name = ""
        self.max_relevance = -1
        for text_component in text_components:
            self.add_component(text_component)


    def add_component(self, text_component):
        if not self.component_relevance.get(text_component.name):
            relevance = text_component.excerts[hash(self.sentence.text)].relevance
            self.component_relevance[text_component.name] = relevance
            if relevance > self.max_relevance:
                self.max_relevance = relevance
                self.max_relevance_element_name = text_component.name

    def define_max_relevance(self):
        for component_name in self.component_relevance:
            # self.max_relevance = 0
            if self.component_relevance[component_name] >= self.max_relevance:
                self.max_relevance = self.component_relevance[component_name]
                self.max_relevance_element_name = component_name
