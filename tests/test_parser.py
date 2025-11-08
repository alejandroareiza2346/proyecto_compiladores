import pytest
from minilang_compiler.lexer import Lexer
from minilang_compiler.parser import Parser, ParseError
from minilang_compiler.ast_nodes import Program, Assign, While, Print, Read


def parse(src: str):
    toks = Lexer(src).tokenize()
    return Parser(toks).parse()


def test_parser_min_program():
    prog = parse("end")
    assert isinstance(prog, Program)
    assert prog.body == []


def test_parser_statements_and_blocks():
    src = """
    read a;
    a = 1 + 2 * 3;
    while a > 0 { print a; a = a - 1; }
    end
    """
    prog = parse(src)
    assert len(prog.body) == 3
    assert isinstance(prog.body[0], Read)
    assert isinstance(prog.body[1], Assign)
    assert isinstance(prog.body[2], While)


def test_parser_error_missing_semicolon():
    src = "print 1 end"
    with pytest.raises(ParseError):
        parse(src)
