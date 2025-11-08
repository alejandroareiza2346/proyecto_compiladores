from minilang_compiler.lexer import Lexer
from minilang_compiler.parser import Parser
from minilang_compiler.semantic import SemanticAnalyzer


def analyze(src: str):
    toks = Lexer(src).tokenize()
    prog = Parser(toks).parse()
    sema = SemanticAnalyzer()
    return sema.analyze(prog)


def test_semantic_initialization_and_warning():
    # x used before being initialized -> warning
    src = "print x; end"
    res = analyze(src)
    assert any("x" in w for w in res.warnings)


def test_semantic_initialized_is_ok():
    src = "x = 1; print x; end"
    res = analyze(src)
    assert res.warnings == []
