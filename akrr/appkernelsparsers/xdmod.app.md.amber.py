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
    parser.add_common_must_have_params_and_stats()
    #set app kernel custom sets  
    parser.add_must_have_parameter('App:Version')
    parser.add_must_have_parameter('Input:Coordinate File')
    parser.add_must_have_parameter('Input:Number of Angles')
    parser.add_must_have_parameter('Input:Number of Atoms')
    parser.add_must_have_parameter('Input:Number of Bonds')
    parser.add_must_have_parameter('Input:Number of Dihedrals')
    parser.add_must_have_parameter('Input:Number of Steps')
    parser.add_must_have_parameter('Input:Structure File')
    parser.add_must_have_parameter('Input:Timestep')

    parser.add_must_have_statistic('Molecular Dynamics Simulation Performance')
    parser.add_must_have_statistic('Time Spent in Direct Force Calculation')
    parser.add_must_have_statistic('Time Spent in Non-Bond List Regeneration')
    parser.add_must_have_statistic('Time Spent in Reciprocal Force Calculation')
    parser.add_must_have_statistic('Wall Clock Time')

    
    #parse common parameters and statistics
    parser.parse_common_params_and_stats(appstdout, stdout, stderr, geninfo)
    
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
        if m:parser.set_parameter("App:Version", "SANDER " + m.group(1))
        
        m=re.match(r'^\|\s+PMEMD implementation of SANDER, Release\s+([0-9\.]+)',lines[j])
        if m:parser.set_parameter("App:Version", "PMEMD " + m.group(1))
       
        m=re.match(r'^\|\s+INPCRD:\s+(\S+)',lines[j])
        if m:parser.set_parameter("Input:Coordinate File", m.group(1))
       
        m=re.match(r'^\|\s+PARM:\s+(\S+)',lines[j])
        if m:parser.set_parameter("Input:Structure File", m.group(1))
        
        if re.search(r'CONTROL\s+DATA\s+FOR\s+THE\s+RUN',lines[j]):
            j+=2
            for k in range(256):
                if re.match(r'^-----------------------------',lines[j]):break
                
                m=re.search(r'nstlim\s+=\s+([0-9]+)',lines[j])
                if m:
                    numSteps = int(m.group(1).strip())
                    parser.set_parameter("Input:Number of Steps", numSteps)
                
                m=re.search(r'dt\s+=\s+([0-9.]+)',lines[j])
                if m:
                    stepSize = 1000.0 * float(m.group(1).strip())
                    parser.set_parameter("Input:Timestep", stepSize * 1e-15, "Second per Step")
                
                j+=1
       
        if re.search(r'RESOURCE\s+USE',lines[j]):
            j+=2
            numBonds     = 0
            numAngles    = 0
            numDihedrals = 0
            for k in range(256):
                if re.match(r'^-----------------------------',lines[j]):break
             
                m=re.search(r'NATOM\s+=\s+([0-9]+)',lines[j])
                if m:parser.set_parameter("Input:Number of Atoms", m.group(1).strip())
             
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
       
            if numBonds>0:parser.set_parameter("Input:Number of Bonds", numBonds)
            if numAngles>0:parser.set_parameter("Input:Number of Angles", numAngles)
            if numDihedrals>0:parser.set_parameter("Input:Number of Dihedrals", numDihedrals)
       
        if re.search(r'PME Nonbond Pairlist CPU Time',lines[j]):
            j+=2
            for k in range(20):
                m=re.search(r'Total\s+([\d\.]+)',lines[j])
                if m:
                    parser.set_statistic("Time Spent in Non-Bond List Regeneration", m.group(1), "Second")
                    break
                j+=1
        if re.search(r'PME Direct Force CPU Time',lines[j]):
            j+=2
            for k in range(20):
                m=re.search(r'Total\s+([\d\.]+)',lines[j])
                if m:
                    parser.set_statistic("Time Spent in Direct Force Calculation", m.group(1), "Second")
                    break
                j+=1
        if re.search(r'PME Reciprocal Force CPU Time',lines[j]):
            j+=2
            for k in range(20):
                m=re.search(r'Total\s+([\d\.]+)',lines[j])
                if m:
                    parser.set_statistic("Time Spent in Reciprocal Force Calculation", m.group(1), "Second")
                    break
                j+=1
        m=re.match(r'^\|\s+Master Total wall time:\s+([0-9.]+)\s+seconds',lines[j])
        if m:
            parser.set_statistic("Wall Clock Time", m.group(1), "Second")
            parser.successfulRun=True
            
            # calculate the performance
            simulationTime = stepSize * numSteps * 0.000001 # measured in nanoseconds
            if simulationTime>0.0:
                parser.set_statistic("Molecular Dynamics Simulation Performance", 1.e-9 * simulationTime / (float(m.group(1)) / 86400.0), "Second per Day")
            
        j+=1
    
    if __name__ == "__main__":
        #output for testing purpose
        print("parsing complete:", parser.parsing_complete())
        parser.print_params_stats_as_must_have()
        print(parser.get_xml())
    
    #return complete XML overwize return None
    return parser.get_xml()
    
    
if __name__ == "__main__":
    """stand alone testing"""
    jobdir=sys.argv[1]
    print("Proccessing Output From",jobdir)
    processAppKerOutput(appstdout=os.path.join(jobdir,"appstdout"),geninfo=os.path.join(jobdir,"gen.info"))
    
    

