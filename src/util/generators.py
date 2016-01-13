import string
import random

from functional import __or


def generateChars(*args, **kwargs):
    """Generates 'size' characters from the 'chars' list of characters."""
    size = __or(args, 0, kwargs.get('size', 0))
    chars = __or(args, 1, kwargs.get('chars', string.ascii_lowercase + string.ascii_uppercase))
    return ''.join(random.choice(chars) for _ in range(size))


def generateNumber(*args, **kwargs):
    """
    Generates an integer between a 'low' and a 'high' inclusive.
    """
    low = __or(args, 0, kwargs.get('low', 0))
    high = __or(args, 1, kwargs.get('high', 1))
    if low <= high:
        return random.randint(low, high)
    else:
        raise AssertionError('low must be less than or equal to high')
