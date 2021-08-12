def get_rule_sentence_relevance(sentence_vivo, rule_vivo):
    return rule_vivo.part_of(sentence_vivo)
