from typing import List
from .tokens import Token, TokenType, KEYWORDS
from .errors import format_error


class LexError(Exception):
    pass


class Lexer:
    def __init__(self, source: str) -> None:
        self.source = source
        self.length = len(source)
        self.pos = 0
        self.line = 1
        self.col = 1

    def _peek(self) -> str:
        return self.source[self.pos] if self.pos < self.length else '\0'

    def _advance(self) -> str:
        ch = self._peek()
        self.pos += 1
        if ch == '\n':
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        return ch

    def _match(self, expected: str) -> bool:
        if self._peek() == expected:
            self._advance()
            return True
        return False

    def _skip_whitespace_and_comments(self) -> None:
        # Salta espacios y comentarios (// y /* */)
        while True:
            ch = self._peek()
            if ch in {' ', '\r', '\t', '\n'}:
                self._advance()
                continue
            # Line comment // ...
            if ch == '/' and self.pos + 1 < self.length and self.source[self.pos + 1] == '/':
                while self._peek() not in {'\n', '\0'}:
                    self._advance()
                continue
            # Block comment /* ... */
            if ch == '/' and self.pos + 1 < self.length and self.source[self.pos + 1] == '*':
                self._advance(); self._advance()  # come el /*
                while True:
                    if self._peek() == '\0':
                        msg = format_error(self.source, self.line, self.col)
                        raise LexError(f"Unterminated block comment\n{msg}")
                    if self._peek() == '*' and (self.pos + 1 < self.length and self.source[self.pos + 1] == '/'):
                        self._advance(); self._advance()  # come el */
                        break
                    self._advance()
                continue
            break

    def _identifier(self, start_line: int, start_col: int) -> Token:
        start = self.pos - 1
        while self._peek().isalnum() or self._peek() == '_':
            self._advance()
        text = self.source[start:self.pos]
        tok_type = KEYWORDS.get(text, TokenType.IDENT)
        return Token(tok_type, text, start_line, start_col)

    def _number(self, start_line: int, start_col: int) -> Token:
        start = self.pos - 1
        while self._peek().isdigit():
            self._advance()
        text = self.source[start:self.pos]
        return Token(TokenType.NUMBER, text, start_line, start_col)

    def tokenize(self) -> List[Token]:
        tokens: List[Token] = []
        while True:
            self._skip_whitespace_and_comments()
            ch = self._peek()
            if ch == '\0':
                tokens.append(Token(TokenType.EOF, '', self.line, self.col))
                break
            start_line, start_col = self.line, self.col
            c = self._advance()

            if c.isalpha() or c == '_':
                tokens.append(self._identifier(start_line, start_col))
                continue
            if c.isdigit():
                tokens.append(self._number(start_line, start_col))
                continue

            if c == '+':
                tokens.append(Token(TokenType.PLUS, c, start_line, start_col))
            elif c == '-':
                tokens.append(Token(TokenType.MINUS, c, start_line, start_col))
            elif c == '*':
                tokens.append(Token(TokenType.STAR, c, start_line, start_col))
            elif c == '/':
                tokens.append(Token(TokenType.SLASH, c, start_line, start_col))
            elif c == '(':
                tokens.append(Token(TokenType.LPAREN, c, start_line, start_col))
            elif c == ')':
                tokens.append(Token(TokenType.RPAREN, c, start_line, start_col))
            elif c == '{':
                tokens.append(Token(TokenType.LBRACE, c, start_line, start_col))
            elif c == '}':
                tokens.append(Token(TokenType.RBRACE, c, start_line, start_col))
            elif c == ';':
                tokens.append(Token(TokenType.SEMI, c, start_line, start_col))
            elif c == '!':
                if self._match('='):
                    tokens.append(Token(TokenType.NEQ, '!=', start_line, start_col))
                else:
                    msg = format_error(self.source, start_line, start_col)
                    raise LexError(f"Unexpected '!' (expected '!=')\n{msg}")
            elif c == '=':
                if self._match('='):
                    tokens.append(Token(TokenType.EQ, '==', start_line, start_col))
                else:
                    tokens.append(Token(TokenType.ASSIGN, '=', start_line, start_col))
            elif c == '<':
                if self._match('='):
                    tokens.append(Token(TokenType.LE, '<=', start_line, start_col))
                else:
                    tokens.append(Token(TokenType.LT, '<', start_line, start_col))
            elif c == '>':
                if self._match('='):
                    tokens.append(Token(TokenType.GE, '>=', start_line, start_col))
                else:
                    tokens.append(Token(TokenType.GT, '>', start_line, start_col))
            else:
                msg = format_error(self.source, start_line, start_col)
                raise LexError(f"Unexpected character '{c}'\n{msg}")
        return tokens
