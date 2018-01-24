import re
import os
import sys
import time

#Set proper path for stand alone test runs
if __name__ == "__main__":
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),'../..'))

import akrr.appkernelsparsers.akrrappkeroutputparser
from akrr.appkernelsparsers.akrrappkeroutputparser import AppKerOutputParser,total_seconds

def processAppKerOutput(appstdout=None,stdout=None,stderr=None,geninfo=None,appKerNResVars=None):
    #set App Kernel Description
    parser=AppKerOutputParser(
        name             = 'test',
        version          = 1,
        description      = "test the resource deployment",
        url              = 'http://xdmod.buffalo.edu',
        measurement_name = 'test'
    )
    #set obligatory parameters and statistics
    #set common parameters and statistics
    parser.setCommonMustHaveParsAndStats()
    #set app kernel custom sets
    parser.setMustHaveStatistic('Wall Clock Time')
    parser.setMustHaveStatistic('Shell is BASH')
    #parse common parameters and statistics
    parser.parseCommonParsAndStats(appstdout,stdout,stderr,geninfo)
    
    #set statistics
    if hasattr(parser,'wallClockTime'):
        parser.setStatistic("Wall Clock Time", total_seconds(parser.wallClockTime), "Second")
    
    #read output
    lines=[]
    if os.path.isfile(stdout):
        fin=open(stdout,"rt")
        lines=fin.readlines()
        fin.close()
    
    #process the output
    parser.setStatistic('Shell is BASH', 0)
    j=0
    while j<len(lines):
       if lines[j].count("Checking that the shell is BASH")>0 and lines[j+1].count("bash")>0:
           parser.setStatistic('Shell is BASH', 1)
       j+=1
    
    if stdout!=None:
        if hasattr(parser,'filesExistance'):
            for k,v in list(parser.filesExistance.items()):
                parser.setStatistic(k+" exists",int(v))
        if hasattr(parser,'dirAccess'):
            for k,v in list(parser.dirAccess.items()):
                parser.setStatistic(k+" accessible",int(v))
    
    if __name__ == "__main__":
        #output for testing purpose
        print(("parsing complete:",parser.parsingComplete()))
        parser.printParsNStatsAsMustHave()
        print((parser.getXML()))
    
    #return complete XML overwize return None
    return parser.getXML()
    
    
if __name__ == "__main__":
    """stand alone testing"""
    jobdir=sys.argv[1]
    print(("Proccessing Output From",jobdir))
    processAppKerOutput(appstdout=os.path.join(jobdir,"appstdout"),
                        stdout=os.path.join(jobdir,"stdout"),
                        stderr=os.path.join(jobdir,"stderr"),
                        geninfo=os.path.join(jobdir,"gen.info"))
    
    

