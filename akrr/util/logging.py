"""
Provide standardized logging output
"""

from . import colorize


class LogLevel(object):

    DEBUG = 1;
    INFO = 4;
    WARNING = 8;
    ERROR = 16;
    INPUT=32;

    messages = {DEBUG: 'DEBUG', INFO: 'INFO', WARNING: 'WARNING', ERROR: 'ERROR', INPUT:'INPUT'}


def __log(level, message, *args):
    """
    Print the provided message at the provided level.

    :param level: corresponds to one of the LogLevel.[DEBUG, TRACE, INFO, WARNING, ERROR] values.
    :param message: the message to be logged.
    :param args: the arguments message is to be formatted with.
    :return: void
    """
    if not level:
        raise AssertionError('Must provide a level in order to log a message')
    if message:
        if len(args) > 0:
            formatted_message = message.format(*args)
        else:
            formatted_message = message
        formatted_message = '{0}\n'.format(formatted_message)
    else:
        formatted_message = ''

    if level == LogLevel.ERROR:
        write('[' + colorize.red(LogLevel.messages.get(level)) + ']: ' + formatted_message)
    elif level == LogLevel.WARNING:
        write('[' + colorize.yellow(LogLevel.messages.get(level)) + ']: ' + formatted_message)
    elif level == LogLevel.INFO:
        write('[' + colorize.green(LogLevel.messages.get(level)) + ']: ' + formatted_message)
    elif level == LogLevel.DEBUG:
        write('[' + colorize.blue(LogLevel.messages.get(level)) + ']: ' + formatted_message)
    elif level == LogLevel.INPUT:
        write('[' + colorize.purple(LogLevel.messages.get(level)) + ']: ' + formatted_message)

def write(message):
    print(message)

def error(message, *args):
    __log(LogLevel.ERROR, message, *args)


def warning(message, *args):
    __log(LogLevel.WARNING, message, *args)


def info(message, *args):
    __log(LogLevel.INFO, message, *args)

def input(message, *args):
    __log(LogLevel.INPUT, message, *args)
    
def debug(message, *args):
    __log(LogLevel.DEBUG, message, *args)
    
