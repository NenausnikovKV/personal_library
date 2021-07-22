class ExcerptBoundaries:
    def __init__(self, start, stop):
        self.start_index = start
        self.stop_index = stop

    def __repr__(self):
        return f"({str(self.start_index)}, {str(self.stop_index)})"

    @classmethod
    def get_excerpt_boundaries(cls, text, excerpt):
        start_boundary = text.find(excerpt.strip())
        stop_boundary = start_boundary + len(excerpt)
        return ExcerptBoundaries(start_boundary, stop_boundary)

    @classmethod
    def get_from_result_components(cls, result_component):
        name = result_component.name
        all_boundaries = []
        for rel_sentence in result_component.relevant_sentences.values():
            sent_boundaries = ExcerptBoundaries(rel_sentence.sentence.start, rel_sentence.sentence.stop)
            all_boundaries.append(sent_boundaries)
        return all_boundaries

    @classmethod
    def get_from_sentence(cls, sentence):
        all_boundaries = []
        sent_boundaries = ExcerptBoundaries(sentence.start, sentence.stop)
        all_boundaries.append(sent_boundaries)
        return all_boundaries


if __name__ == '__main__':

    indices = (ExcerptBoundaries(0, 20), ExcerptBoundaries(177, 196))
