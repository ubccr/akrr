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

def processAppKerOutput(appstdout=None,stdout=None,stderr=None,geninfo=None,appKerNResVars=None):
    #set App Kernel Description
    parser=AppKerOutputParser(
        name             = 'xdmod.benchmark.io.mpi-tile-io',
        version          = 1,
        description      = "MPI-Tile-IO Benchmark",
        url              = 'http://www.mcs.anl.gov/research/projects/pio-benchmark',
        measurement_name = 'MPI-Tile-IO'
    )
    #set obligatory parameters and statistics
    #set common parameters and statistics
    parser.setCommonMustHaveParsAndStats()
    #set app kernel custom sets  
    parser.setMustHaveParameter('2D Collective Read Test File System')
    parser.setMustHaveParameter('2D Collective Write Test File System')
    parser.setMustHaveParameter('2D HDF5 Collective Read Test File System')
    parser.setMustHaveParameter('2D HDF5 Collective Write Test File System')
    parser.setMustHaveParameter('2D Independent Read Test File System')
    parser.setMustHaveParameter('2D Independent Write Test File System')
    parser.setMustHaveParameter('2D Per-Process Data Topology')
    parser.setMustHaveParameter('2D Per-Process Ghost Zone')
    parser.setMustHaveParameter('2D Per-Process Memory')
    parser.setMustHaveParameter('2D Process Topology')
    parser.setMustHaveParameter('3D Collective Read Test File System')
    parser.setMustHaveParameter('3D Collective Write Test File System')
    parser.setMustHaveParameter('3D HDF5 Collective Read Test File System')
    parser.setMustHaveParameter('3D HDF5 Collective Write Test File System')
    parser.setMustHaveParameter('3D Independent Read Test File System')
    parser.setMustHaveParameter('3D Independent Write Test File System')
    parser.setMustHaveParameter('3D Per-Process Data Topology')
    parser.setMustHaveParameter('3D Per-Process Ghost Zone')
    parser.setMustHaveParameter('3D Per-Process Memory')
    parser.setMustHaveParameter('3D Process Topology')
    parser.setMustHaveParameter('App:ExeBinSignature')
    parser.setMustHaveParameter('HDF Version')
    #parser.setMustHaveParameter('MPI-IO Hints')
    parser.setMustHaveParameter('RunEnv:Nodes')
    
    parser.setMustHaveStatistic('2D Array Collective Read Aggregate Throughput')
    parser.setMustHaveStatistic('2D Array Collective Write Aggregate Throughput')
    parser.setMustHaveStatistic('2D Array HDF5 Collective Read Aggregate Throughput')
    parser.setMustHaveStatistic('2D Array HDF5 Collective Write Aggregate Throughput')
    parser.setMustHaveStatistic('2D Array Independent Read Aggregate Throughput')
    parser.setMustHaveStatistic('2D Array Independent Write Aggregate Throughput')
    parser.setMustHaveStatistic('3D Array Collective Read Aggregate Throughput')
    parser.setMustHaveStatistic('3D Array Collective Write Aggregate Throughput')
    parser.setMustHaveStatistic('3D Array HDF5 Collective Read Aggregate Throughput')
    parser.setMustHaveStatistic('3D Array HDF5 Collective Write Aggregate Throughput')
    parser.setMustHaveStatistic('3D Array Independent Read Aggregate Throughput')
    parser.setMustHaveStatistic('3D Array Independent Write Aggregate Throughput')
    parser.setMustHaveStatistic('File Close Time (2D Data Collective Read)')
    parser.setMustHaveStatistic('File Close Time (2D Data Collective Write)')
    parser.setMustHaveStatistic('File Close Time (2D Data HDF5 Collective Read)')
    parser.setMustHaveStatistic('File Close Time (2D Data HDF5 Collective Write)')
    parser.setMustHaveStatistic('File Close Time (2D Data Independent Read)')
    parser.setMustHaveStatistic('File Close Time (2D Data Independent Write)')
    parser.setMustHaveStatistic('File Close Time (3D Data Collective Read)')
    parser.setMustHaveStatistic('File Close Time (3D Data Collective Write)')
    parser.setMustHaveStatistic('File Close Time (3D Data HDF5 Collective Read)')
    parser.setMustHaveStatistic('File Close Time (3D Data HDF5 Collective Write)')
    parser.setMustHaveStatistic('File Close Time (3D Data Independent Read)')
    parser.setMustHaveStatistic('File Close Time (3D Data Independent Write)')
    parser.setMustHaveStatistic('File Open Time (2D Data Collective Read)')
    parser.setMustHaveStatistic('File Open Time (2D Data Collective Write)')
    parser.setMustHaveStatistic('File Open Time (2D Data HDF5 Collective Read)')
    parser.setMustHaveStatistic('File Open Time (2D Data HDF5 Collective Write)')
    parser.setMustHaveStatistic('File Open Time (2D Data Independent Read)')
    parser.setMustHaveStatistic('File Open Time (2D Data Independent Write)')
    parser.setMustHaveStatistic('File Open Time (3D Data Collective Read)')
    parser.setMustHaveStatistic('File Open Time (3D Data Collective Write)')
    parser.setMustHaveStatistic('File Open Time (3D Data HDF5 Collective Read)')
    parser.setMustHaveStatistic('File Open Time (3D Data HDF5 Collective Write)')
    parser.setMustHaveStatistic('File Open Time (3D Data Independent Read)')
    parser.setMustHaveStatistic('File Open Time (3D Data Independent Write)')
    parser.setMustHaveStatistic('Wall Clock Time')
    
    #parse common parameters and statistics
    parser.parseCommonParsAndStats(appstdout,stdout,stderr,geninfo)
    
    if hasattr(parser,'appKerWallClockTime'):
        parser.setStatistic("Wall Clock Time", parser.appKerWallClockTime.total_seconds(), "Second")
    
    #read output
    lines=[]
    if os.path.isfile(appstdout):
        fin=open(appstdout,"rt")
        lines=fin.readlines()
        fin.close()
    
    #process the output
    # The parameters mapping table
    # The result mapping table
    pm = {
        "processesTopology":{
            're':r"^# processes topology:(.+)",
            'refun':re.match,
            'val':None},      
        "localDatasetTopology":{
            're':r"^# local dataset topology:(.+)element",
            'refun':re.match,
            'val':None},
        "localMemoryUsage":{
            're':r"^# local dataset memory usage:(.+)byte",
            'refun':re.match,
            'val':None},
        "datasetGhostZone":{
            're':r"^# local dataset ghost zone:(.+)",
            'refun':re.match,
            'val':None},
        "mpiIOhints":{
            're':r"^# mpiio hints:(.+)",
            'refun':re.match,
            'val':None},
        "maxFileOpenTime":{
            're':r"^# Open:.+?max=(\S+)",
            'refun':re.match,
            'val':None},
        "maxFileCloseTime":{
            're':r"^# Close:.+?max=(\S+)",
            'refun':re.match,
            'val':None},
        "collectiveIO":{
            're':r"^# collective IO:(.+)",
            'refun':re.match,
            'val':None},
        "testFileName":{
            're':r"^# filename:(.+)",
            'refun':re.match,
            'val':None},
        "fileSystem":{
            're':r"^# filesystem:(.+)",
            'refun':re.match,
            'val':None},
        "hdf5Version":{
            're':r"^# HDF5 Version:(.+)",
            'refun':re.match,
            'val':None},
    }
    
    parser.successfulRun=False
    j=-1
    while j<len(lines)-1:
        for k,v in pm.iteritems():
            m=v['refun'](v['re'],lines[j])
            if m: v['val']=m.group(1).strip()

        m=re.match(r'^# (.+?)bandwidth:(.+)bytes',lines[j])
        if m:
            readOrWrite = m.group(1).strip()
            IObandwidth = m.group(2).strip()
            
            # can output data ?
            if pm['processesTopology']['val'] and pm['collectiveIO']['val']:
                # construct the label
                label=''
                dim='2D'
                m=re.search(r'\d+x\d+x\d',pm['processesTopology']['val'])
                if m:dim = '3D'
    
                if pm['hdf5Version']['val']:
                    label += 'HDF5 '
                    parser.setParameter( "HDF Version", pm['hdf5Version']['val'] )
                
                m=re.search(r'yes',pm['collectiveIO']['val'],re.I)
                if m: label += 'Collective '
                else: label += 'Independent '
                
                m0=re.search(r'read',readOrWrite,re.I)
                m1=re.search(r'write',readOrWrite,re.I)
                if m0:label += 'Read'
                elif m1:label += 'Write'
                else:
                    l=readOrWrite
                    label += l.uppercase()[0]+l[1:]
    
                parser.setStatistic( "%s Array %s Aggregate Throughput"%(dim,label),
                    "%.2f"%(float(IObandwidth) / 1024.0 / 1024.0 ), "MByte per Second" )
                if pm["maxFileOpenTime"]['val']:
                    parser.setStatistic( "File Open Time (%s Data %s)"%(dim,label),  pm["maxFileOpenTime"]['val'],  "Second" ) 
                if pm["maxFileCloseTime"]['val']:
                    parser.setStatistic( "File Close Time (%s Data %s)"%(dim,label), pm["maxFileCloseTime"]['val'], "Second" )
    
                parser.setParameter( "%s Process Topology"%(dim,),          pm["processesTopology"]['val'] );
                if pm["localMemoryUsage"]['val']:
                    parser.setParameter( "%s Per-Process Memory"%(dim,),        float(pm["localMemoryUsage"]['val']) / 1024.0 / 1024.0, "MByte" )
                if pm["localDatasetTopology"]['val']:
                    parser.setParameter( "%s Per-Process Data Topology"%(dim,), pm["localDatasetTopology"]['val'], "Element" )
                if pm["datasetGhostZone"]['val']:
                    parser.setParameter( "%s Per-Process Ghost Zone"%(dim,),    pm["datasetGhostZone"]['val'] )
                if pm["mpiIOhints"]['val']:
                    parser.setParameter( "MPI-IO Hints",                     pm["mpiIOhints"]['val'] )      
                #$benchmark->setParameter( "${dim} ${label} Test File",        $testFileName )     if ( defined($testFileName) );
                if pm["fileSystem"]['val']:
                    parser.setParameter( "%s %s Test File System"%(dim,label), pm["fileSystem"]['val'] )
                parser.successfulRun=True
        
                pm["processesTopology"]['val']=None
                pm["localDatasetTopology"]['val']=None
                pm["localMemoryUsage"]['val']=None
                pm["datasetGhostZone"]['val']=None
                pm["mpiIOhints"]['val']=None
                #pm["readOrWrite"]['val']=None
                pm["collectiveIO"]['val']=None
                #pm["IObandwidth"]['val']=None
                pm["maxFileOpenTime"]['val']=None
                pm["maxFileCloseTime"]['val']=None
                pm["testFileName"]['val']=None
                pm["fileSystem"]['val']=None
                pm["hdf5Version"]['val']=None
        j+=1
    
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
    
    

