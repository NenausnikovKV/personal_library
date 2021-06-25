class FinalComponent():

    def __init__(self, name, text_excerts):
        self.name = name
        self.excerts = text_excerts

    def __repr__(self):
        return f"{self.name} - {self.excerts}"

    @classmethod
    def get_from_result_component(cls, result_component):
        name = result_component.name
        excerts = [rel_sentence.sentence.text for rel_sentence in result_component.relevant_senteces.values()]
        return FinalComponent(name, excerts)
