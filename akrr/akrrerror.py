"""
akrr exceptions etc.
"""

class akrrError(Exception):
    def __init__(self, errmsg=None, errcode=None, extra=None,e=None):
        self.code = errcode
        self.msg = errmsg
        self.extra = extra
        self.e = e

    def __str__(self):
        s=""
        if self.errcode is not None:
            s=s+str(self.errcode)+"\n"
        if self.errmsg is not None:
            s=s+str(self.errmsg)+"\n"
        if self.extra is not None:
            s=s+str(self.extra)+"\n"
        if self.e is not None:
            s=s+str(self.e)+"\n"
        if s == "":
            s="No message"
        return s
