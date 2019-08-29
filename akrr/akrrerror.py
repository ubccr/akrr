"""
akrr exceptions etc.
"""


class AkrrBaseException(Exception):
    pass


class AkrrValueException(AkrrBaseException):
    pass


class AkrrRestAPIException(AkrrBaseException):
    pass


class AkrrError(AkrrBaseException):
    def __init__(self, errmsg=None, errcode=None, extra=None, e=None):
        self.code = errcode
        self.msg = errmsg
        self.extra = extra
        self.e = e

    def __str__(self):
        s = ""
        if self.code is not None:
            s = s + str(self.code) + "\n"
        if self.msg is not None:
            s = s + str(self.msg) + "\n"
        if self.extra is not None:
            s = s + str(self.extra) + "\n"
        if self.e is not None:
            s = s + str(self.e) + "\n"
        if s == "":
            s = "No message"
        return s


class AkrrOpenStackException(AkrrBaseException):
    pass