from __future__ import annotations
from enum import Enum, auto

class ModifierSymbol(Enum):
    Optional = '?'
    ZeroOrMore = "*"
    OneOrMore = "+"
    None_ = "" 

class TermType(Enum):
    GROUP = auto()      # ( )
    OPTION = auto()     # [ ]
    REPETITION = auto() # { }
    TERMINAL = auto()   # "string" or 'string'
    IDENTIFIER = auto() # rule_name

class AST(object):
    pass

class AlternationNode(AST):
    'alternation = ( S , concatenation , S , "|" ? ) +'
    def __init__(self, concatenations: list[ConcatenationNode]):
        self.concatenations = concatenations

    def __repr__(self):
        return f"Alt({self.concatenations})"

class TermNode(AST):
    '''
    term = "(" , S , rhs , S , ")"
         | "[" , S , rhs , S , "]"
         | "{" , S , rhs , S , "}"
         | terminal
         | identifier ;
    '''
    def __init__(self, type: TermType, value):
        self.type = type
        # value is either a string (for Terminal/Identifier) 
        # or an AlternationNode (for Group/Option/Repetition)
        self.value = value 

    def __repr__(self):
        if self.type in [TermType.TERMINAL, TermType.IDENTIFIER]:
            return f"{self.type.name}({self.value})"
        return f"{self.type.name}({self.value})"

class FactorNode(AST):
    '''
    factor = term , S , "?"
       | term , S , "*"
       | term , S , "+"
       | term , S
       ;
    '''
    def __init__(self, term: TermNode, symbol: ModifierSymbol = ModifierSymbol.None_):
        self.term = term
        self.symbol = symbol

    def __repr__(self):
        sym = self.symbol.value if self.symbol else ""
        return f"Factor({self.term}{sym})"

class ConcatenationNode(AST):
    'concatenation = ( S , factor , S , "," ? ) +'
    def __init__(self, factors: list[FactorNode]):
        self.factors = factors

    def __repr__(self):
        return f"Concat({self.factors})"

class RuleNode(AST):
    'rule = identifier , S , "=" , S , alternation , S , terminator'
    def __init__(self, ident: str, alternation: AlternationNode):
        self.identifier = ident
        self.alternation = alternation

    def __repr__(self):
        return f"\nRule({self.identifier} = {self.alternation})"

class GrammarNode(AST):
    'grammar = ( S , rule , S ) *'
    def __init__(self, rules: list[RuleNode]):
        self.rules = rules

    def __repr__(self):
        return f"Grammar({self.rules})"
    def undefined(self):
        """Returns set of undefined identifiers"""
        used_rules = set()
        def visit(node):
            if isinstance(node, AlternationNode):
                for concat in node.concatenations:
                    visit(concat)
            elif isinstance(node, ConcatenationNode):
                for factor in node.factors:
                    visit(factor)
            elif isinstance(node, FactorNode):
                visit(node.term)
            elif isinstance(node, TermNode):
                if node.type == TermType.IDENTIFIER:
                    used_rules.add(node.value)
                elif node.type in (TermType.GROUP, TermType.OPTION, TermType.REPETITION):
                    visit(node.value)
        for rule in self.rules:
            visit(rule.alternation)

        defined_rules = {rule.identifier for rule in self.rules}
        undefined = used_rules - defined_rules
        return undefined
