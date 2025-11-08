from minilang_compiler.compiler import compile_pipeline


def test_pipeline_run_example_program():
    # This mirrors examples/program1.minilang
    src = (
        "read a;\n"
        "read b;\n"
        "c = a + b * 2;\n"
        "if c >= 10 {\n"
        "    print c;\n"
        "} else {\n"
        "    print 0;\n"
        "}\n"
        "i = 0;\n"
        "while i < c {\n"
        "    print i;\n"
        "    i = i + 1;\n"
        "}\n"
        "end\n"
    )
    result = compile_pipeline(source_code=src, run=True, inputs=[3, 7])
    # Expect first output is c=17, followed by 0..16
    assert hasattr(result, 'outputs')
    outs = getattr(result, 'outputs')
    assert outs[0] == 17
    assert outs[-1] == 16
    assert len(outs) == 18
