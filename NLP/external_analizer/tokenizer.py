import yargy


class Yargy_tokenizer():
    """"""
    def __init__(self):
        # yargy - токенизация по правилам синтаксиса
        tokenizer = yargy.tokenizer.MorphTokenizer()