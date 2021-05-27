from collections import defaultdict


class SyntaxTree():

    def __init__(self, sent, vertices, token_dict):
        self.sent = sent
        self.vertices = vertices
        self.token_dict = token_dict


    @classmethod
    def create_tree_from_sents(cls, sent):
        token_dict = defaultdict(list)
        vertices = []
        for token in sent.tokens:
            token_dict[token.head_id].append(token)
            if token.head_id == 0:
                vertices.append(token.id)
        return cls(sent, vertices, token_dict)


    # def _sentence_tree(self):
    #     for vertex in self.vertices:
    #         self.extract_tree_branch(self.token_dict[vertex])
    #
    #     token_dict = {token.id: token for token in sent.tokens}
    #     head_id_dict = {token.head_id: token for token in sent.tokens}
    #     for token in sent.tokens:
    #         token1 = token
    #         token2 = token_dict[token.head_id]
    #
    # def extract_tree_branch(self, start):
    #     pass