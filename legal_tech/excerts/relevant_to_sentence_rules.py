from legal_tech.components.rated_rule import RatedRule
from legal_tech.excerts.vivo_sentence import VivoSentence


class RelevantToSentenceRules(VivoSentence):
    # предложение, виво и словрь подходящих правил с их релевантностью
    def __init__(self, vivo_sentence, relevant_to_rules_sentences):

        VivoSentence.__init__(self, vivo_sentence.sentence, vivo_sentence.vivo)

        
        self.max_relevance_rule = None
        self.max_relevance = -1

        self.rated_rules = dict()
        for relevant_to_rule_sentences in relevant_to_rules_sentences:
            rule = relevant_to_rule_sentences.rule
            relevance = relevant_to_rule_sentences.relevant_sentences[ hash(self.sentence.text)].relevance
            self.add_rated_rule(rule, relevance)

    def update_max_relevance(self, rated_rule):
        self.max_relevance = rated_rule.relevance
        self.max_relevance_rule = rated_rule

    def add_rated_rule(self, rule, relevance):
        if rule.name not in self.rated_rules:
            rated_rule = RatedRule(rule, relevance)
            self.rated_rules[rule.name] = rated_rule
            if relevance > self.max_relevance:
                self.update_max_relevance(rated_rule)


    def define_max_relevance(self):
        for component_name in self.rated_rules:
            # self.max_relevance = 0
            if self.rated_rules[component_name].relevance >= self.max_relevance:
                self.max_relevance = self.rated_rules[component_name].relevance
                self.max_relevance_rule = self.rated_rules[component_name]
