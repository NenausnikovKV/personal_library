
class OrderedComponent:
    """
    Хранилище компонентов
    """
    def __init__(self, component_name, first_num):
        self.name = component_name
        self.nums = [first_num]

    def add_num(self, num):
        self.nums.append(num)
        self.nums.sort()

    def __repr__(self):
        return    "{0}, {1}".format(self.name, self.nums)




