import re
import os
import sys

#Set proper path for stand alone test runs
if __name__ == "__main__":
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),'../..'))

import akrr.appkernelsparsers.akrrappkeroutputparser
from akrr.appkernelsparsers.akrrappkeroutputparser import AppKerOutputParser,total_seconds

#graph500/run input$numCores

def processAppKerOutput(appstdout=None,stdout=None,stderr=None,geninfo=None,appKerNResVars=None):
    #set App Kernel Description
    parser=AppKerOutputParser(
        name             = 'xdmod.benchmark.graph.graph500',
        version          = 1,
        description      = "Graph500 Benchmark",
        url              = 'http://www.Graph500.org',
        measurement_name = 'Graph500'
    )
    #set obligatory parameters and statistics
    #set common parameters and statistics
    parser.setCommonMustHaveParsAndStats()
    #set app kernel custom sets  
    parser.setMustHaveParameter('App:Version')
    parser.setMustHaveParameter('Edge Factor')
    parser.setMustHaveParameter('Input File')
    parser.setMustHaveParameter('Number of Roots to Check')
    parser.setMustHaveParameter('Number of Edges')
    parser.setMustHaveParameter('Number of Vertices')
    parser.setMustHaveParameter('Scale')
    
    parser.setMustHaveStatistic('Harmonic Mean TEPS')
    parser.setMustHaveStatistic('Harmonic Standard Deviation TEPS')
    parser.setMustHaveStatistic('Median TEPS')
    parser.setMustHaveStatistic('Wall Clock Time')
        
    #parse common parameters and statistics
    parser.parseCommonParsAndStats(appstdout,stdout,stderr,geninfo)
    
    if hasattr(parser,'appKerWallClockTime'):
        parser.setStatistic("Wall Clock Time", total_seconds(parser.appKerWallClockTime), "Second")
    elif hasattr(parser,'wallClockTime'):
        parser.setStatistic("Wall Clock Time", total_seconds(parser.wallClockTime), "Second")  
    
    #read output
    lines=[]
    if os.path.isfile(appstdout):
        fin=open(appstdout,"rt")
        lines=fin.readlines()
        fin.close()
    
    #process the output
    parser.successfulRun=True
    Nerrors=0
    j=0
    while j<len(lines):
        m=re.match(r'^Graph500 version:\s+(.+)',lines[j])
        if m:parser.setParameter("App:Version",m.group(1).strip())
        
        m=re.match(r'ERROR:\s+(.+)',lines[j])
        if m:Nerrors+=1
        
        m=re.match(r'^Reading input from\s+(.+)',lines[j])
        if m:parser.setParameter("Input File",m.group(1))
       
        m=re.match(r'^SCALE:\s+(\d+)',lines[j])
        if m:parser.setParameter("Scale",m.group(1))
       
        m=re.match(r'^edgefactor:\s+(\d+)',lines[j])
        if m:parser.setParameter("Edge Factor",m.group(1))

        m=re.match(r'^NBFS:\s+(\d+)',lines[j])
        if m:parser.setParameter("Number of Roots to Check",m.group(1))
    
        m=re.match(r'^median_TEPS:\s+(\d[0-9.e\+]+)',lines[j])
        if m:parser.setStatistic("Median TEPS", m.group(1), "Traversed Edges Per Second" )
    
        m=re.match(r'^harmonic_mean_TEPS:\s+(\d[0-9.e\+]+)',lines[j])
        if m:
            parser.successfulRun=True
            parser.setStatistic("Harmonic Mean TEPS", m.group(1), "Traversed Edges Per Second" )
    
        m=re.match(r'^harmonic_stddev_TEPS:\s+(\d[0-9.e\+]+)',lines[j])
        if m:parser.setStatistic("Harmonic Standard Deviation TEPS", m.group(1), "Traversed Edges Per Second" )
    
        m=re.match(r'^median_validate:\s+([\d.]+)\s+s',lines[j])
        if m:parser.setStatistic("Median Validation Time", m.group(1), "Second" )
    
        m=re.match(r'^mean_validate:\s+([\d.]+)\s+s',lines[j])
        if m:parser.setStatistic("Mean Validation Time", m.group(1), "Second" )
    
        m=re.match(r'^stddev_validate:\s+([\d.]+)\s+s',lines[j])
        if m:parser.setStatistic("Standard Deviation Validation Time", m.group(1), "Second" )
            
        j+=1
    if Nerrors>0:
        parser.successfulRun=False

    if parser.getParameter('Scale')!=None and parser.getParameter('Edge Factor')!=None :
        SCALE=int(parser.getParameter('Scale'))
        edgefactor=int(parser.getParameter('Edge Factor'))
        parser.setParameter("Number of Vertices",2**SCALE)
        parser.setParameter("Number of Edges",edgefactor*2**SCALE)
        
        
    if __name__ == "__main__":
        #output for testing purpose
        parser.parsingComplete(True)
        print("parsing complete:",parser.parsingComplete())
        parser.printParsNStatsAsMustHave()
        print(parser.getXML())
    
    #return complete XML overwize return None
    return parser.getXML()
    
    
if __name__ == "__main__":
    """stand alone testing"""
    jobdir=sys.argv[1]
    print("Proccessing Output From",jobdir)
    processAppKerOutput(appstdout=os.path.join(jobdir,"appstdout"),geninfo=os.path.join(jobdir,"gen.info"))
    
    

