"""
Different utils for interaction with user
"""
from typing import Callable, Sequence, Union, ClassVar
from enum import Enum

def ask(header, validate: Callable[[str], bool] = None, default: str = None):
    """
    Ask user question, validate if requested and return entered value
    """
    import akrr.util.log as log
    from akrr.util import smart_str_merge

    prompt = "[%s] " % default if default is not None else ""
    while True:
        log.log_input(header + ":")

        user_input = input(prompt)
        if default is not None and user_input == "":
            user_input = default
        if validate(user_input):
            log.empty_line()
            return user_input
        else:
            log.error("Incorrect value try again")


def multiple_choice(header, choices: Sequence[str], default: str = None) -> str:
    """
    Ask user multiple choice question, check for correctness and return entered value
    """
    import akrr.util.log as log
    from akrr.util import smart_str_merge

    prompt = "[%s] " % default if default is not None else ""
    while True:
        log.log_input(header + " (%s):", smart_str_merge(choices))

        user_input = input(prompt)
        if default is not None and user_input == "":
            user_input = default
        if user_input in choices:
            log.empty_line()
            return user_input
        else:
            log.error("Incorrect value try again")


def multiple_choice_enum(header, enum_class: ClassVar[Enum], default: Enum = None) -> ClassVar[Enum]:
    """
    Ask user multiple choice question, choice is from enum_class Enum class, check for correctness and
    return Enum from entered value
    """
    choices = [str(v.value) for v in enum_class]
    return enum_class[multiple_choice(header, choices, default=None if default is None else str(default.value))]
