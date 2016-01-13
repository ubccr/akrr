import re
import os
import sys
if __name__ == "__main__":
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),'../'))

import arrappkeroutputparser
from arrappkeroutputparser import AppKerOutputParser

def processAppKerOutput(appstdout=None,nodes=None):
    parser=AppKerOutputParser(
        name             = 'xdmod.app.md.namd',
        version          = 1,
        description      = "NAMD: Scalable Molecular Dynamics Package",
        url              = 'http://www.ks.uiuc.edu/Research/namd/',
        measurement_name = 'NAMD'
    )
    parser.setMustHaveParameter('App:ExeBinSignature')
    parser.setMustHaveParameter('App:Version')
    parser.setMustHaveParameter('Input:Coordinate File')
    parser.setMustHaveParameter('Input:Number of Angles')
    parser.setMustHaveParameter('Input:Number of Atoms')
    parser.setMustHaveParameter('Input:Number of Bonds')
    parser.setMustHaveParameter('Input:Number of Dihedrals')
    parser.setMustHaveParameter('Input:Number of Steps')
    parser.setMustHaveParameter('Input:Structure File')
    parser.setMustHaveParameter('Input:Timestep')
    parser.setMustHaveParameter('RunEnv:Nodes')
    
    parser.setMustHaveStatistic('Memory')
    parser.setMustHaveStatistic('Molecular Dynamics Simulation Performance')
    parser.setMustHaveStatistic('Wall Clock Time')
    
    result=None
    
    nodeslist=""
    if nodes:
        if os.path.isfile(nodes):
            nodeslist=os.popen('cat "%s"|gzip -9|base64 -w 0'%(nodes)).read()
    
    fin=open(appstdout,"rt")
    lines=fin.readlines()
    fin.close()
    
    ExeBinSignature=''
    successfulRun=False
    
    j=0
    while j<len(lines):
       m=re.search(r'===ExeBinSignature===(.+)',lines[j])
       if m:ExeBinSignature+=m.group(1).strip()+'\n'
       
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
    
    
    ExeBinSignature=os.popen('echo "%s"|gzip -9|base64 -w 0'%(ExeBinSignature)).read()
    parser.setParameter("App:ExeBinSignature",ExeBinSignature)
    parser.setParameter("RunEnv:Nodes",nodeslist)
    #$benchmark->setParameter( "RunEnv:Nodes",        $ENV{"INCA_BATCHWRAPPER_NODELIST"} )            if ( exists $ENV{"INCA_BATCHWRAPPER_NODELIST"} );
    #$reporter->setResult(1);
    #$reporter->print();
    
    if __name__ == "__main__":
        print "parsing complete:",parser.parsingComplete()
        print parser.getXML()
    
if __name__ == "__main__":
    jobdir=sys.argv[1]
    print "Proccessing Output From",jobdir
    processAppKerOutput(appstdout=os.path.join(jobdir,"appstdout"),nodes=os.path.join(jobdir,"nodes"))
    
    

