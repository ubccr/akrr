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
    #initiate parser
    parser=AppKerOutputParser(
        name             = 'xdmod.benchmark.io.mdtest'
    )
    #set obligatory parameters and statistics
    #set common parameters and statistics (App:ExeBinSignature and RunEnv:Nodes)
    parser.add_common_must_have_params_and_stats()
    #set app kernel custom sets
    parser.add_must_have_parameter('RunEnv:Nodes')

    parser.add_must_have_parameter('Arguments (single directory per process)')
    parser.add_must_have_parameter('Arguments (single directory)')
    parser.add_must_have_parameter('Arguments (single tree directory per process)')
    parser.add_must_have_parameter('Arguments (single tree directory)')
    parser.add_must_have_parameter('files/directories (single directory per process)')
    parser.add_must_have_parameter('files/directories (single directory)')
    parser.add_must_have_parameter('files/directories (single tree directory per process)')
    parser.add_must_have_parameter('files/directories (single tree directory)')
    parser.add_must_have_parameter('tasks (single directory per process)')
    parser.add_must_have_parameter('tasks (single directory)')
    parser.add_must_have_parameter('tasks (single tree directory per process)')
    parser.add_must_have_parameter('tasks (single tree directory)')

    parser.add_must_have_statistic('Directory creation (single directory per process)')
    parser.add_must_have_statistic('Directory creation (single directory)')
    parser.add_must_have_statistic('Directory creation (single tree directory per process)')
    parser.add_must_have_statistic('Directory creation (single tree directory)')
    parser.add_must_have_statistic('Directory removal (single directory per process)')
    parser.add_must_have_statistic('Directory removal (single directory)')
    parser.add_must_have_statistic('Directory removal (single tree directory per process)')
    parser.add_must_have_statistic('Directory removal (single tree directory)')
    parser.add_must_have_statistic('Directory stat (single directory per process)')
    parser.add_must_have_statistic('Directory stat (single directory)')
    parser.add_must_have_statistic('Directory stat (single tree directory per process)')
    parser.add_must_have_statistic('Directory stat (single tree directory)')
    parser.add_must_have_statistic('File creation (single directory per process)')
    parser.add_must_have_statistic('File creation (single directory)')
    parser.add_must_have_statistic('File creation (single tree directory per process)')
    parser.add_must_have_statistic('File creation (single tree directory)')
    parser.add_must_have_statistic('File read (single directory per process)')
    parser.add_must_have_statistic('File read (single directory)')
    parser.add_must_have_statistic('File read (single tree directory per process)')
    parser.add_must_have_statistic('File read (single tree directory)')
    parser.add_must_have_statistic('File removal (single directory per process)')
    parser.add_must_have_statistic('File removal (single directory)')
    parser.add_must_have_statistic('File removal (single tree directory per process)')
    parser.add_must_have_statistic('File removal (single tree directory)')
    parser.add_must_have_statistic('File stat (single directory per process)')
    parser.add_must_have_statistic('File stat (single directory)')
    parser.add_must_have_statistic('File stat (single tree directory per process)')
    parser.add_must_have_statistic('File stat (single tree directory)')
    parser.add_must_have_statistic('Tree creation (single directory per process)')
    parser.add_must_have_statistic('Tree creation (single directory)')
    parser.add_must_have_statistic('Tree creation (single tree directory per process)')
    parser.add_must_have_statistic('Tree creation (single tree directory)')
    parser.add_must_have_statistic('Tree removal (single directory per process)')
    parser.add_must_have_statistic('Tree removal (single directory)')
    parser.add_must_have_statistic('Tree removal (single tree directory per process)')
    parser.add_must_have_statistic('Tree removal (single tree directory)')

    parser.add_must_have_statistic('Wall Clock Time')

    #parse common parameters and statistics
    parser.parse_common_params_and_stats(appstdout, stdout, stderr, geninfo)

    if hasattr(parser,'appKerWallClockTime'):
        parser.set_statistic("Wall Clock Time", total_seconds(parser.appKerWallClockTime), "Second")
    
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
                    parser.set_statistic(m.group(1).strip() + testname, m.group(2), "Operations/Second")
                else:
                    break
                j=j+1
         m=re.search(r'finished at',lines[j])
         if m:parser.successfulRun=True
         m=re.match(r'^Command line used:.+mdtest\s+(.+)',lines[j])
         
         if m:
             parser.set_parameter("Arguments" + testname, m.group(1).strip())
         m=re.search(r'([0-9]+) tasks, ([0-9]+) files/directories',lines[j])
         if m:
             parser.set_parameter("tasks" + testname, m.group(1).strip())
             parser.set_parameter("files/directories" + testname, m.group(2).strip())
         j=j+1

         #parser.set_parameter("mega parameter",m.group(1))
#         
#         m=re.search(r'My mega parameter\s+(\d+)',lines[j])
#         if m:parser.set_statistic("mega statistics",m.group(1),"Seconds")
#
#         m=re.search(r'Done',lines[j])
#         if m:parser.successfulRun=True
#         
#         j+=1
        
    
    if __name__ == "__main__":
        #output for testing purpose
        print("Parsing complete:", parser.parsing_complete(verbose=True))
        print("Following statistics and parameter can be set as obligatory:")
        parser.print_params_stats_as_must_have()
        print("\nResulting XML:")
        print(parser.get_xml())
    
    #return complete XML otherwise return None
    return parser.get_xml()
    
    
if __name__ == "__main__":
    """stand alone testing"""
    jobdir=sys.argv[1]
    print("Proccessing Output From",jobdir)
    testParser(jobdir,processAppKerOutput)

    
    

