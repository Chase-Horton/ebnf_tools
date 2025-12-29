from .lexer import Lexer, TokenType
from .ast import (
    AlternationNode, ConcatenationNode,
    GrammarNode, RuleNode, TermNode,
    TermType, FactorNode, ModifierSymbol)

class Parser:
    def __init__(self, filename:str):
        try:
            with open(filename) as f:
                ebnf_code = f.read().strip()
        except:
            raise Exception(f"Error opening the file: {filename}")
        lexer = Lexer(ebnf_code)
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()
    
    def consume(self, token_type:TokenType):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            raise Exception(f"Parsing error. Expected: {token_type.name}, got: {self.current_token.type.name}")
    
    def parse(self):
        """grammar = rule*"""
        rules = []
        while self.current_token.type != TokenType.EOF:
            rules.append(self.parse_rule())
        return GrammarNode(rules)

    def parse_rule(self):
        """rule = identifier = alternation"""
        indentifier = self.current_token.value
        self.consume(TokenType.IDENTIFIER)
        self.consume(TokenType.EQUALS)
        rhs = self.parse_alternation()
        self.consume(TokenType.SEMICOLON)
        return RuleNode(indentifier, rhs)
    
    def parse_alternation(self):
        """alternation = concatenation (| concatenation)*"""
        concats = []
        concats.append(self.parse_concatentation())
        while self.current_token.type == TokenType.PIPE:
            self.consume(TokenType.PIPE)
            concats.append(self.parse_concatentation())
        return AlternationNode(concats)
    
    def parse_concatentation(self):
        factors = []
        while self.current_token.type in [
            TokenType.IDENTIFIER, TokenType.STRING,
            TokenType.LPAREN, TokenType.LBRACE, TokenType.LBRACKET,
            TokenType.COMMA]:
            if self.current_token.type == TokenType.COMMA:
                self.consume(TokenType.COMMA)
            #check if was trailing comma
            if self.current_token.type in [TokenType.PIPE, TokenType.SEMICOLON, TokenType.RPAREN, TokenType.RBRACKET, TokenType.RBRACE]:
                break

            factors.append(self.parse_factor())
        return ConcatenationNode(factors)
    
    def parse_factor(self):
        """factor = term modifier?"""
        term = self.parse_term()
        symbol = ModifierSymbol.None_
        if self.current_token.type == TokenType.QUESTION:
            symbol = ModifierSymbol.Optional
            self.consume(TokenType.QUESTION)
        elif self.current_token.type == TokenType.ASTERISK:
            symbol = ModifierSymbol.ZeroOrMore
            self.consume(TokenType.ASTERISK)
        elif self.current_token.type == TokenType.PLUS:
            symbol = ModifierSymbol.OneOrMore
            self.consume(TokenType.PLUS)
            
        return FactorNode(term, symbol)
    
    def parse_term(self):
        """term = group | option | repetition | terminal | identifier"""
        token = self.current_token
        
        if token.type == TokenType.LPAREN:
            self.consume(TokenType.LPAREN)
            expr = self.parse_alternation()
            self.consume(TokenType.RPAREN)
            return TermNode(TermType.GROUP, expr)
            
        elif token.type == TokenType.LBRACKET:
            self.consume(TokenType.LBRACKET)
            expr = self.parse_alternation()
            self.consume(TokenType.RBRACKET)
            return TermNode(TermType.OPTION, expr)
            
        elif token.type == TokenType.LBRACE:
            self.consume(TokenType.LBRACE)
            expr = self.parse_alternation()
            self.consume(TokenType.RBRACE)
            return TermNode(TermType.REPETITION, expr)
            
        elif token.type == TokenType.STRING:
            val = token.value
            self.consume(TokenType.STRING)
            return TermNode(TermType.TERMINAL, val)
            
        elif token.type == TokenType.IDENTIFIER:
            val = token.value
            self.consume(TokenType.IDENTIFIER)
            return TermNode(TermType.IDENTIFIER, val)
            
        else:
            raise Exception(f"Unexpected token in term: {token}")

def ValidateGrammar(grammar: GrammarNode) -> bool:
    """Accepts a grammar node and returns true if all used identifiers are properly declared, else returns false"""
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
    for rule in grammar.rules:
        visit(rule.alternation)

    defined_rules = {rule.identifier for rule in grammar.rules}
    undefined = used_rules - defined_rules
    if undefined:
        return False
    return True