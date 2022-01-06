
class OrderedCategories:
    """
    Хранилище компонентов
    """
    def __init__(self, category, first_num):
        self.name = category
        self.nums = [first_num]

    def add_num(self, num):
        self.nums.append(num)

    def __repr__(self):
        return    "{0}, {1}".format(self.name, self.nums)

    def __eq__(self, other):
        if self.name==other.name:
            return True
        return False
        



