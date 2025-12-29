from enum import Enum, auto
class TokenType(Enum):
    IDENTIFIER = auto()
    STRING = auto()
    EQUALS = auto()
    PIPE = auto()
    COMMA = auto()
    SEMICOLON = auto()
    LPAREN = auto()
    RPAREN = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    LBRACE = auto()
    RBRACE = auto()
    QUESTION = auto()
    ASTERISK = auto()
    PLUS = auto()
    EOF = auto()

class Token:
    def __init__(self, type:TokenType, value:str):
        self.type = type
        self.value = value
    def __repr__(self):
        return f"Token({self.type.name}, {self.value})"

class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[0] if self.text else None
    
    def advance(self):
        """Increment Pointer and set current_char to next"""
        self.pos += 1
        if self.pos < len(self.text):
            self.current_char = self.text[self.pos]
        else:
            self.current_char = None

    def peek(self):
        """Look at the next character without consuming it."""
        peek_pos = self.pos + 1
        if peek_pos < len(self.text):
            return self.text[peek_pos]
        return None
    
    def skip_comment(self):
        self.advance() # consume '('
        self.advance() # consume '*'
        
        while self.current_char is not None:
            if self.current_char == '*' and self.peek() == ')':
                self.advance() # consume '*'
                self.advance() # consume ')'
                return
            self.advance()
    
    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def _id(self):
        result = ''
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()
        return Token(TokenType.IDENTIFIER, result)

    def _string(self, quote_type):
        self.advance() # skip opening quote
        result = ''
        while self.current_char is not None and self.current_char != quote_type:
            result += self.current_char
            self.advance()
        self.advance() # skip closing quote
        return Token(TokenType.STRING, result)
    def get_next_token(self):
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            
            if self.current_char == '(' and self.peek() == '*':
                self.skip_comment()
                continue
            
            if self.current_char.isalpha() or self.current_char == '_':
                return self._id()
            
            if self.current_char == '"' or self.current_char == "'":
                return self._string(self.current_char)

            char_map = {
                '=': TokenType.EQUALS,
                '|': TokenType.PIPE,
                ',': TokenType.COMMA,
                ';': TokenType.SEMICOLON,
                '(': TokenType.LPAREN,
                ')': TokenType.RPAREN,
                '[': TokenType.LBRACKET,
                ']': TokenType.RBRACKET,
                '{': TokenType.LBRACE,
                '}': TokenType.RBRACE,
                '?': TokenType.QUESTION,
                '*': TokenType.ASTERISK,
                '+': TokenType.PLUS
            }

            if self.current_char in char_map:
                token = Token(char_map[self.current_char], self.current_char)
                self.advance()
                return token

            raise Exception(f"Invalid character: {self.current_char}")

        return Token(TokenType.EOF, "")
