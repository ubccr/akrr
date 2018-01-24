"""
logging utilities, custom exceptions etc.
"""
ERROR_GENERAL = 'Error: '
ERROR_CANT_CONNECT = "Can't establish a connetion."
ERROR_REMOTE_FILES = "Can't access files/directories."
ERROR_REMOTE_JOB = "Can't run job."


class akrrError(Exception):
    def __init__(self, errcode="Unknown", errmsg="No message", extra=None):
        self.code = errcode
        self.msg = errmsg
        self.extra = extra

    def __str__(self):
        if self.extra == None:
            return self.code + self.msg
        else:
            return self.code + " " + self.msg + " " + str(self.extra)
        
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    
def log(message,highlight="none"):
    """
    Function that will log the provided message to stdout.
    """
    if highlight=="ok" or highlight.lower()[0]=='o':
        print(bcolors.OKGREEN+message+bcolors.ENDC)
    elif highlight=="warning" or highlight.lower()[0]=='w':
        print(bcolors.WARNING+message+bcolors.ENDC)
    elif highlight=="error" or highlight.lower()[0]=='e':
        print(bcolors.FAIL+message+bcolors.ENDC)
    elif highlight=="blue" or highlight.lower()[0]=='b':
        print(bcolors.OKBLUE+message+bcolors.ENDC)   
    else:
        print(message)
def logstr(message,highlight="none"):
    """
    Function that will higlight string
    """
    msg=""
    if highlight=="ok" or highlight.lower()[0]=='o':
        msg+=bcolors.OKGREEN+message+bcolors.ENDC
    elif highlight=="warning" or highlight.lower()[0]=='w':
        msg+=bcolors.WARNING+message+bcolors.ENDC
    elif highlight=="error" or highlight.lower()[0]=='w':
        msg+=bcolors.FAIL+message+bcolors.ENDC
    else:
        msg+=message
    return msg
def logerr(message,message2=None):
    """
    Function that will log the provided message to stdout.
    """
    print(bcolors.FAIL)
    print(">ERROR"+">"*74)
    print()
    print(message)
    print(bcolors.ENDC)
    if message2!=None:
        print(bcolors.FAIL)
        print("="*80)
        print(bcolors.ENDC)
        print()
        print(message2)
    
    print(bcolors.FAIL+"<ERROR"+"<"*74)
    print(bcolors.ENDC)

