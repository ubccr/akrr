"""
functions to highlight text in console output
"""


class Colors:
    PURPLE = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'

    colors = [PURPLE, BLUE, GREEN, YELLOW, RED]

    @staticmethod
    def is_color(value):
        if value is not None and value in Colors.colors:
            return True
        return False


def colorize(text, color):
    """
    Turns the provided text the provided color. It does this by wrapping it with the provided color code before
    and an end color code after the text.

    :param text: the textual input to be colored.
    :param color: the color to be used during the colorizing process.
    :return: color + text + end color.
    """
    if text and color and Colors.is_color(color):
        return color + text + Colors.ENDC
    elif text and color is not Colors.is_color(color):
        raise AssertionError('Color must be valid')
    else:
        return text


def purple(text):
    """
    Turns the provided text 'Purple'. It does this by wrapping it with a color code before
    and an end color code after the text.

    :param text the textual input that will be colored purple.
    :return: the text but wrapped in a color code that when output to stdout will be interpreted as purple.
    """
    return colorize(text, Colors.PURPLE)


def blue(text):
    """
    Turns the provided text 'Blue'. It does this by wrapping it with a color code before
    and an end color code after the text.

    :param text the textual input that will be colored blue.
    :return: the text but wrapped in a color code that when output to stdout will be interpreted as blue.
    """
    return colorize(text, Colors.BLUE)


def green(text):
    """
    Turns the provided text 'Green'. It does this by wrapping it with a color code before
    and an end color code after the text.

    :param text the textual input that will be colored green.
    :return: the text but wrapped in a color code that when output to stdout will be interpreted as green.
    """
    return colorize(text, Colors.GREEN)


def yellow(text):
    """
    Turns the provided text 'Yellow'. It does this by wrapping it with a color code before
    and an end color code after the text.

    :param text the textual input that will be colored yellow.
    :return: the text but wrapped in a color code that when output to stdout will be interpreted as yellow.
    """
    return colorize(text, Colors.YELLOW)


def red(text):
    """
    Turns the provided text 'Red'. It does this by wrapping it with a color code before
    and an end color code after the text.

    :param text the textual input that will be colored red.
    :return: the text but wrapped in a color code that when output to stdout will be interpreted as red.
    """
    return colorize(text, Colors.RED)
