# Part of XDMoD=>AKRR
# parser for Intel MPI Benchmarks AK
#
# authors: Nikolay Simakov, Charng-Da Lu
#

import os
import sys
import traceback

import akrr
import akrr.db
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
    parser.add_must_have_parameter('RunEnv:Nodes')
    parser.add_must_have_statistic('Wall Clock Time')
    parser.add_must_have_statistic("Success Rate")
    parser.add_must_have_statistic("Successful Subtasks")
    parser.add_must_have_statistic("Total Number of Subtasks")
    
    #set obligatory parameters and statistics
    #set common parameters and statistics
    
    parser.parse_common_params_and_stats(appstdout, stdout, stderr, geninfo)
    
    if hasattr(parser,'wallClockTime'):
        parser.set_statistic("Wall Clock Time", total_seconds(parser.wallClockTime), "Second")
    
    #check the status of subtasks
    
    #appKerNResVars['taskId']=self.task_id
    #appKerNResVars['subTasksId']=self.subTasksId
    successRate=0.0
    totalSubtasks=0
    successfulSubtasks=0
    try:
        db,cur= akrr.db.get_akrr_db()
        
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
    
    parser.set_statistic("Success Rate", successRate)
    parser.set_statistic("Successful Subtasks", successfulSubtasks)
    parser.set_statistic("Total Number of Subtasks", totalSubtasks)
    #if successfulSubtasks==totalSubtasks:
        
    if __name__ == "__main__":
        #output for testing purpose
        print("parsing complete:", parser.parsing_complete(verbose=True))
        parser.print_params_stats_as_must_have()
        print(parser.get_xml())
    
    #return complete XML overwize return None
    return parser.get_xml()
    
    
if __name__ == "__main__":
    """stand alone testing"""
    jobdir=sys.argv[1]
    print("Proccessing Output From",jobdir)
    processAppKerOutput(appstdout=os.path.join(jobdir,"appstdout"),geninfo=os.path.join(jobdir,"gen.info"))
    
    

