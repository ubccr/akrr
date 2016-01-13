import re
import os
import sys

#Set proper path for stand alone test runs
if __name__ == "__main__":
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),'../../src'))

import akrrappkeroutputparser
from akrrappkeroutputparser import AppKerOutputParser

def processAppKerOutput(appstdout=None,stdout=None,stderr=None,geninfo=None,appKerNResVars=None):
    #set App Kernel Description
    parser=AppKerOutputParser(
        name             = 'xdmod.app.md.charmm',
        version          = 1,
        description      = "CHARMM: Chemistry at Harvard Macromolecular Mechanics",
        url              = 'http://www.charmm.org',
        measurement_name = 'CHARMM'
    )
    #set obligatory parameters and statistics
    #set common parameters and statistics
    parser.setCommonMustHaveParsAndStats()
    #set app kernel custom sets
    parser.setMustHaveParameter('App:Version')
    parser.setMustHaveParameter('Input:Number of Angles')
    parser.setMustHaveParameter('Input:Number of Atoms')
    parser.setMustHaveParameter('Input:Number of Bonds')
    parser.setMustHaveParameter('Input:Number of Dihedrals')
    parser.setMustHaveParameter('Input:Number of Steps')
    parser.setMustHaveParameter('Input:Timestep')

    parser.setMustHaveStatistic('Molecular Dynamics Simulation Performance')
    parser.setMustHaveStatistic('Time Spent in External Energy Calculation')
    parser.setMustHaveStatistic('Time Spent in Integration')
    parser.setMustHaveStatistic('Time Spent in Internal Energy Calculation')
    parser.setMustHaveStatistic('Time Spent in Non-Bond List Generation')
    parser.setMustHaveStatistic('Time Spent in Waiting (Load Unbalance-ness)')
    parser.setMustHaveStatistic('User Time')
    parser.setMustHaveStatistic('Wall Clock Time')

    
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
    wallClockTime = 0.0
    numSteps = 0
    stepSize = 0.0
    timeBreakdownColumns=None
    numAtoms = 0
    numBonds = 0
    numAngles = 0
    numDihedrals = 0
    
    j=0
    while j<len(lines):
       
        m0=re.search(r'\s+Chemistry at HARvard Macromolecular Mechanics',lines[j])
        m1=re.search(r'\sVersion\s+([\da-zA-Z]+)',lines[j+1])
        if m0 and m1:parser.setParameter("App:Version",m1.group(1).strip())
        
        if re.search(r'Summary of the structure file counters',lines[j]):
            j+=1
            for k in range(256):
                if re.search(r'CHARMM>',lines[j]):break
             
                m=re.search(r'Number of atoms\s+=\s+(\d+)',lines[j])
                if m:numAtoms+=int(m.group(1).strip())
             
                m=re.search(r'Number of bonds\s+=\s+(\d+)',lines[j])
                if m:numBonds+=int(m.group(1).strip())
             
                m=re.search(r'Number of angles\s+=\s+(\d+)',lines[j])
                if m:numAngles+=int(m.group(1).strip())
             
                m=re.search(r'Number of dihedrals\s+=\s+(\d+)',lines[j])
                if m:numDihedrals+=int(m.group(1).strip())
             
                j+=1
        
        if re.search(r'<MAKGRP> found',lines[j]):
            j+=1
            for k in range(256):
                if re.search(r'NUMBER OF DEGREES OF FREEDOM',lines[j]):break
             
                m=re.search(r'NSTEP\s+=\s+(\d+)',lines[j])
                if m:
                    numSteps=int(m.group(1).strip())
                    parser.setParameter( "Input:Number of Steps", numSteps )
                
                if re.search(r'TIME STEP\s+=',lines[j]):
                    m=re.search(r'([\d\-Ee\.]+)\s+PS',lines[j])
                    if m:
                        stepSize = 1000.0*float(m.group(1).strip())
                        parser.setParameter( "Input:Timestep", stepSize *1e-15, "Second per Step" )
                j+=1
        
        if re.search(r'NORMAL TERMINATION BY NORMAL STOP',lines[j]):
            parser.successfulRun=True
        
        if re.search(r'JOB ACCOUNTING INFORMATION',lines[j]):
            parser.successfulRun=True
            
            j+=1
            for k in range(256):
                if j>len(lines)-1: break
                m=re.search(r'ELAPSED TIME:\s*([\d\.]+)\s*MINUTES',lines[j])
                if m:
                    wallClockTime=60.0 * float(m.group(1).strip())
                    parser.setStatistic( "Wall Clock Time", wallClockTime, "Second" )
                
                m=re.search(r'CPU TIME:\s*([\d\.]+)\s*MINUTES',lines[j])
                if m:parser.setStatistic( "User Time", 60.0 * float(m.group(1).strip()), "Second" )
                
                m=re.search(r'ELAPSED TIME:\s*([\d\.]+)\s*SECONDS',lines[j])
                if m:
                    wallClockTime=float(m.group(1).strip())
                    parser.setStatistic( "Wall Clock Time", wallClockTime, "Second" )
                
                m=re.search(r'CPU TIME:\s*([\d\.]+)\s*SECONDS',lines[j])
                if m:parser.setStatistic( "User Time", m.group(1).strip(), "Second" )
                
                j+=1
            if j>len(lines)-1: break
        if re.search(r'Parallel load balance \(sec',lines[j]):
            j+=1
            # grab the column headers from the output, e.g.
            #
            # Parallel load balance (sec.):
            # Node Eext      Eint   Wait    Comm    List   Integ   Total
            #   0   205.5     6.4     1.2    31.2    23.2     2.8   270.4
            #   1   205.2     7.3     1.1    31.2    23.3     3.2   271.2
            #   2   205.2     7.7     0.6    32.3    23.3     3.2   272.3
            #   3   205.2     7.8     0.6    32.1    23.3     3.3   272.3
            #PARALLEL> Average timing for all nodes:
            #   4   205.3     7.3     0.9    31.7    23.3     3.1   271.6
            timeBreakdownColumns=lines[j].strip().split()
        if re.search(r'PARALLEL>\s*Average timing for all nodes',lines[j]) and timeBreakdownColumns:
            j+=1
            timeBreakdown = lines[j].strip().split()
            if len(timeBreakdownColumns)==len(timeBreakdown):
                for k in range(len(timeBreakdown)):
                    if timeBreakdownColumns[k] == "Eext":
                        parser.setStatistic( "Time Spent in External Energy Calculation",   timeBreakdown[k], "Second" )
                    if timeBreakdownColumns[k] == "Eint":
                        parser.setStatistic( "Time Spent in Internal Energy Calculation",   timeBreakdown[k], "Second" ) 
                    if timeBreakdownColumns[k] == "Wait":
                        parser.setStatistic( "Time Spent in Waiting (Load Unbalance-ness)", timeBreakdown[k], "Second" ) 
                    if timeBreakdownColumns[k] == "List":
                        parser.setStatistic( "Time Spent in Non-Bond List Generation",      timeBreakdown[k], "Second" ) 
                    if timeBreakdownColumns[k] == "Integ":
                        parser.setStatistic( "Time Spent in Integration",                   timeBreakdown[k], "Second" ) 
            
        j+=1
    if numAtoms>0:parser.setParameter( "Input:Number of Atoms",     numAtoms )
    if numBonds>0:parser.setParameter( "Input:Number of Bonds",     numBonds )
    if numAngles>0:parser.setParameter( "Input:Number of Angles",    numAngles )
    if numDihedrals>0:parser.setParameter( "Input:Number of Dihedrals", numDihedrals )
    
    if wallClockTime>0.0 and numSteps>0 and stepSize>0.0:
        # $stepSize is in femtoseconds
        # $wallClockTime is in seconds
        parser.setStatistic( "Molecular Dynamics Simulation Performance", ( 1e-6 * stepSize * numSteps ) / ( wallClockTime / 86400.0 )*1e-9, "Second per Day" )
    
    if __name__ == "__main__":
        #output for testing purpose
        print "parsing complete:",parser.parsingComplete()
        parser.printParsNStatsAsMustHave()
        print parser.getXML()
    
    #return complete XML overwize return None
    return parser.getXML()
    
    
if __name__ == "__main__":
    """stand alone testing"""
    jobdir=sys.argv[1]
    print "Proccessing Output From",jobdir
    processAppKerOutput(appstdout=os.path.join(jobdir,"appstdout"),geninfo=os.path.join(jobdir,"gen.info"))
    
    

