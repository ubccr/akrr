import re
import os
import sys

#Set proper path for stand alone test runs
if __name__ == "__main__":
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),'../..'))

import akrr.appkernelsparsers.akrrappkeroutputparser
from akrr.appkernelsparsers.akrrappkeroutputparser import AppKerOutputParser

def processAppKerOutput(appstdout=None,stdout=None,stderr=None,geninfo=None,appKerNResVars=None):
    #set App Kernel Description
    parser=AppKerOutputParser(
        name             = 'xdmod.app.md.lammps',
        version          = 1,
        description      = "LAMMPS: Large-scale Atomic/Molecular Massively Parallel Simulator",
        url              = 'http://lammps.sandia.gov',
        measurement_name = 'LAMMPS'
    )
    #set obligatory parameters and statistics
    #set common parameters and statistics
    parser.setCommonMustHaveParsAndStats()
    #set app kernel custom sets  
    parser.setMustHaveParameter('App:Version')
    parser.setMustHaveParameter('Input:Number of Atoms')
    parser.setMustHaveParameter('Input:Number of Steps')
    parser.setMustHaveParameter('Input:Timestep')
    
    parser.setMustHaveStatistic('Molecular Dynamics Simulation Performance')
    parser.setMustHaveStatistic('Per-Process Memory')
    parser.setMustHaveStatistic('Time Spent in Bond Potential Calculation')
    parser.setMustHaveStatistic('Time Spent in Communication')
    parser.setMustHaveStatistic('Time Spent in Long-Range Coulomb Potential (K-Space) Calculation')
    parser.setMustHaveStatistic('Time Spent in Neighbor List Regeneration')
    parser.setMustHaveStatistic('Time Spent in Pairwise Potential Calculation')
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
    wallClockTime=None
    simulationUnits=None
    numSteps=None
    stepSize=None
    j=0
    while j<len(lines):
       
        m=re.match(r'^LAMMPS\s+\(([\w ]+)\)',lines[j])
        if m:parser.setParameter("App:Version",m.group(1).strip())
        
        m=re.match(r'^Memory usage per processor = ([\d\.]+) Mbyte',lines[j])
        if m:parser.setStatistic( "Per-Process Memory",m.group(1).strip(), "MByte" )
       
        m=re.match(r'^Loop time of ([\d\.]+) on',lines[j])
        if m:
            parser.successfulRun=True
            wallClockTime=float(m.group(1).strip())
            parser.setStatistic("Wall Clock Time", wallClockTime, "Second" )
            m1=re.search(r'(\d+) atoms',lines[j])
            if m1:parser.setParameter( "Input:Number of Atoms", m1.group(1).strip())
       
        m=re.match(r'^units\s+(\w+)',lines[j])
        if m:simulationUnits=m.group(1).strip().lower()
        
        m=re.match(r'^run\s+(\d+)',lines[j])
        if m:
            numSteps=int(m.group(1).strip())
            parser.setParameter("Input:Number of Steps", numSteps)
        
        m=re.match(r'^timestep\s+([\d\.]+)',lines[j])
        if m:stepSize=float(m.group(1).strip())
        
        m=re.match(r'^Pair\s+time.+= ([\d\.]+)',lines[j])
        if parser.successfulRun and m:
            parser.setStatistic("Time Spent in Pairwise Potential Calculation", m.group(1).strip(), "Second" )
        
        m=re.match(r'^Bond\s+time.+= ([\d\.]+)',lines[j])
        if parser.successfulRun and m:
            parser.setStatistic("Time Spent in Bond Potential Calculation", m.group(1).strip(), "Second" )
        
        m=re.match(r'^Kspce\s+time.+= ([\d\.]+)',lines[j])
        if parser.successfulRun and m:
            parser.setStatistic("Time Spent in Long-Range Coulomb Potential (K-Space) Calculation", m.group(1).strip(), "Second" )
        
        m=re.match(r'^Neigh\s+time.+= ([\d\.]+)',lines[j])
        if parser.successfulRun and m:
            parser.setStatistic("Time Spent in Neighbor List Regeneration", m.group(1).strip(), "Second" )
        
        m=re.match(r'^Comm\s+time.+= ([\d\.]+)',lines[j])
        if parser.successfulRun and m:
            parser.setStatistic("Time Spent in Communication", m.group(1).strip(), "Second" )
        
        j+=1
    
    if parser.successfulRun and numSteps and simulationUnits != "lj":
        # The default value for $stepSize is (see http://lammps.sandia.gov/doc/units.html):
        #
        #   0.005 tau for $simulationUnits eq "lj"
        #   1e-15 second for $simulationUnits eq "real" or "metal"
        #   1e-18 second for $simulationUnits eq "electron"
        #   1e-8  second for $simulationUnits eq "si" or "cgs"
    
        # If $simulationUnits is (see http://lammps.sandia.gov/doc/units.html)
        #
        #  "lj", the unit for $stepSize is tau
        #  "real" or "electron", the unit for $stepSize is 1e-15 second
        #  "metal", the unit for $stepSize is 1e-12 second
        #  "si" or "cgs", the unit for $stepSize is second
    
        # The default $simulationUnits is "lj"
        #
        # We ignore "lj" since "lj" is unitless.
        if stepSize==None:
            if simulationUnits == "real":stepSize = 1.0
            if simulationUnits.find("electron")>=0 or  simulationUnits.find("metal")>=0: stepSize = 0.001
            if simulationUnits.find("si")>=0 or  simulationUnits.find("cgs")>=0: stepSize = 1.0e-8
        
        stepSizeInSec=stepSize
        if stepSize:
            if simulationUnits.find("electron")>=0 or  simulationUnits.find("real")>=0: stepSizeInSec=stepSize*1.0e-15
            if simulationUnits=="metal":  stepSizeInSec=stepSize*1.0e-12
        if stepSizeInSec:
            parser.setParameter("Input:Timestep", stepSizeInSec, "Second per Step" );
            parser.setStatistic("Molecular Dynamics Simulation Performance", 1.0e-9*( 1.0e9 * stepSizeInSec * numSteps ) / ( wallClockTime / 86400.0 ), "Second per Day" )
    if __name__ == "__main__":
        #output for testing purpose
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
    
    

