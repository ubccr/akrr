from .functional import __or
from .generators import generateChars, generateNumber


def which(program):
    import os
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None

import re
import datetime

def getFormatedRepeatIn(repeat_in):
    repeatInFin = None
    if repeat_in == None:
        return None

    repeat_in = repeat_in.strip()
    if repeatInFin == None or repeatInFin == '':
        match = re.match(r'(\d+)-(\d+)-(\d+) (\d+):(\d+):(\d+)', repeat_in, 0)
        if match != None:
            g = match.group(1, 2, 3, 4, 5, 6)
            repeatInFin = "%01d-%02d-%03d %02d:%02d:%02d" % (
                int(g[0]), int(g[1]), int(g[2]), int(g[3]), int(g[4]), int(g[5]))
    if repeatInFin == None:
        match = re.match(r'(\d+)-(\d+)-(\d+) (\d+):(\d+)', repeat_in, 0)
        if match != None:
            g = match.group(1, 2, 3, 4, 5)
            repeatInFin = "%01d-%02d-%03d %02d:%02d:%02d" % (int(g[0]), int(g[1]), int(g[2]), int(g[3]), int(g[4]), 0)
    if repeatInFin == None:
        match = re.match(r'(\d+) (\d+):(\d+):(\d+)', repeat_in, 0)
        if match != None:
            g = match.group(1, 2, 3, 4)
            repeatInFin = "%01d-%02d-%03d %02d:%02d:%02d" % (0, 0, int(g[0]), int(g[1]), int(g[2]), int(g[3]))
    if repeatInFin == None:
        match = re.match(r'(\d+) (\d+):(\d+)', repeat_in, 0)
        if match != None:
            g = match.group(1, 2, 3)
            repeatInFin = "%01d-%02d-%03d %02d:%02d:%02d" % (0, 0, int(g[0]), int(g[1]), int(g[2]), 0)
    if repeatInFin == None:
        match = re.match(r'(\d+):(\d+):(\d+)', repeat_in, 0)
        if match != None:
            g = match.group(1, 2, 3)
            repeatInFin = "%01d-%02d-%03d %02d:%02d:%02d" % (0, 0, 0, int(g[0]), int(g[1]), int(g[2]))
    if repeatInFin == None:
        match = re.match(r'(\d+):(\d+)', repeat_in, 0)
        if match != None:
            g = match.group(1, 2)
            repeatInFin = "%01d-%02d-%03d %02d:%02d:%02d" % (0, 0, 0, int(g[0]), int(g[1]), 0)
    if repeatInFin == None:
        match = re.match(r'(\d+)', repeat_in, 0)
        if match != None:
            g = match.group(1)
            repeatInFin = "%01d-%02d-%03d %02d:%02d:%02d" % (0, 0, int(g[0]), 0, 0, 0)
    #if repeatInFin==None:
    #    raise IOError("Incorrect data-time format for repeating period")
    #print 'repeatInFin',repeat_in,repeatInFin
    return repeatInFin

def getTimeDeltaRepeatIn(repeat_in):
    repeatInFin=None
    if repeat_in==None:
        raise IOError("There is no repeating period")
    repeatInFin=getFormatedRepeatIn(repeat_in)
    if repeatInFin==None:
        raise IOError("Incorrect data-time format for repeating period")
    
    #check the repeat values
    match = re.match( r'(\d+)-(\d+)-(\d+) (\d+):(\d+):(\d+)', repeatInFin, 0)
    g=match.group(1,2,3,4,5,6)
    tao=(int(g[0]),int(g[1]),int(g[2]),int(g[3]),int(g[4]),int(g[5]))
    td=datetime.timedelta(tao[2],tao[3],tao[4],tao[5])
    if tao[0]!=0 or tao[1]!=0:
        if tao[2]!=0 or tao[3]!=0 or tao[4]!=0 or tao[5]!=0:
            raise IOError("If repeating period is calendar months or years then increment in day/hours/mins/secs should be zero.")
    return td

def getFormatedTimeToStart(time_to_start):
    #determine timeToStart
    timeToStart = None
    if time_to_start == None or time_to_start == "":  #i.e. start now
        timeToStart = datetime.datetime.today()

    if timeToStart == None:
        iform = 0
        datetimeformats = ["%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S", "%y-%m-%d %H:%M:%S", "%y-%m-%d %H:%M"]
        while not (timeToStart != None or iform >= len(datetimeformats)):
            try:
                timeToStart = datetime.datetime.strptime(time_to_start, datetimeformats[iform])
            except:
                iform += 1
    if timeToStart == None:
        iform = 0
        datetimeformats = ["%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S"]
        while not (timeToStart != None or iform >= len(datetimeformats)):
            try:
                timeToStart = datetime.datetime.strptime(
                    datetime.datetime.today().strftime("%Y-%m-%d ") + time_to_start, datetimeformats[iform])
            except:
                iform += 1
    #if timeToStart==None:
    #    raise IOError("Incorrect data-time format")
    if timeToStart == None:
        return None
    else:
        return timeToStart.strftime("%Y-%m-%d %H:%M:%S")

def getDatatimeTimeToStart(time_to_start):
    timeToStart=getFormatedTimeToStart(time_to_start)
    if timeToStart==None:
        raise IOError("Incorrect data-time format for time_to_start")
    timeToStart=datetime.datetime.strptime(timeToStart,"%Y-%m-%d %H:%M:%S")
    return timeToStart


def log_input(message, *args):
    from . import colorize
    
    if message:
        if len(args) > 0:
            formatted_message = message.format(*args)
        else:
            formatted_message = message
    else:
        formatted_message = ''
        
    print('[' + colorize.purple('INPUT') + ']: ' + formatted_message)

