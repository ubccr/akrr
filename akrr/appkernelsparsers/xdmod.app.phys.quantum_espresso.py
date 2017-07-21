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
        name             = 'xdmod.app.phys.quantum_espresso',
        version          = 1,
        description      = "Quantum ESPRESSO (PWSCF)",
        url              = 'http://www.quantum-espresso.org',
        measurement_name = 'Quantum_ESPRESSO'
    )
    #set obligatory parameters and statistics
    #set common parameters and statistics
    parser.setCommonMustHaveParsAndStats()
    #set app kernel custom sets  
    parser.setMustHaveParameter('App:Version')
    parser.setMustHaveParameter('Input:Number of Atoms per Cell')
    parser.setMustHaveParameter('Input:Number of Atomic Types')
    parser.setMustHaveParameter('Input:Number of Electrons')
    
    parser.setMustHaveStatistic('Wall Clock Time')
    parser.setMustHaveStatistic('User Time')
    parser.setMustHaveStatistic("Per-Process Dynamical Memory")
    parser.setMustHaveStatistic("Time Spent in Program Initialization")
    parser.setMustHaveStatistic("Time Spent in Electron Energy Calculation")
    parser.setMustHaveStatistic("Time Spent in Force Calculation")
    #This statistic probably was working for a different set of inputs, optional now
    #parser.setMustHaveStatistic("Time Spent in Stress Calculation")
    #This statistic probably was working for a different set of inputs, optional now
    #parser.setMustHaveStatistic("Time Spent in Potential Updates (Charge Density and Wavefunctions Extrapolations)")
    
    #parse common parameters and statistics
    parser.parseCommonParsAndStats(appstdout,stdout,stderr,geninfo)
    
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
       
        m=re.match(r'^\s+Program PWSCF\s+([\w\.]+)\s+starts',lines[j])
        if m:parser.setParameter("App:Version",m.group(1).strip())
       
        m=re.match(r'^\s+number of atoms\/cell\s*=\s*([\d\.]+)',lines[j])
        if m:parser.setParameter("Input:Number of Atoms per Cell",m.group(1).strip())
        
        m=re.match(r'^\s+number of atomic types\s*=\s*([\d\.]+)',lines[j])
        if m:parser.setParameter("Input:Number of Atomic Types",m.group(1).strip())
       
        m=re.match(r'^\s+number of electrons\s*=\s*([\d\.]+)',lines[j])
        if m:parser.setParameter("Input:Number of Electrons",m.group(1).strip())
        
        m=re.match(r'^\s+per-process dynamical memory:\s*([\d\.]+)\s*Mb',lines[j])
        if m:parser.setStatistic("Per-Process Dynamical Memory", (m.group(1).strip()), "MByte" );
        
        m=re.match(r'^\s+init_run\s+:\s*([\d\.]+)s CPU',lines[j])
        if m:parser.setStatistic("Time Spent in Program Initialization", (m.group(1).strip()), "Second" );
        
        m=re.match(r'^\s+electrons\s+:\s*([\d\.]+)s CPU',lines[j])
        if m:parser.setStatistic("Time Spent in Electron Energy Calculation", (m.group(1).strip()), "Second" );
        
        m=re.match(r'^\s+forces\s+:\s*([\d\.]+)s CPU',lines[j])
        if m:parser.setStatistic("Time Spent in Force Calculation", (m.group(1).strip()), "Second" );
        
        m=re.match(r'^\s+stress\s+:\s*([\d\.]+)s CPU',lines[j])
        if m:parser.setStatistic("Time Spent in Stress Calculation", (m.group(1).strip()), "Second" );
        
        m=re.match(r'^\s+update_pot\s+:\s*([\d\.]+)s CPU',lines[j])
        if m:parser.setStatistic("Time Spent in Potential Updates (Charge Density and Wavefunctions Extrapolations)", float(m.group(1).strip()), "Second" );
        
        m=re.match(r'^\s+PWSCF\s+:(.+CPU.+)',lines[j])
        if m:
            runTimes=m.group(1).strip().split(',')
            for runTime in runTimes:
                v=runTime.split()
                if len(v)>1:
                    sec=0.0
                    if v[0].lower().find("m")>=0:
                        m=re.match(r'^([0-9]+)m([0-9.]+)s',v[0])
                        sec=float(m.group(1))*60.0+float(m.group(2))
                    else:
                        m=re.match(r'^([0-9.]+)s',v[0])
                        sec=float(m.group(1))                    
                    if v[1].upper().find("CPU")>=0:
                        parser.setStatistic("User Time", sec, "Second" );
                    if v[1].upper().find("WALL")>=0:
                        parser.setStatistic("Wall Clock Time", sec, "Second" );
        
        
        if re.match(r'^\s+JOB DONE',lines[j]):
            parser.successfulRun=True
        j+=1
    if __name__ == "__main__":
        #output for testing purpose
        print "parsing complete:",parser.parsingComplete(True)
        if hasattr(parser, 'successfulRun'):print "successfulRun",parser.successfulRun
        parser.printParsNStatsAsMustHave()
        print parser.getXML()
        
    
    #return complete XML overwize return None
    return parser.getXML()
    
    
if __name__ == "__main__":
    """stand alone testing"""
    jobdir=sys.argv[1]
    print "Proccessing Output From",jobdir
    processAppKerOutput(appstdout=os.path.join(jobdir,"appstdout"),geninfo=os.path.join(jobdir,"gen.info"))
    
    

