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
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),'../..'))

import akrr.appkernelsparsers.akrrappkeroutputparser
from akrr.appkernelsparsers.akrrappkeroutputparser import AppKerOutputParser,total_seconds

#graph500/run input$numCores

def getMiB(val,units):
    if units=="MiB":
        return val
    if units=="KiB":
        return val/1024.0
    if units=="GiB":
        return val*1024

def processAppKerOutput(appstdout=None,stdout=None,stderr=None,geninfo=None,appKerNResVars=None):
    #set App Kernel Description
    parser=AppKerOutputParser(
        name             = 'xdmod.benchmark.io.ior',
        version          = 1,
        description      = "IOR (Interleaved-Or-Random) Benchmark",
        url              = 'http://freshmeat.net/projects/ior',
        measurement_name = 'IOR'
    )
    #set obligatory parameters and statistics
    #set common parameters and statistics
    parser.setCommonMustHaveParsAndStats()
    #set app kernel custom sets  
    parser.setMustHaveParameter('App:Version')
    if appKerNResVars==None or (appKerNResVars!=None and 'testHDF5' in appKerNResVars and appKerNResVars['testHDF5']==True):
        parser.setMustHaveParameter('HDF Version')
        parser.setMustHaveParameter('HDF5 Collective N-to-1 Test File System')
        parser.setMustHaveParameter('HDF5 Independent N-to-1 Test File System')
        parser.setMustHaveParameter('HDF5 N-to-N Test File System')
    if appKerNResVars==None or (appKerNResVars!=None and 'testMPIIO' in appKerNResVars and appKerNResVars['testMPIIO']==True):
        parser.setMustHaveParameter('MPIIO Collective N-to-1 Test File System')
        parser.setMustHaveParameter('MPIIO Independent N-to-1 Test File System')
        parser.setMustHaveParameter('MPIIO N-to-N Test File System')
    if appKerNResVars==None or (appKerNResVars!=None and 'testPOSIX' in appKerNResVars and appKerNResVars['testPOSIX']==True):
        parser.setMustHaveParameter('POSIX N-to-1 Test File System')
        parser.setMustHaveParameter('POSIX N-to-N Test File System')
    if appKerNResVars==None or (appKerNResVars!=None and 'testNetCDF' in appKerNResVars and appKerNResVars['testNetCDF']==True):
        parser.setMustHaveParameter('Parallel NetCDF Collective N-to-1 Test File System')
        parser.setMustHaveParameter('Parallel NetCDF Independent N-to-1 Test File System')
    parser.setMustHaveParameter('Parallel NetCDF Version')
    parser.setMustHaveParameter('Per-Process Data Size')
    parser.setMustHaveParameter('Per-Process I/O Block Size')
    parser.setMustHaveParameter('RunEnv:Nodes')
    parser.setMustHaveParameter('Transfer Size Per I/O')
    
    if appKerNResVars==None or (appKerNResVars!=None and 'testHDF5' in appKerNResVars and appKerNResVars['testHDF5']==True):
        parser.setMustHaveStatistic('HDF5 Collective N-to-1 Read Aggregate Throughput')
        parser.setMustHaveStatistic('HDF5 Collective N-to-1 Write Aggregate Throughput')
        parser.setMustHaveStatistic('HDF5 Independent N-to-1 Read Aggregate Throughput')
        parser.setMustHaveStatistic('HDF5 Independent N-to-1 Write Aggregate Throughput')
        parser.setMustHaveStatistic('HDF5 N-to-N Read Aggregate Throughput')
        parser.setMustHaveStatistic('HDF5 N-to-N Write Aggregate Throughput')
    if appKerNResVars==None or (appKerNResVars!=None and 'testMPIIO' in appKerNResVars and appKerNResVars['testMPIIO']==True):
        parser.setMustHaveStatistic('MPIIO Collective N-to-1 Read Aggregate Throughput')
        parser.setMustHaveStatistic('MPIIO Collective N-to-1 Write Aggregate Throughput')
        parser.setMustHaveStatistic('MPIIO Independent N-to-1 Read Aggregate Throughput')
        parser.setMustHaveStatistic('MPIIO Independent N-to-1 Write Aggregate Throughput')
        parser.setMustHaveStatistic('MPIIO N-to-N Read Aggregate Throughput')
        parser.setMustHaveStatistic('MPIIO N-to-N Write Aggregate Throughput')
    if appKerNResVars==None or (appKerNResVars!=None and 'testPOSIX' in appKerNResVars and appKerNResVars['testPOSIX']==True):
        parser.setMustHaveStatistic('POSIX N-to-1 Read Aggregate Throughput')
        parser.setMustHaveStatistic('POSIX N-to-1 Write Aggregate Throughput')
        parser.setMustHaveStatistic('POSIX N-to-N Read Aggregate Throughput')
        parser.setMustHaveStatistic('POSIX N-to-N Write Aggregate Throughput')
    if appKerNResVars==None or (appKerNResVars!=None and 'testNetCDF' in appKerNResVars and appKerNResVars['testNetCDF']==True):
        parser.setMustHaveStatistic('Parallel NetCDF Collective N-to-1 Read Aggregate Throughput')
        parser.setMustHaveStatistic('Parallel NetCDF Collective N-to-1 Write Aggregate Throughput')
        parser.setMustHaveStatistic('Parallel NetCDF Independent N-to-1 Read Aggregate Throughput')
        parser.setMustHaveStatistic('Parallel NetCDF Independent N-to-1 Write Aggregate Throughput')
    
    parser.setMustHaveStatistic('Number of Tests Passed')
    parser.setMustHaveStatistic('Number of Tests Started')
     
    parser.setMustHaveStatistic('Wall Clock Time')
    
    parser.completeOnPartialMustHaveStatistics=True
    #parse common parameters and statistics
    parser.parseCommonParsAndStats(appstdout,stdout,stderr,geninfo)
    
    if hasattr(parser,'appKerWallClockTime'):
        parser.setStatistic("Wall Clock Time", total_seconds(parser.appKerWallClockTime), "Second")
    
    #read output
    lines=[]
    if os.path.isfile(appstdout):
        fin=open(appstdout,"rt")
        lines=fin.readlines()
        fin.close()
    
    #process the output
    
    #find which version of IOR was used
    ior_output_version=None
    j=0
    while j<len(lines)-1:
        #IOR RELEASE: IOR-2.10.3
        m=re.match(r'^#\s+IOR RELEASE:\s(.+)',lines[j])
        if m:ior_output_version=2
        
        m=re.match(r'^IOR-[3-9]\.[0-9]+\.[0-9]: MPI Coordinated Test of Parallel I/O',lines[j])
        if m:ior_output_version=3
        
        j+=1
    if ior_output_version==None:
        print("ERROR: unknown version of IOR output!!!")
    
    
    testsPassed=0
    totalNumberOfTests=0
    parser.successfulRun=False
    
    if ior_output_version==2:
        METRICS={}
        j=-1
        while j<len(lines)-1:
            m=re.match(r'^# (.+?):(.+)',lines[j])
            if m:
                METRICS[m.group(1).strip()]=m.group(2).strip()
                if m.group(1).strip()=="segmentCount":
                    METRICS[m.group(1).strip()]=m.group(2).strip().split()[0]
            m=re.match(r'^# IOR command line used:',lines[j])      
            if m:totalNumberOfTests+=1
            
            if "IOR RELEASE" in METRICS:
                parser.setParameter( "App:Version", METRICS["IOR RELEASE"])
        
            if "Compile-time HDF Version" in METRICS:
                parser.setParameter( "HDF Version", METRICS["Compile-time HDF Version"])
        
            if "Compile-time PNETCDF Version" in METRICS:
                parser.setParameter( "Parallel NetCDF Version", METRICS["Compile-time PNETCDF Version"])
                
            if "blockSize" in METRICS and "segmentCount" in METRICS:
                #print METRICS["blockSize"],METRICS["segmentCount"]
                parser.setParameter( "Per-Process Data Size", ( float(METRICS["blockSize"]) / 1024.0 / 1024.0 ) * int(METRICS["segmentCount"]), "MByte" )
                parser.setParameter( "Per-Process I/O Block Size", ( float(METRICS["blockSize"]) / 1024.0 / 1024.0 ), "MByte" )
    
        
            if "reorderTasks" in METRICS:
                if int(METRICS["reorderTasks"])!=0:
                    parser.setParameter( "Reorder Tasks for Read-back Tests", "Yes" )
    
        
            if "repetitions" in METRICS:
                if 1 < int(METRICS["repetitions"]):
                    parser.setParameter( "Test Repetitions", METRICS["repetitions"])
    
        
            if "transferSize" in METRICS:
                parser.setParameter( "Transfer Size Per I/O", ( float(METRICS["transferSize"]) / 1024.0 / 1024.0 ), "MByte" )
    
        
            if "mpiio hints passed to MPI_File_open" in METRICS:
                parser.setParameter( "MPI-IO Hints", METRICS["mpiio hints passed to MPI_File_open"])
            
            if "Write bandwidth" in METRICS and "Read bandwidth" in METRICS and \
               "api" in METRICS and "filePerProc" in METRICS and "collective" in METRICS and \
               "randomOffset" in METRICS and "Run finished" in METRICS:
                
                testsPassed+=1
                
                label = METRICS["api"];
                
                m=re.search(r'NCMPI',label,re.I)
                if m:label = "Parallel NetCDF"
                
                m=re.search(r'POSIX',label,re.I)
                if m and "useO_DIRECT" in METRICS: 
                    if int(METRICS["useO_DIRECT"]) != 0:
                        label += ' (O_DIRECT)'
                if m==None:
                    # POSIX doesn't have collective I/O
                    if int(METRICS["collective"]) == 0: label += ' Independent'
                    else: label += ' Collective'
                
                if int(METRICS["randomOffset"]) == 0: label += ''
                else: label += ' Random'
                
                if int(METRICS["filePerProc"]) == 0: label += ' N-to-1'
                else: label += ' N-to-N'
                
                # for N-to-N (each process writes to its own file), it must be
                # Independent, so we can remove the redundant words such as
                # "Independent" and "Collective"
                m=re.search(r' (Independent|Collective).+N-to-N',label,re.I)
                if m:
                    label=label.replace(" Independent","").replace(" Collective","")
        
                # now we have the label, get test-specific parameters
                m=re.search(r'MPIIO',label,re.I)
                if m:
                    if "useFileView" in METRICS:
                        if 0 != int(METRICS["useFileView"]):
                            parser.setParameter( label + " Uses MPI_File_set_view",   "Yes" ) 
                    if "useSharedFilePointer" in METRICS:
                        if 0 != int(METRICS["useSharedFilePointer"]):
                            parser.setParameter( label + " Uses Shared File Pointer", "Yes" )
                
                m=re.search(r'POSIX',label,re.I)
                if m:
                    if "fsyncPerWrite" in METRICS:
                        if 0 != int(METRICS["fsyncPerWrite"]):
                            parser.setParameter( label + " Uses fsync per Write", "Yes" )
                
                m=re.search(r'mean=(\S+)',METRICS["Write bandwidth"])
                if m:
                    metric     = m.group(1).strip()
                    writeLabel = label
        
                    # writes are always sequential
                    writeLabel = writeLabel.replace(" Random","")
                    parser.setStatistic( writeLabel+" Write Aggregate Throughput", "%.2f"%(float(metric) / 1024.0 / 1024.0, ), "MByte per Second" );
                    #parser.setParameter( "${writeLabel} Test File",        METRICS["testFileName"} ) if ( exists METRICS["testFileName"} );
                    if "fileSystem" in METRICS:
                        parser.setParameter( writeLabel+" Test File System", METRICS["fileSystem"])
                    parser.successfulRun=True
                    
                    if "File Open Time (Write)" in METRICS:
                        m2=re.search(r'mean=(\S+)',METRICS["File Open Time (Write)"])
                        if m2:
                            parser.setStatistic( writeLabel+"  File Open Time (Write)", m2.group(1).strip(), "Second" );
                    if "File Close Time (Write)" in METRICS:
                        m2=re.search(r'mean=(\S+)',METRICS["File Close Time (Write)"])
                        if m2:                   
                            parser.setStatistic( writeLabel+"  File Close Time (Write)", m2.group(1).strip(), "Second" );
                            
        
                m=re.search(r'mean=(\S+)',METRICS["Read bandwidth"])
                if m:
                    parser.setStatistic( label+" Read Aggregate Throughput", "%.2f"%(float(m.group(1).strip()) / 1024.0 / 1024.0, ), "MByte per Second" );
                    parser.successfulRun=True
                    
                    if "File Open Time (Read)" in METRICS:
                        m2=re.search(r'mean=(\S+)',METRICS["File Open Time (Read)"])
                        if m2:                   
                            parser.setStatistic( writeLabel+"  File Open Time (Read)", m2.group(1).strip(), "Second" );
                    if "File Close Time (Read)" in METRICS:
                        m2=re.search(r'mean=(\S+)',METRICS["File Close Time (Read)"])
                        if m2:                   
                            parser.setStatistic( writeLabel+"  File Close Time (Read)", m2.group(1).strip(), "Second" );
                
                METRICS={}
        
            j+=1
    
    if ior_output_version==3:
        i=0
        input_summary={}
        rsl_w={}
        rsl_r={}
        filesystem=None
        while i<len(lines)-1:
            m=re.match(r'^IOR-([3-9]\.[0-9]+\.[0-9]+): MPI Coordinated Test of Parallel I/O',lines[i])
            if m:parser.setParameter( "App:Version", m.group(1).strip())
            
            m=re.match(r'^File System To Test:(.+)',lines[i])
            if m:filesystem=m.group(1).strip()
            
            m=re.match(r'^# Starting Test:',lines[i])
            if m:totalNumberOfTests+=1
            
            m0=re.match(r'^Summary:$',lines[i])
            if m0:
                #input summary section
                input_summary={}
                i+=1
                while i<len(lines):
                    m1=re.match(r'^\t([^=\n\r\f\v]+)=(.+)',lines[i])
                    if m1:
                        input_summary[m1.group(1).strip()]=m1.group(2).strip()
                    else:
                        break
                    i+=1
                #process input_summary
                input_summary['filesystem']=filesystem
                input_summary['API']=input_summary['api']
                if input_summary['api'].count("MPIIO")>0:
                    input_summary['API']="MPIIO"
                    input_summary['API_Version']=input_summary['api'].replace("MPIIO","").strip()
                    parser.setParameter( "MPIIO Version", input_summary['API_Version'])
                if input_summary['api'].count("HDF5")>0:
                    input_summary['API']="HDF5"
                    input_summary['API_Version']=input_summary['api'].replace("HDF5-","").replace("HDF5","").strip()
                    parser.setParameter( "HDF Version", input_summary['API_Version'])
                if input_summary['api'].count("NCMPI")>0:
                    input_summary['API']="Parallel NetCDF"
                    input_summary['API_Version']=input_summary['api'].replace("NCMPI","").strip()
                    parser.setParameter( "Parallel NetCDF Version", input_summary['API_Version'])
                
                input_summary['fileAccessPattern']=""
                input_summary['collectiveOrIndependent']=""
                if input_summary['access'].count('single-shared-file')>0:
                    input_summary['fileAccessPattern']="N-to-1"
                if input_summary['access'].count('file-per-process')>0:
                    input_summary['fileAccessPattern']="N-to-N"
                if input_summary['access'].count('independent')>0:
                    input_summary['collectiveOrIndependent']="Independent"
                if input_summary['access'].count('collective')>0:
                    input_summary['collectiveOrIndependent']="Collective"
                if input_summary['fileAccessPattern']=="N-to-N" and input_summary['collectiveOrIndependent']=="Independent":
                    input_summary['collectiveOrIndependent']=""
                
                if input_summary['collectiveOrIndependent']!="":
                    input_summary['method']=" ".join((input_summary['API'],
                                                      input_summary['collectiveOrIndependent'],
                                                      input_summary['fileAccessPattern']))
                else:
                    input_summary['method']=" ".join((input_summary['API'],
                                                      input_summary['fileAccessPattern']))
                
                if input_summary['filesystem']!=None:
                    parser.setParameter(input_summary['method']+' Test File System',input_summary['filesystem'])
                    
                if "pattern" in input_summary:
                    m1=re.match(r'^segmented \(([0-9]+) segment',input_summary["pattern"])
                    if m1:input_summary["segmentCount"]=int(m1.group(1).strip())
                
                if "blocksize" in input_summary and "segmentCount" in input_summary:
                    val,unit=input_summary["blocksize"].split()
                    blockSize=getMiB(float(val),unit)
                    segmentCount=input_summary["segmentCount"]
                    parser.setParameter( "Per-Process Data Size", blockSize*segmentCount, "MByte" )
                    parser.setParameter( "Per-Process I/O Block Size", blockSize, "MByte" )
                
                if "xfersize" in input_summary:
                    val,unit=input_summary["xfersize"].split()
                    transferSize=getMiB(float(val),unit)
                    parser.setParameter( "Transfer Size Per I/O", transferSize, "MByte" )
            
            m0=re.match(r'^access\s+bw\(MiB/s\)\s+block\(KiB\)\s+xfer\(KiB\)\s+open\(s\)\s+wr/rd\(s\)\s+close\(s\)\s+total\(s\)\s+iter',lines[i])
            if m0:
                i+=1
                while i<len(lines):
                    m1=re.match(r'^write\s+([0-9\.]+)+\s+([0-9\.]+)+\s+([0-9\.]+)+\s+([0-9\.]+)+\s+([0-9\.]+)+\s+([0-9\.]+)+\s+([0-9\.]+)+\s+([0-9\.]+)+',lines[i])
                    m2=re.match(r'^read\s+([0-9\.]+)+\s+([0-9\.]+)+\s+([0-9\.]+)+\s+([0-9\.]+)+\s+([0-9\.]+)+\s+([0-9\.]+)+\s+([0-9\.]+)+\s+([0-9\.]+)+',lines[i])
                    if m1 or m2:
                        if m1:
                            access="Write"
                            bw,block,xfer,open_s,wrrd_s,close_s,total_s,iter=m1.groups()
                        else:
                            access="Read"
                            bw,block,xfer,open_s,wrrd_s,close_s,total_s,iter=m2.groups()
                            testsPassed+=1
                            parser.successfulRun=True
                        
                        parser.setStatistic( input_summary['method']+" %s Aggregate Throughput"%access, bw, "MByte per Second" );
                        parser.setStatistic( input_summary['method']+"  File Open Time (%s)"%access, open_s, "Second" );
                        parser.setStatistic( input_summary['method']+"  File Close Time (%s)"%access, close_s, "Second" );
                    
                    m1=re.match(r'^Summary of all tests:',lines[i])
                    if m1:break
                    i+=1
                #reset variables
                input_summary={}
                rsl_w={}
                rsl_r={}
                #filesystem=None
            i+=1
    parser.setStatistic('Number of Tests Passed',testsPassed )
    parser.setStatistic('Number of Tests Started',totalNumberOfTests )
    
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
    
    

