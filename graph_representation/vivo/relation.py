class Relation:

    def __init__(self, *text, rating=0):
        if len(text)==1 and isinstance(text[0], str):
            self.text = text[0]
            self.text1 = self.text[:self.text.find("-")]
            self.text2 = self.text[self.text.find("-") + 1:]
        if len(text) == 2:
            self.text1 = text[0]
            self.text2 = text[1]
            self.text = Relation.get_relation_text(self.text1, self.text2)
        self.rating = rating

    def __str__(self):
        return self.text + " - " + str(self.rating)

    def __eq__(self, other):
        if isinstance(other, Relation):
            return self.text1 == other.text1 and self.text2 == other.text2
        elif isinstance(other, str):
            return self.text1 + "-" + self.text2 == other
        else:
            return None

    def __hash__(self):
        return hash(self.text)

    def __lt__(self, other):
        if self.rating<other.rating:
            return True
        else:
            return False



    def have_node(self, text):
        if any( [self.text1 == text, self.text2 == text] ):
            return True
        else:
            return False




    @staticmethod
    def get_relation_text(text1, text2):
        if text1 < text2:
            return text1 + "-" + text2
        else:
            return text2 + "-" + text1





