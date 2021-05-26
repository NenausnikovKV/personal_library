from abc import abstractmethod

@abstractmethod
class MorphDictionary:
    def __init__(self):
        """
            загрузка внешнего морфологического словаря
        """
        pass
    def parse(self, word_list):
        pass

