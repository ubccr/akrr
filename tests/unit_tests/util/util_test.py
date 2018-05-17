

def test_clear_from_build_in_var():
    from akrr.util import clear_from_build_in_var

    tmp = {}
    exec(
        "import sys\n"
        "my_var1=sys.path\n"
        "my_var2=2\n",
        tmp)
    tmp = clear_from_build_in_var(tmp)

    assert "__builtins__" not in tmp
    assert "sys" not in tmp
    assert "my_var1" in tmp
    assert "my_var2" in tmp
    assert tmp["my_var2"] == 2
