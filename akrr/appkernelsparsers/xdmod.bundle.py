# Part of XDMoD=>AKRR
# parser for Intel MPI Benchmarks AK
#
# authors: Nikolay Simakov, Charng-Da Lu
#

import re
import os
import sys
import traceback

#Set proper path for stand alone test runs
if __name__ == "__main__":
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),'../..'))


import akrr
import akrr.cfg
import akrr.appkernelsparsers.akrrappkeroutputparser
from akrr.appkernelsparsers.akrrappkeroutputparser import AppKerOutputParser,total_seconds

#graph500/run input$numCores

def processAppKerOutput(appstdout=None,stdout=None,stderr=None,geninfo=None,appKerNResVars=None):
    #set App Kernel Description
    parser=AppKerOutputParser(
        name             = 'xdmod.bundle',
        version          = 1,
        description      = 'bundled tasks',
        url              = 'https://xdmod.ccr.buffalo.edu',
        measurement_name = 'BUNDLE'
    )
    parser.setMustHaveParameter('RunEnv:Nodes')
    parser.setMustHaveStatistic('Wall Clock Time')
    parser.setMustHaveStatistic("Success Rate")
    parser.setMustHaveStatistic("Successful Subtasks")
    parser.setMustHaveStatistic("Total Number of Subtasks")
    
    #set obligatory parameters and statistics
    #set common parameters and statistics
    
    parser.parseCommonParsAndStats(appstdout,stdout,stderr,geninfo)
    
    if hasattr(parser,'wallClockTime'):
        parser.setStatistic("Wall Clock Time", total_seconds(parser.wallClockTime), "Second")
    
    #check the status of subtasks
    
    #appKerNResVars['taskId']=self.task_id
    #appKerNResVars['subTasksId']=self.subTasksId
    successRate=0.0
    totalSubtasks=0
    successfulSubtasks=0
    try:
        db,cur=akrr.cfg.getExportDB()
        
        for subTaskId in appKerNResVars['subTasksId']:
            cur.execute('''SELECT instance_id,status FROM akrr_xdmod_instanceinfo
                WHERE instance_id=%s ;''',(subTaskId,))
            raw=cur.fetchall()
            instance_id,status=raw[0]
            successRate+=status
            successfulSubtasks+=status
            
        successRate/=len(appKerNResVars['subTasksId'])
        totalSubtasks=len(appKerNResVars['subTasksId'])
        cur.close()
        del db
    except:
        print(traceback.format_exc())
    
    parser.setStatistic("Success Rate", successRate)
    parser.setStatistic("Successful Subtasks", successfulSubtasks)
    parser.setStatistic("Total Number of Subtasks", totalSubtasks)
    #if successfulSubtasks==totalSubtasks:
        
    if __name__ == "__main__":
        #output for testing purpose
        print("parsing complete:",parser.parsingComplete(Verbose=True))
        parser.printParsNStatsAsMustHave()
        print(parser.getXML())
    
    #return complete XML overwize return None
    return parser.getXML()
    
    
if __name__ == "__main__":
    """stand alone testing"""
    jobdir=sys.argv[1]
    print("Proccessing Output From",jobdir)
    processAppKerOutput(appstdout=os.path.join(jobdir,"appstdout"),geninfo=os.path.join(jobdir,"gen.info"))
    
    

