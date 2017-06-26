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
        name             = 'xdmod.app.md.namd',
        version          = 1,
        description      = "NAMD: Scalable Molecular Dynamics Package",
        url              = 'http://www.ks.uiuc.edu/Research/namd/',
        measurement_name = 'NAMD'
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
    
    parser.setMustHaveStatistic('Memory')
    parser.setMustHaveStatistic('Molecular Dynamics Simulation Performance')
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
    successfulRun=False
    j=0
    while j<len(lines):
       
       m=re.match(r'^Info: NAMD ([0-9a-zA-Z\.]+)',lines[j])
       if m:parser.setParameter("App:Version",m.group(1))
       
       m=re.match(r'^Info: TIMESTEP\s+([0-9\.]+)',lines[j])
       if m:parser.setParameter("Input:Timestep",m.group(1)+"e-15", "Second per Step" )
       
       m=re.match(r'^Info: NUMBER OF STEPS\s+([0-9\.]+)',lines[j])
       if m:parser.setParameter("Input:Number of Steps",m.group(1))
       
       m=re.match(r'^Info: COORDINATE PDB\s+(.+)',lines[j])
       if m:parser.setParameter("Input:Coordinate File",m.group(1))
       
       m=re.match(r'^Info: STRUCTURE FILE\s+(.+)',lines[j])
       if m:parser.setParameter("Input:Structure File",m.group(1))
       
       m=re.match(r'^Info: Running on ([0-9\.]+) processors, ([0-9\.]+) nodes, ([0-9\.]+) physical nodes.',lines[j])
       if m:
           parser.setParameter("App:NCores",m.group(1).strip())
           parser.setParameter("App:NNodes",m.group(3).strip())
       
       if re.match(r'^Info: STRUCTURE SUMMARY',lines[j]):
          j+=1
          for k in range(25):
             if re.match(r'^Info: \*\*\*\*\*',lines[j]):
                break
             
             m=re.match(r'^Info:\s+([0-9]+)\s+ATOMS\n',lines[j])
             if m:parser.setParameter("Input:Number of Atoms",m.group(1))
             
             m=re.match(r'^Info:\s+([0-9]+)\s+BONDS\n',lines[j])
             if m:parser.setParameter("Input:Number of Bonds",m.group(1))
             
             m=re.match(r'^Info:\s+([0-9]+)\s+ANGLES\n',lines[j])
             if m:parser.setParameter("Input:Number of Angles",m.group(1))
             
             m=re.match(r'^Info:\s+([0-9]+)\s+DIHEDRALS\n',lines[j])
             if m:parser.setParameter("Input:Number of Dihedrals",m.group(1))
             
             j+=1
       
       if re.search(r'Info: Benchmark time:',lines[j]):
          m=re.search(r' ([0-9.]+) days/ns',lines[j])      
          if m:parser.setStatistic( "Molecular Dynamics Simulation Performance", str(1.0e-9/float(m.group(1))), "Second per Day" )
       
       m=re.match(r'^WallClock:\s+([0-9\.]+)\s+CPUTime:\s+([0-9\.]+)\s+Memory:\s+([0-9\.]+)',lines[j])
       if m:
          parser.setStatistic("Wall Clock Time", m.group(1), "Second")
          parser.setStatistic("Memory", m.group(3), "MByte")
          successfulRun=True
       
       m=re.match(r'^End of program',lines[j])
       if m:successfulRun=True
       
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
    
    

