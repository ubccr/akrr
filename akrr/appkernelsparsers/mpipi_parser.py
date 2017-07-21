# Generic Parser
import re
import os
import sys

#Set proper path for stand alone test runs
if __name__ == "__main__":
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),'../..'))

import akrr.appkernelsparsers.akrrappkeroutputparser
from akrr.appkernelsparsers.akrrappkeroutputparser import AppKerOutputParser,total_seconds

def processAppKerOutput(appstdout=None,stdout=None,stderr=None,geninfo=None,appKerNResVars=None):
    #set App Kernel Description
    if(appKerNResVars!=None and 'app' in appKerNResVars and 'name' in appKerNResVars['app']):
        akname=appKerNResVars['app']['name']
    else:
        akname='unknown'
   
    #initiate parser
    parser=AppKerOutputParser(
        name             = akname
    )
    #set obligatory parameters and statistics
    #set common parameters and statistics (App:ExeBinSignature and RunEnv:Nodes)
    parser.setCommonMustHaveParsAndStats()
    #set app kernel custom sets
    parser.setMustHaveParameter('App:ExeBinSignature')
    parser.setMustHaveParameter('App:Version')
    parser.setMustHaveParameter('Number of Darts Throws')
    parser.setMustHaveParameter('Number of Rounds')
    parser.setMustHaveParameter('RunEnv:Nodes')
    
    parser.setMustHaveStatistic('Darts Throws per Second')
    parser.setMustHaveStatistic('Time for PI Calculation')
    parser.setMustHaveStatistic('Wall Clock Time')

    #parse common parameters and statistics
    parser.parseCommonParsAndStats(appstdout,stdout,stderr,geninfo)

    if hasattr(parser,'appKerWallClockTime'):
        parser.setStatistic("Wall Clock Time", parser.appKerWallClockTime.total_seconds(), "Second")
    
    #Here can be custom output parsing
    #read output
    lines=[]
    if os.path.isfile(appstdout):
        fin=open(appstdout,"rt")
        lines=fin.readlines()
        fin.close()
     
    #process the output
    parser.successfulRun=False
    j=0
    while j<len(lines):
        m=re.search(r'version:\s+(.+)',lines[j])
        if m:parser.setParameter('App:Version',m.group(1))
        
        m=re.search(r'number of throws at dartboard:\s+(\d+)',lines[j])
        if m:parser.setParameter('Number of Darts Throws',m.group(1))
        
        m=re.search(r'number of rounds for dartz throwing\s+(\d+)',lines[j])
        if m:parser.setParameter('Number of Rounds',m.group(1))
         
        m=re.search(r'Time for PI calculation:\s+([0-9\.]+)',lines[j])
        if m:parser.setStatistic("Time for PI Calculation",m.group(1),"Seconds")
        
        m=re.search(r'Giga Darts Throws per Second \(GDaPS\):\s+([0-9\.]+)',lines[j])
        if m:parser.setStatistic("Darts Throws per Second",m.group(1),"GDaPS")

        m=re.search(r'Giga Darts Throws per Second',lines[j])
        if m:parser.successfulRun=True
         
        j+=1
        
    
    if __name__ == "__main__":
        #output for testing purpose
        print "Parsing complete:",parser.parsingComplete(Verbose=True)
        print "Following statistics and parameter can be set as obligatory:"
        parser.printParsNStatsAsMustHave()
        print "\nResulting XML:"
        print parser.getXML()
    
    #return complete XML otherwise return None
    return parser.getXML()
    
    
if __name__ == "__main__":
    """stand alone testing"""
    jobdir=sys.argv[1]
    print "Proccessing Output From",jobdir
    testParser(jobdir,processAppKerOutput)

    
    

