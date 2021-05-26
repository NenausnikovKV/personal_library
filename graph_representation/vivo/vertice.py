from operator import attrgetter


class Vertice:

    def __init__(self, node, relation_list):
        self.node = node
        self.relations = relation_list
        if len(self.relations) == 0:
            self.max_rating = 0
        else:
            max_rating_relation = max(self.relations, key=attrgetter("rating"))
            self.max_rating = max_rating_relation.rating
