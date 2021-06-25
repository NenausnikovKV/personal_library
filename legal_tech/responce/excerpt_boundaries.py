class ExcerptBoundaries:
    def __init__(self, start, stop):
        self.start_index = start
        self.stop_index = stop

    @classmethod
    def get_excerpt_boundaries(cls, text, excerpt):
        start_boundary = text.find(excerpt.strip())
        stop_boundary = start_boundary + len(excerpt)
        return ExcerptBoundaries(start_boundary, stop_boundary)

if __name__ == '__main__':

    indices = (ExcerptBoundaries(0, 20), ExcerptBoundaries(177, 196))
