from enum import Enum, auto
from dataclasses import dataclass


class TokenType(Enum):
    # Single-character tokens
    PLUS = auto()        # +
    MINUS = auto()       # -
    STAR = auto()        # *
    SLASH = auto()       # /
    LPAREN = auto()      # (
    RPAREN = auto()      # )
    LBRACE = auto()      # {
    RBRACE = auto()      # }
    SEMI = auto()        # ;
    ASSIGN = auto()      # =

    # One or two character tokens
    LT = auto()          # <
    GT = auto()          # >
    LE = auto()          # <=
    GE = auto()          # >=
    EQ = auto()          # ==
    NEQ = auto()         # !=

    # Literals
    IDENT = auto()
    NUMBER = auto()

    # Keywords
    READ = auto()
    PRINT = auto()
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    END = auto()

    EOF = auto()


KEYWORDS = {
    'read': TokenType.READ,
    'print': TokenType.PRINT,
    'if': TokenType.IF,
    'else': TokenType.ELSE,
    'while': TokenType.WHILE,
    'end': TokenType.END,
}


@dataclass(frozen=True)
class Token:
    type: TokenType
    lexeme: str
    line: int
    column: int

    def __repr__(self) -> str:
        return f"Token({self.type.name}, '{self.lexeme}', {self.line}:{self.column})"
