# Part of XDMoD=>AKRR
# parser for Intel MPI Benchmarks AK
#
# authors: Nikolay Simakov, Charng-Da Lu
#

import re
import os
import sys
#import akrr

#Set proper path for stand alone test runs
if __name__ == "__main__":
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),'../..'))

import akrr.appkernelsparsers.akrrappkeroutputparser
from akrr.appkernelsparsers.akrrappkeroutputparser import AppKerOutputParser, total_seconds

#graph500/run input$numCores

def processAppKerOutput(appstdout=None,stdout=None,stderr=None,geninfo=None,appKerNResVars=None):
    #set App Kernel Description
    parser=AppKerOutputParser(
        name             = 'xdmod.benchmark.hpcc',
        version          = 1,
        description      = "HPC Challenge Benchmarks",
        url              = 'http://icl.cs.utk.edu/hpcc/',
        measurement_name = 'xdmod.benchmark.hpcc'
    )
    #set obligatory parameters and statistics
    #set common parameters and statistics
    parser.add_common_must_have_params_and_stats()
    #set app kernel custom sets  
    parser.add_must_have_parameter('App:Version')
    parser.add_must_have_parameter('Input:DGEMM Problem Size')
    parser.add_must_have_parameter('Input:High Performance LINPACK Grid Cols')
    parser.add_must_have_parameter('Input:High Performance LINPACK Grid Rows')
    parser.add_must_have_parameter('Input:High Performance LINPACK Problem Size')
    parser.add_must_have_parameter('Input:MPI Ranks')
    parser.add_must_have_parameter('Input:MPIRandom Problem Size')
    parser.add_must_have_parameter('Input:OpenMP Threads')
    parser.add_must_have_parameter('Input:PTRANS Problem Size')
    parser.add_must_have_parameter('Input:STREAM Array Size')
    parser.add_must_have_parameter('RunEnv:CPU Speed')
    parser.add_must_have_parameter('RunEnv:Nodes')
    
    parser.add_must_have_statistic('Average Double-Precision General Matrix Multiplication (DGEMM) Floating-Point Performance')
    parser.add_must_have_statistic("Average STREAM 'Add' Memory Bandwidth")
    parser.add_must_have_statistic("Average STREAM 'Copy' Memory Bandwidth")
    parser.add_must_have_statistic("Average STREAM 'Scale' Memory Bandwidth")
    parser.add_must_have_statistic("Average STREAM 'Triad' Memory Bandwidth")
    parser.add_must_have_statistic('Fast Fourier Transform (FFTW) Floating-Point Performance')
    parser.add_must_have_statistic('High Performance LINPACK Efficiency')
    parser.add_must_have_statistic('High Performance LINPACK Floating-Point Performance')
    parser.add_must_have_statistic('High Performance LINPACK Run Time')
    parser.add_must_have_statistic('MPI Random Access')
    parser.add_must_have_statistic('Parallel Matrix Transpose (PTRANS)')
    parser.add_must_have_statistic('Wall Clock Time')
    #parse common parameters and statistics
    parser.parse_common_params_and_stats(appstdout, stdout, stderr, geninfo)
    
    if hasattr(parser,'appKerWallClockTime'):
        parser.set_statistic("Wall Clock Time", total_seconds(parser.appKerWallClockTime), "Second")
    
    # Intel MPI benchmark suite contains three classes of benchmarks:
    #
    #  Single-transfer, which needs only 2 processes
    #  Parallel-transfer, which can use as many processes that are available
    #  Collective, which can use as many processes that are available
    
    # The parameters mapping table
    Params = {
    "CommWorldProcs"      : [ "MPI Ranks",                             "",      "" ],
    "HPL_N"               : [ "High Performance LINPACK Problem Size", "",      "" ],
    "HPL_nprow"           : [ "High Performance LINPACK Grid Rows",    "",      "" ],
    "HPL_npcol"           : [ "High Performance LINPACK Grid Cols",    "",      "" ],
    "PTRANS_n"            : [ "PTRANS Problem Size",                   "",      "" ],
    "MPIRandomAccess_N"   : [ "MPIRandom Problem Size",                "MWord", "val/1024/1024" ],
    "STREAM_VectorSize"   : [ "STREAM Array Size",                     "MWord", "" ],
    "DGEMM_N"             : [ "DGEMM Problem Size",                    "",      "" ],
    "omp_get_num_threads" : [ "OpenMP Threads",                        "",      "" ],
    }
    
    # The result mapping table
    Metrics = {
    "HPL_Tflops"           : [ "High Performance LINPACK Floating-Point Performance",
                               "MFLOP per Second",   "val*1e6" ],
    "HPL_time"             : [ "High Performance LINPACK Run Time",
                               "Second",             "" ],
    "PTRANS_GBs"           : [ "Parallel Matrix Transpose (PTRANS)",
                               "MByte per Second",   "val*1024" ],
    "MPIRandomAccess_GUPs" : [ "MPI Random Access",
                               "MUpdate per Second", "val*1000" ],
    "MPIFFT_Gflops"        : [ "Fast Fourier Transform (FFTW) Floating-Point Performance",
                               "MFLOP per Second",   "val*1000" ],
    "StarDGEMM_Gflops"     : [ "Average Double-Precision General Matrix Multiplication (DGEMM) Floating-Point Performance",
                               "MFLOP per Second",   "val*1000" ],
    "StarSTREAM_Copy"      : [ "Average STREAM 'Copy' Memory Bandwidth",
                               "MByte per Second",   "val*1024" ],
    "StarSTREAM_Scale"     : [ "Average STREAM 'Scale' Memory Bandwidth",
                               "MByte per Second",   "val*1024" ],
    "StarSTREAM_Add"       : [ "Average STREAM 'Add' Memory Bandwidth",
                               "MByte per Second",   "val*1024" ],
    "StarSTREAM_Triad"     : [ "Average STREAM 'Triad' Memory Bandwidth",
                               "MByte per Second",   "val*1024" ]
    }
    
    #read output
    lines=[]
    if os.path.isfile(appstdout):
        fin=open(appstdout,"rt")
        lines=fin.readlines()
        fin.close()
    
    #process the output
    parser.successfulRun=False
    resultBegin=None
    hpl_tflops=None
    numCores=None
    
    values={}
    j=-1
    while j<len(lines)-1:
        j+=1
        m=re.search(r'End of HPC Challenge tests',lines[j])
        if m:parser.successfulRun=True
       
        m=re.match(r'^Begin of Summary section',lines[j])
        if m:
            resultBegin=1
            continue
        
        m=re.match(r'^(\w+)=([\w\.]+)',lines[j])
        if m and resultBegin:
            metricName=m.group(1).strip()
            values[metricName] = m.group(2).strip()
            if metricName=="HPL_Tflops":hpl_tflops = float(values[metricName])
            if metricName=="CommWorldProcs":numCores = int(values[metricName])
        m=re.match(r'^Running on ([0-9\.]+) processors',lines[j])
        if m:
            numCores = int(m.group(1).strip())
    if hpl_tflops==None or  numCores==None:
        parser.successfulRun=False
    
    hpccVersion=None
    MHz=None
    theoreticalGFlops=None
    
    if "VersionMajor" in values and "VersionMinor" in values and "VersionMicro" in values:
        hpccVersion=values["VersionMajor"]+"."+values["VersionMinor"]+"."+values["VersionMicro"]
    if "VersionRelease" in values:
        hpccVersion+=values["VersionRelease"]
    if hpccVersion:
        parser.set_parameter("App:Version", hpccVersion)
    
    for k,v in Params.items():
        if not k in values:
            continue
        val=values[k]
        if v[2].find('val')>=0:
            val=float(val)
            val=eval(v[2])
        if v[1]=="":
            v[1]=None
        parser.set_parameter("Input:" + v[0], val, v[1])
    
    for k,v in Metrics.items():
        if not k in values:
            continue
        val=values[k]
        if v[2].find('val')>=0:
            val=float(val)
            val=eval(v[2])
        if v[1]=="":
            v[1]=None
        parser.set_statistic(v[0], val, v[1])
    
    if "cpuSpeed" in parser.geninfo:
        ll=parser.geninfo["cpuSpeed"].splitlines()
        cpuSpeedMax=0.0
        for l in ll:
            m=re.search(r'([\d\.]+)$',l)
            if m:
                v=float(m.group(1).strip())
                if v>cpuSpeedMax:cpuSpeedMax=v
        if cpuSpeedMax>0.0:
            parser.set_parameter("RunEnv:CPU Speed", cpuSpeedMax, "MHz")
            MHz=cpuSpeedMax
    #print appKerNResVars
    #print MHz
    #print numCores
    
    if appKerNResVars !=None:
        if 'resource' in appKerNResVars and 'app' in appKerNResVars:
            if 'theoreticalGFlopsPerCore' in appKerNResVars['app']:
                resname=appKerNResVars['resource']['name']
                if resname in appKerNResVars['app']['theoreticalGFlopsPerCore']:
                    theoreticalGFlops=appKerNResVars['app']['theoreticalGFlopsPerCore'][resname] * numCores
                    print("theoreticalGFlops",resname,theoreticalGFlops)
    
    if theoreticalGFlops==None and MHz!=None:        
            # Most modern x86 & POWER processors are superscale and can issue 4 instructions per cycle
            theoreticalGFlops = MHz * numCores * 4 / 1000.0
    if theoreticalGFlops and hpl_tflops:
            # Convert both to GFlops and derive the Efficiency
            percent = ( 1000.0 * hpl_tflops / theoreticalGFlops ) * 100.0;
            parser.set_statistic("High Performance LINPACK Efficiency", "%.3f" % percent, "Percent")
            
    
           
    
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
    
    

