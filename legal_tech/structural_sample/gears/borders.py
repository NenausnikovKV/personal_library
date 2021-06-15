class Borders():
    """
    Границы слева и справа от заданнной категоррии
    """
    def __init__(self, left_categories, right_categories):
        self.left = set(left_categories)
        self.right = set(right_categories)

