import pytest
from minilang_compiler.lexer import Lexer, LexError
from minilang_compiler.tokens import TokenType


def test_lexer_basic_tokens():
    src = "read a; print 1+2; end"
    toks = Lexer(src).tokenize()
    types = [t.type for t in toks]
    assert TokenType.READ in types
    assert TokenType.IDENT in types
    assert TokenType.PRINT in types
    assert TokenType.NUMBER in types
    assert types[-1] == TokenType.EOF


def test_lexer_comments_and_positions():
    src = "// comment\nread a; /* block */ print a; end"
    toks = Lexer(src).tokenize()
    # Ensure comments skipped and tokens present
    kinds = [t.type for t in toks]
    assert kinds.count(TokenType.READ) == 1
    assert kinds.count(TokenType.PRINT) == 1


def test_lexer_error_bang_without_equal():
    src = "! end"
    with pytest.raises(LexError):
        Lexer(src).tokenize()
