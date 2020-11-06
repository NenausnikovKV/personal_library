import os


def get_punctuation_list():
    path = os.getcwd()[:os.getcwd().find("source")]  + "source\\NLP\\token_stage\\punctuation_mark"
    f = open(path, "r", encoding="utf-8")
    punctuation_text = ""
    for line in f:
        punctuation_text = punctuation_text + line
    punctuation_list = punctuation_text.split()
    return punctuation_list

class Token():

    punctuation_list = get_punctuation_list()

    def __init__(self, text, type):
        self.text = text.upper()
        self.type = type

    def __lt__(self, other):
        return self.text < other.text

    def __str__(self):
        return self.text + " (" + self.type + ")" + " - "

    def define_token_type(self):
        if self.text in list(Token.punctuation_list):
            type = "punctuation"
        elif self.text.isdigit():
            type = "digit"
        else:
            type = "word"
        return type

class SentenceToken(Token):

    def __init__(self, text, type, start=0, stop=0):
        super().__init__(text, type)
        self.start = start
        self.stop = stop
