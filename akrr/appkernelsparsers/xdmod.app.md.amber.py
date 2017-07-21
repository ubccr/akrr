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
        name             = 'xdmod.app.md.amber',
        version          = 1,
        description      = "Amber: Assisted Model Building with Energy Refinement",
        url              = 'http://ambermd.org',
        measurement_name = 'Amber'
    )
    #set obligatory parameters and statistics
    #set common parameters and statistics
    parser.setCommonMustHaveParsAndStats()
    #set app kernel custom sets  
    parser.setMustHaveParameter('App:Version')
    parser.setMustHaveParameter('Input:Coordinate File')
    parser.setMustHaveParameter('Input:Number of Angles')
    parser.setMustHaveParameter('Input:Number of Atoms')
    parser.setMustHaveParameter('Input:Number of Bonds')
    parser.setMustHaveParameter('Input:Number of Dihedrals')
    parser.setMustHaveParameter('Input:Number of Steps')
    parser.setMustHaveParameter('Input:Structure File')
    parser.setMustHaveParameter('Input:Timestep')

    parser.setMustHaveStatistic('Molecular Dynamics Simulation Performance')
    parser.setMustHaveStatistic('Time Spent in Direct Force Calculation')
    parser.setMustHaveStatistic('Time Spent in Non-Bond List Regeneration')
    parser.setMustHaveStatistic('Time Spent in Reciprocal Force Calculation')
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
    numSteps = 0
    stepSize = 0
    j=0
    while j<len(lines):
       
        m=re.search(r'Amber\s+([0-9a-zA-Z]+)\s+SANDER\s+20[0-9]+',lines[j])
        if m:parser.setParameter("App:Version","SANDER "+m.group(1))
        
        m=re.match(r'^\|\s+PMEMD implementation of SANDER, Release\s+([0-9\.]+)',lines[j])
        if m:parser.setParameter("App:Version","PMEMD "+m.group(1))
       
        m=re.match(r'^\|\s+INPCRD:\s+(\S+)',lines[j])
        if m:parser.setParameter("Input:Coordinate File",m.group(1))
       
        m=re.match(r'^\|\s+PARM:\s+(\S+)',lines[j])
        if m:parser.setParameter("Input:Structure File",m.group(1))
        
        if re.search(r'CONTROL\s+DATA\s+FOR\s+THE\s+RUN',lines[j]):
            j+=2
            for k in range(256):
                if re.match(r'^-----------------------------',lines[j]):break
                
                m=re.search(r'nstlim\s+=\s+([0-9]+)',lines[j])
                if m:
                    numSteps = int(m.group(1).strip())
                    parser.setParameter( "Input:Number of Steps", numSteps )
                
                m=re.search(r'dt\s+=\s+([0-9.]+)',lines[j])
                if m:
                    stepSize = 1000.0 * float(m.group(1).strip())
                    parser.setParameter( "Input:Timestep", stepSize*1e-15, "Second per Step" )
                
                j+=1
       
        if re.search(r'RESOURCE\s+USE',lines[j]):
            j+=2
            numBonds     = 0
            numAngles    = 0
            numDihedrals = 0
            for k in range(256):
                if re.match(r'^-----------------------------',lines[j]):break
             
                m=re.search(r'NATOM\s+=\s+([0-9]+)',lines[j])
                if m:parser.setParameter("Input:Number of Atoms",m.group(1).strip())
             
                m=re.search(r'NBONH\s+=\s+([0-9]+)',lines[j])
                if m:numBonds+=int(m.group(1).strip())
             
                m=re.search(r'NBONA\s+=\s+([0-9]+)',lines[j])
                if m:numBonds+=int(m.group(1).strip())
             
                m=re.search(r'NTHETH\s+=\s+([0-9]+)',lines[j])
                if m:numAngles+=int(m.group(1).strip())
             
                m=re.search(r'NTHETA\s+=\s+([0-9]+)',lines[j])
                if m:numAngles+=int(m.group(1).strip())
             
                m=re.search(r'NPHIH\s+=\s+([0-9]+)',lines[j])
                if m:numDihedrals+=int(m.group(1).strip())
             
                m=re.search(r'NPHIA\s+=\s+([0-9]+)',lines[j])
                if m:numDihedrals+=int(m.group(1).strip())
             
                j+=1
       
            if numBonds>0:parser.setParameter("Input:Number of Bonds",numBonds)
            if numAngles>0:parser.setParameter("Input:Number of Angles",numAngles)
            if numDihedrals>0:parser.setParameter("Input:Number of Dihedrals",numDihedrals)
       
        if re.search(r'PME Nonbond Pairlist CPU Time',lines[j]):
            j+=2
            for k in range(20):
                m=re.search(r'Total\s+([\d\.]+)',lines[j])
                if m:
                    parser.setStatistic("Time Spent in Non-Bond List Regeneration", m.group(1), "Second")
                    break
                j+=1
        if re.search(r'PME Direct Force CPU Time',lines[j]):
            j+=2
            for k in range(20):
                m=re.search(r'Total\s+([\d\.]+)',lines[j])
                if m:
                    parser.setStatistic("Time Spent in Direct Force Calculation", m.group(1), "Second")
                    break
                j+=1
        if re.search(r'PME Reciprocal Force CPU Time',lines[j]):
            j+=2
            for k in range(20):
                m=re.search(r'Total\s+([\d\.]+)',lines[j])
                if m:
                    parser.setStatistic("Time Spent in Reciprocal Force Calculation", m.group(1), "Second")
                    break
                j+=1
        m=re.match(r'^\|\s+Master Total wall time:\s+([0-9.]+)\s+seconds',lines[j])
        if m:
            parser.setStatistic("Wall Clock Time", m.group(1), "Second")
            parser.successfulRun=True
            
            # calculate the performance
            simulationTime = stepSize * numSteps * 0.000001 # measured in nanoseconds
            if simulationTime>0.0:
                parser.setStatistic( "Molecular Dynamics Simulation Performance", 1.e-9*simulationTime / ( float(m.group(1)) / 86400.0 ), "Second per Day" )
            
        j+=1
    
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
    
    

