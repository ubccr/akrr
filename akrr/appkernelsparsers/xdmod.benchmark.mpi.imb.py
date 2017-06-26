# Part of XDMoD=>AKRR
# parser for Intel MPI Benchmarks AK
#
# authors: Nikolay Simakov, Charng-Da Lu
#

import re
import os
import sys

#Set proper path for stand alone test runs
if __name__ == "__main__":
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),'../../src'))

import akrrappkeroutputparser
from akrrappkeroutputparser import AppKerOutputParser,total_seconds

#graph500/run input$numCores

def processAppKerOutput(appstdout=None,stdout=None,stderr=None,geninfo=None,appKerNResVars=None):
    #set App Kernel Description
    parser=AppKerOutputParser(
        name             = 'xdmod.benchmark.mpi.imb',
        version          = 1,
        description      = "Intel MPI Benchmarks",
        url              = 'http://www.intel.com/software/imb',
        measurement_name = 'Intel MPI Benchmarks'
    )
    #set obligatory parameters and statistics
    #set common parameters and statistics
    parser.setCommonMustHaveParsAndStats()
    #set app kernel custom sets  
    parser.setMustHaveParameter('App:MPI Thread Environment')
    parser.setMustHaveParameter('App:MPI Version')
    parser.setMustHaveParameter('App:Max Message Size')
    
    parser.setMustHaveStatistic('Max Exchange Bandwidth')
    parser.setMustHaveStatistic("Max MPI-2 Bidirectional 'Get' Bandwidth (aggregate)")
    parser.setMustHaveStatistic("Max MPI-2 Bidirectional 'Get' Bandwidth (non-aggregate)")
    parser.setMustHaveStatistic("Max MPI-2 Bidirectional 'Put' Bandwidth (aggregate)")
    parser.setMustHaveStatistic("Max MPI-2 Bidirectional 'Put' Bandwidth (non-aggregate)")
    parser.setMustHaveStatistic("Max MPI-2 Unidirectional 'Get' Bandwidth (aggregate)")
    parser.setMustHaveStatistic("Max MPI-2 Unidirectional 'Get' Bandwidth (non-aggregate)")
    parser.setMustHaveStatistic("Max MPI-2 Unidirectional 'Put' Bandwidth (aggregate)")
    parser.setMustHaveStatistic("Max MPI-2 Unidirectional 'Put' Bandwidth (non-aggregate)")
    parser.setMustHaveStatistic('Max PingPing Bandwidth')
    parser.setMustHaveStatistic('Max PingPong Bandwidth')
    parser.setMustHaveStatistic('Max SendRecv Bandwidth')
    parser.setMustHaveStatistic('Min AllGather Latency')
    parser.setMustHaveStatistic('Min AllGatherV Latency')
    parser.setMustHaveStatistic('Min AllReduce Latency')
    parser.setMustHaveStatistic('Min AllToAll Latency')
    parser.setMustHaveStatistic('Min AllToAllV Latency')
    parser.setMustHaveStatistic('Min Barrier Latency')
    parser.setMustHaveStatistic('Min Broadcast Latency')
    parser.setMustHaveStatistic('Min Gather Latency')
    parser.setMustHaveStatistic('Min GatherV Latency')
    #parser.setMustHaveStatistic("Min MPI-2 'Accumulate' Latency (aggregate)")
    #parser.setMustHaveStatistic("Min MPI-2 'Accumulate' Latency (non-aggregate)")
    parser.setMustHaveStatistic('Min MPI-2 Window Creation Latency')
    parser.setMustHaveStatistic('Min Reduce Latency')
    parser.setMustHaveStatistic('Min ReduceScatter Latency')
    parser.setMustHaveStatistic('Min Scatter Latency')
    parser.setMustHaveStatistic('Min ScatterV Latency')
    parser.setMustHaveStatistic('Wall Clock Time')

    
    #parse common parameters and statistics
    parser.parseCommonParsAndStats(appstdout,stdout,stderr,geninfo)
    
    if hasattr(parser,'appKerWallClockTime'):
        parser.setStatistic("Wall Clock Time", total_seconds(parser.appKerWallClockTime), "Second")
    
    # Intel MPI benchmark suite contains three classes of benchmarks:
    #
    #  Single-transfer, which needs only 2 processes
    #  Parallel-transfer, which can use as many processes that are available
    #  Collective, which can use as many processes that are available
    
    # The parameters mapping table
    Params = {
        "MPI Thread Environment"          : [ "MPI Thread Environment", "",      "" ],
        "MPI Version"                     : [ "MPI Version",            "",      "" ],
        "Maximum message length in bytes" : [ "Max Message Size",       "MByte", "<val>/1024/1024" ]
    }
    
    # The result mapping table
    Metrics = {
        "PingPing"         : [ "PingPing Bandwidth",                   "MByte per Second", "max" ],
        "PingPong"         : [ "PingPong Bandwidth",                   "MByte per Second", "max" ],
        "Multi-PingPing"   : [ "PingPing Bandwidth",                   "MByte per Second", "max" ],
        "Multi-PingPong"   : [ "PingPong Bandwidth",                   "MByte per Second", "max" ],
        "Sendrecv"         : [ "SendRecv Bandwidth",                   "MByte per Second", "max" ],
        "Exchange"         : [ "Exchange Bandwidth",                   "MByte per Second", "max" ],
        "Allreduce"        : [ "AllReduce Latency",                    "us",               "min" ],
        "Reduce"           : [ "Reduce Latency",                       "us",               "min" ],
        "Reduce_scatter"   : [ "ReduceScatter Latency",                "us",               "min" ],
        "Allgather"        : [ "AllGather Latency",                    "us",               "min" ],
        "Allgatherv"       : [ "AllGatherV Latency",                   "us",               "min" ],
        "Gather"           : [ "Gather Latency",                       "us",               "min" ],
        "Gatherv"          : [ "GatherV Latency",                      "us",               "min" ],
        "Scatter"          : [ "Scatter Latency",                      "us",               "min" ],
        "Scatterv"         : [ "ScatterV Latency",                     "us",               "min" ],
        "Alltoall"         : [ "AllToAll Latency",                     "us",               "min" ],
        "Alltoallv"        : [ "AllToAllV Latency",                    "us",               "min" ],
        "Bcast"            : [ "Broadcast Latency",                    "us",               "min" ],
        "Barrier"          : [ "Barrier Latency",                      "us",               "min" ],
        "Window"           : [ "MPI-2 Window Creation Latency",        "us",               "min" ],
        "Multi-Unidir_Get" : [ "MPI-2 Unidirectional 'Get' Bandwidth", "MByte per Second", "max" ],
        "Multi-Unidir_Put" : [ "MPI-2 Unidirectional 'Put' Bandwidth", "MByte per Second", "max" ],
        "Multi-Bidir_Get"  : [ "MPI-2 Bidirectional 'Get' Bandwidth",  "MByte per Second", "max" ],
        "Multi-Bidir_Put"  : [ "MPI-2 Bidirectional 'Put' Bandwidth",  "MByte per Second", "max" ],
        "Unidir_Get"       : [ "MPI-2 Unidirectional 'Get' Bandwidth", "MByte per Second", "max" ],
        "Unidir_Put"       : [ "MPI-2 Unidirectional 'Put' Bandwidth", "MByte per Second", "max" ],
        "Bidir_Get"        : [ "MPI-2 Bidirectional 'Get' Bandwidth",  "MByte per Second", "max" ],
        "Bidir_Put"        : [ "MPI-2 Bidirectional 'Put' Bandwidth",  "MByte per Second", "max" ],
        "Accumulate"       : [ "MPI-2 'Accumulate' Latency",           "us",               "min" ]
    }
    
    #read output
    lines=[]
    if os.path.isfile(appstdout):
        fin=open(appstdout,"rt")
        lines=fin.readlines()
        fin.close()
    
    #process the output
    parser.successfulRun=False
    aggregateMode=None
    metric=None
    j=-1
    while j<len(lines)-1:
        j+=1
        m=re.search(r'All processes entering MPI_Finalize',lines[j])
        if m:parser.successfulRun=True
       
        m=re.match(r'^# Benchmarking\s+(\S+)',lines[j])
        if m:
            if m.group(1) in Metrics:
                metric=m.group(1)
                continue
        
        m=re.match(r'^#\s+MODE:\s+(\S+)',lines[j])
        if m and metric and aggregateMode==None:
            aggregateMode=m.group(1)
            continue
        
        m=re.match(r'^# (.+): (.+)',lines[j])
        if m:# benchmark parameters
            param=m.group(1).strip()
            if param in Params:
                val=m.group(2).strip()
                v=Params[param][2]
                if v.find('<val>')>=0:
                    val=float(val)
                    val=eval(v.replace('<val>','val'))
                parser.setParameter( "App:" + Params[param][0], str(val) + " ", Params[param][1] )
            continue
        
        m=re.match(r'^\s+([1-9]\d*)\s+\d+',lines[j])
        if m and metric:# this effectively skips the first line of result, which has #bytes = 0
            results=[]
            
            while m:
                numbers=lines[j].split()
                results.append(float(numbers[-1]))# tokenize the line, and extract the last column
                
                j+=1
                if j<len(lines):
                    m=re.match(r'^\s+([1-9]\d*)\s+\d+',lines[j])
                    if lines[j].count('IMB_init_buffers_iter')>0:
                        break
                else:
                    break
            metricName=Metrics[metric][0]
            if aggregateMode:
                metricName+=" ("+aggregateMode.lower()+ ")"
            if len(results)>0:
                if Metrics[metric][1]=='us':
                    statname=Metrics[metric][2][0].upper()+Metrics[metric][2][1:]+" "+metricName
                    statval=eval(Metrics[metric][2]+"(results)")
                    parser.setStatistic(statname,statval*1e-6, "Second" )
                else:
                    statname=Metrics[metric][2][0].upper()+Metrics[metric][2][1:]+" "+metricName
                    statval=eval(Metrics[metric][2]+"(results)")
                    parser.setStatistic(statname,statval, Metrics[metric][1])
            
            aggregateMode=None
            metric=None
    if parser.getParameter("App:MPI Thread Environment")==None:
        parser.setParameter("App:MPI Thread Environment","")
           
    
    if __name__ == "__main__":
        #output for testing purpose
        print "parsing complete:",parser.parsingComplete(Verbose=True)
        parser.printParsNStatsAsMustHave()
        print parser.getXML()
    #Print out missing parameters for debug purpose
    parser.parsingComplete(Verbose=True)
    #return complete XML overwize return None
    return parser.getXML()
    
    
if __name__ == "__main__":
    """stand alone testing"""
    jobdir=sys.argv[1]
    print "Proccessing Output From",jobdir
    processAppKerOutput(appstdout=os.path.join(jobdir,"appstdout"),geninfo=os.path.join(jobdir,"gen.info"))
    
    

