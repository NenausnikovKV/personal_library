from file_processing import file_processing


def get_punctuation_list():
    address = file_processing.get_library_address("punctuation_mark")
    # path = os.getcwd()[:os.getcwd().find("source")]  + "source\\NLP\\token_stage\\punctuation_mark"
    f = open(address, "r", encoding="utf-8")
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


    @staticmethod
    def define_type(word_text):
        if word_text in list(Token.punctuation_list):
            token_type = "punctuation"
        elif word_text.isdigit():
            token_type = "digit"
        else:
            token_type = "word"
        return token_type

class SentenceToken(Token):

    def __init__(self, text, type, num =-1, start=-1, stop=-1):
        super().__init__(text, type)
        self.start = start
        self.stop = stop
        self.num = num

    @staticmethod
    def find_normal_token_text(token, normal_tokens):
        start = token.start
        for norm_token in normal_tokens:
            if norm_token.start == start:
                return norm_token.text
        return None

