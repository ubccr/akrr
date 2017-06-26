# Generic Parser
import re
import os
import sys

#Set proper path for stand alone test runs
if __name__ == "__main__":
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),'../../src'))

from akrrappkeroutputparser import AppKerOutputParser,testParser,total_seconds


def processAppKerOutput(appstdout=None,stdout=None,stderr=None,geninfo=None,appKerNResVars=None):
    #initiate parser
    parser=AppKerOutputParser(
        name             = 'xdmod.benchmark.io.mdtest'
    )
    #set obligatory parameters and statistics
    #set common parameters and statistics (App:ExeBinSignature and RunEnv:Nodes)
    parser.setCommonMustHaveParsAndStats()
    #set app kernel custom sets
    parser.setMustHaveParameter('RunEnv:Nodes')

    parser.setMustHaveParameter('Arguments (single directory per process)')
    parser.setMustHaveParameter('Arguments (single directory)')
    parser.setMustHaveParameter('Arguments (single tree directory per process)')
    parser.setMustHaveParameter('Arguments (single tree directory)')
    parser.setMustHaveParameter('files/directories (single directory per process)')
    parser.setMustHaveParameter('files/directories (single directory)')
    parser.setMustHaveParameter('files/directories (single tree directory per process)')
    parser.setMustHaveParameter('files/directories (single tree directory)')
    parser.setMustHaveParameter('tasks (single directory per process)')
    parser.setMustHaveParameter('tasks (single directory)')
    parser.setMustHaveParameter('tasks (single tree directory per process)')
    parser.setMustHaveParameter('tasks (single tree directory)')

    parser.setMustHaveStatistic('Directory creation (single directory per process)')
    parser.setMustHaveStatistic('Directory creation (single directory)')
    parser.setMustHaveStatistic('Directory creation (single tree directory per process)')
    parser.setMustHaveStatistic('Directory creation (single tree directory)')
    parser.setMustHaveStatistic('Directory removal (single directory per process)')
    parser.setMustHaveStatistic('Directory removal (single directory)')
    parser.setMustHaveStatistic('Directory removal (single tree directory per process)')
    parser.setMustHaveStatistic('Directory removal (single tree directory)')
    parser.setMustHaveStatistic('Directory stat (single directory per process)')
    parser.setMustHaveStatistic('Directory stat (single directory)')
    parser.setMustHaveStatistic('Directory stat (single tree directory per process)')
    parser.setMustHaveStatistic('Directory stat (single tree directory)')
    parser.setMustHaveStatistic('File creation (single directory per process)')
    parser.setMustHaveStatistic('File creation (single directory)')
    parser.setMustHaveStatistic('File creation (single tree directory per process)')
    parser.setMustHaveStatistic('File creation (single tree directory)')
    parser.setMustHaveStatistic('File read (single directory per process)')
    parser.setMustHaveStatistic('File read (single directory)')
    parser.setMustHaveStatistic('File read (single tree directory per process)')
    parser.setMustHaveStatistic('File read (single tree directory)')
    parser.setMustHaveStatistic('File removal (single directory per process)')
    parser.setMustHaveStatistic('File removal (single directory)')
    parser.setMustHaveStatistic('File removal (single tree directory per process)')
    parser.setMustHaveStatistic('File removal (single tree directory)')
    parser.setMustHaveStatistic('File stat (single directory per process)')
    parser.setMustHaveStatistic('File stat (single directory)')
    parser.setMustHaveStatistic('File stat (single tree directory per process)')
    parser.setMustHaveStatistic('File stat (single tree directory)')
    parser.setMustHaveStatistic('Tree creation (single directory per process)')
    parser.setMustHaveStatistic('Tree creation (single directory)')
    parser.setMustHaveStatistic('Tree creation (single tree directory per process)')
    parser.setMustHaveStatistic('Tree creation (single tree directory)')
    parser.setMustHaveStatistic('Tree removal (single directory per process)')
    parser.setMustHaveStatistic('Tree removal (single directory)')
    parser.setMustHaveStatistic('Tree removal (single tree directory per process)')
    parser.setMustHaveStatistic('Tree removal (single tree directory)')

    parser.setMustHaveStatistic('Wall Clock Time')

    #parse common parameters and statistics
    parser.parseCommonParsAndStats(appstdout,stdout,stderr,geninfo)

    if hasattr(parser,'appKerWallClockTime'):
        parser.setStatistic("Wall Clock Time", total_seconds(parser.appKerWallClockTime), "Second")
    
    #Here can be custom output parsing
    #read output
    lines=[]
    if os.path.isfile(appstdout):
        fin=open(appstdout,"rt")
        lines=fin.readlines()
        fin.close()
     
    #process the output
    testname=""
    parser.successfulRun=False
    j=0
    while j<len(lines):
         m=re.match(r'^#Testing (.+)',lines[j])
         if m:
             testname=" ("+m.group(1).strip()+")"
         m=re.match(r'^SUMMARY:',lines[j])
         if m:
             j=j+3
             while j<len(lines):
                m=re.match(r'([A-Za-z0-9 ]+):\s+[0-9.]+\s+[0-9.]+\s+([0-9.]+)\s+([0-9.]+)',lines[j])
                if m:
                    parser.setStatistic(m.group(1).strip()+testname,m.group(2),"Operations/Second")
                else:
                    break
                j=j+1
         m=re.search(r'finished at',lines[j])
         if m:parser.successfulRun=True
         m=re.match(r'^Command line used:.+mdtest\s+(.+)',lines[j])
         
         if m:
             parser.setParameter("Arguments"+testname,m.group(1).strip())
         m=re.search(r'([0-9]+) tasks, ([0-9]+) files/directories',lines[j])
         if m:
             parser.setParameter("tasks"+testname,m.group(1).strip())
             parser.setParameter("files/directories"+testname,m.group(2).strip())
         j=j+1

         #parser.setParameter("mega parameter",m.group(1))
#         
#         m=re.search(r'My mega parameter\s+(\d+)',lines[j])
#         if m:parser.setStatistic("mega statistics",m.group(1),"Seconds")
#
#         m=re.search(r'Done',lines[j])
#         if m:parser.successfulRun=True
#         
#         j+=1
        
    
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

    
    

