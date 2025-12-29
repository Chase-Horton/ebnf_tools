from .ast import (GrammarNode, RuleNode,
AlternationNode, ConcatenationNode, ModifierSymbol,
TermNode, TermType, FactorNode)
from random import choice, randint

class RandomGenerator:
    def __init__(self, grammar: GrammarNode):
        self.grammar = grammar
        self.rules = {rule.identifier: rule for rule in grammar.rules}

    def generate(self, rule_name: str, max_depth: int = 20) -> str:
        if rule_name not in self.rules:
            return f"<Undefined: {rule_name}>"
        return self._visit_rule(self.rules[rule_name], 0, max_depth)

    def _visit_rule(self, node: RuleNode, depth: int, max_depth: int) -> str:
        if depth > max_depth:
            return "" # Prevent infinite recursion
        return self._visit_alternation(node.alternation, depth + 1, max_depth)

    def _visit_alternation(self, node: AlternationNode, depth: int, max_depth: int) -> str:
        # pick one random concatenation path
        rand_choice = choice(node.concatenations)
        return self._visit_concatenation(rand_choice, depth, max_depth)

    def _visit_concatenation(self, node: ConcatenationNode, depth: int, max_depth: int) -> str:
        parts = [self._visit_factor(f, depth, max_depth) for f in node.factors]
        return "".join(parts)

    def _visit_factor(self, node: FactorNode, depth: int, max_depth: int) -> str:
        count = 1
        if node.symbol == ModifierSymbol.Optional:
            count = choice([0, 1])
        elif node.symbol == ModifierSymbol.ZeroOrMore:
            count = randint(0, 3) # Keep random repetition low for readability
        elif node.symbol == ModifierSymbol.OneOrMore:
            count = randint(1, 3)
            
        parts = []
        for _ in range(count):
            parts.append(self._visit_term(node.term, depth, max_depth))
        return "".join(parts)

    def _visit_term(self, node: TermNode, depth: int, max_depth: int) -> str:
        if node.type == TermType.TERMINAL:
            return node.value
        elif node.type == TermType.IDENTIFIER:
            if node.value in self.rules:
                 return self._visit_rule(self.rules[node.value], depth, max_depth)
            return f"<{node.value}>"
        elif node.type == TermType.GROUP:
            return self._visit_alternation(node.value, depth, max_depth)
        elif node.type == TermType.OPTION: # [ ... ]
            if choice([True, False]):
                return self._visit_alternation(node.value, depth, max_depth)
            return ""
        elif node.type == TermType.REPETITION: # { ... }
            count = randint(0, 3)
            parts = [self._visit_alternation(node.value, depth, max_depth) for _ in range(count)]
            return "".join(parts)
        return ""