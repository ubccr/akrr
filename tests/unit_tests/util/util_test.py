import pytest
import os


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


def test_exec_files_to_dict(datadir):
    from akrr.util import exec_files_to_dict

    tmp = exec_files_to_dict(str(datadir.join("test.py")))

    assert "__builtins__" not in tmp
    assert "sys" not in tmp
    assert "my_path" in tmp
    assert "banana" in tmp
    assert tmp["banana"] == "yellow"


@pytest.mark.parametrize("s, d, keep_double_brackets, expected", [
    (
        "here is fancy test {var1} to replace\n and ${{var1}} to keep",
        {"var1": "var1_value", "var2": "var2_value"},
        None,
        "here is fancy test var1_value to replace\n and ${var1} to keep"
    ), (
        "here is fancy test {var1} to replace\n and ${{var1}} to keep",
        {"var1": "var1_value", "var2": "var2_value"},
        False,
        "here is fancy test var1_value to replace\n and ${var1} to keep"
    ), (
        "here is fancy test {var1} to replace\n and ${{var1}} to keep",
        {"var1": "var1_value", "var2": "var2_value"},
        True,
        "here is fancy test var1_value to replace\n and ${{var1}} to keep"
    ), (
        "here is fancy test {var1} to replace\n and ${{var1}} to keep\n and {var2} is recursive",
        {"var1": "var1_value", "var2": "var2_{var1}_value"},
        None,
        "here is fancy test var1_value to replace\n and ${var1} to keep\n and var2_var1_value_value is recursive"
    )
])
def test_format_recursively(s: str, d: dict, keep_double_brackets: bool, expected: str):
    from akrr.util import format_recursively
    if keep_double_brackets is None:
        assert format_recursively(s, d) == expected
    else:
        assert format_recursively(s, d, keep_double_brackets) == expected


@pytest.mark.parametrize("s, ds, expected", [
    (
        "here is fancy test @var1@ to replace\n and @var2@ to replace too",
        [{"var1": "var1_value", "var2": "var2_value"}, {"var2": "var2_new_value"}],
        "here is fancy test var1_value to replace\n and var2_new_value to replace too"
    ),
])
def test_replace_at_var_at(s, ds, expected):
    from akrr.util import replace_at_var_at
    assert replace_at_var_at(s, ds) == expected

