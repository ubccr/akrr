# Generic Parser
import re
import os
import sys

#Set proper path for stand alone test runs
if __name__ == "__main__":
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),'../..'))

from akrr.appkernelsparsers.akrrappkeroutputparser import AppKerOutputParser,testParser,total_seconds


def processAppKerOutput(appstdout=None,stdout=None,stderr=None,geninfo=None,appKerNResVars=None):
    #set App Kernel Description
    if(appKerNResVars!=None and 'app' in appKerNResVars and 'name' in appKerNResVars['app']):
        akname=appKerNResVars['app']['name']
    else:
        akname='unknown'
   
    #initiate parser
    parser=AppKerOutputParser(
        name             = akname
    )
    #set obligatory parameters and statistics
    #set common parameters and statistics (App:ExeBinSignature and RunEnv:Nodes)
    parser.add_common_must_have_params_and_stats()
    #set app kernel custom sets
    #parser.add_must_have_parameter('App:Version')
    
    parser.add_must_have_statistic('Wall Clock Time')
    #parse common parameters and statistics
    parser.parse_common_params_and_stats(appstdout, stdout, stderr, geninfo)

    if hasattr(parser,'appKerWallClockTime'):
        parser.set_statistic("Wall Clock Time", total_seconds(parser.appKerWallClockTime), "Second")
    
    #Here can be custom output parsing
#     #read output
#     lines=[]
#     if os.path.isfile(appstdout):
#         fin=open(appstdout,"rt")
#         lines=fin.readlines()
#         fin.close()
#     
#     #process the output
#     parser.successfulRun=False
#     j=0
#     while j<len(lines):
#         m=re.search(r'My mega parameter\s+(\d+)',lines[j])
#         if m:parser.set_parameter("mega parameter",m.group(1))
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

    
    

