def get_sentence_relevance_to_rule(sentence_vivo, rule_vivo):
    return rule_vivo.part_of(sentence_vivo)
