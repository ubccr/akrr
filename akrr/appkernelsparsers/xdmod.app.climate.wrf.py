import re
import os
import sys
import time

#Set proper path for stand alone test runs
if __name__ == "__main__":
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),'../..'))

import akrr.appkernelsparsers.akrrappkeroutputparser
from akrr.appkernelsparsers.akrrappkeroutputparser import AppKerOutputParser

def processAppKerOutput(appstdout=None,stdout=None,stderr=None,geninfo=None,appKerNResVars=None):
    #set App Kernel Description
    parser=AppKerOutputParser(
        name             = 'xdmod.app.climate.wrf',
        version          = 1,
        description      = "Weather Research and Forecasting Model",
        url              = 'http://www.wrf-model.org',
        measurement_name = 'WRF'
    )
    #set obligatory parameters and statistics
    #set common parameters and statistics
    parser.setCommonMustHaveParsAndStats()
    #set app kernel custom sets  
    parser.setMustHaveParameter('App:Version')
    parser.setMustHaveParameter('Input:Grid Resolution')
    parser.setMustHaveParameter('Input:Simulation Length')
    parser.setMustHaveParameter('Input:Simulation Start Date')
    parser.setMustHaveParameter('Input:Timestep')
    parser.setMustHaveParameter('RunEnv:Nodes')
    parser.setMustHaveParameter('WRF Dynamical Solver')
    
    #parser.setMustHaveStatistic('Average Floating-Point Performance')
    parser.setMustHaveStatistic('Average Simulation Speed')
    parser.setMustHaveStatistic('Mean Time To Simulate One Timestep')
    parser.setMustHaveStatistic('Output Data Size')
    #parser.setMustHaveStatistic('Peak Floating-Point Performance')
    parser.setMustHaveStatistic('Peak Simulation Speed')
    parser.setMustHaveStatistic('Time Spent on I/O')
    parser.setMustHaveStatistic('Wall Clock Time')
    
    
    #parse common parameters and statistics
    parser.parseCommonParsAndStats(appstdout,stdout,stderr,geninfo)
    
    #read output
    lines=[]
    if os.path.isfile(appstdout):
        fin=open(appstdout,"rt")
        lines=fin.readlines()
        fin.close()
    
    #process the output
    IOsize=None
    wallClockTime=None
    iterationWallClockTime=[]
    simTimePerIteration=None
    dx=None
    dy=None
    flopsConversion=None
    
    j=0
    while j<len(lines):
        m=re.search(r'XDMOD\*\*\*SIZE OF CURRENT DIR BEFORE WRF RUN\s*(\d+)',lines[j])
        if m:IOsize=int(m.group(1).strip())
        
        m=re.search(r'XDMOD\*\*\*SIZE OF CURRENT DIR AFTER WRF RUN\s*(\d+)',lines[j])
        if m and IOsize:parser.setStatistic("Output Data Size",
            (int(m.group(1).strip())-IOsize)/1024.0/1024.0, "MByte" );
        
        m=re.search(r'XDMOD\*\*\*WRF RUN BEGINS HERE --(.+)',lines[j])
        if m:wallClockTime=parser.getDateTimeLocal(m.group(1).strip())
        
        m=re.search(r'XDMOD\*\*\*WRF RUN HAS FINISHED --(.+)',lines[j])
        if m and wallClockTime:
            wallClockTime=parser.getDateTimeLocal(m.group(1).strip())-wallClockTime
            parser.setStatistic("Wall Clock Time", wallClockTime.total_seconds(), "Second" );
        
        if lines[j].find('XDMOD***RESULT OF rsl.out.0000 BEGINS')>=0:
            # the output from MPI rank #0
            IOtime = 0.0
            while j<len(lines):
                if lines[j].find('XDMOD***RESULT OF rsl.out.0000 ENDS')>=0:break
                
                m=re.search(r'Timing for processing restart file.+?:\s+(\d\S+)',lines[j],re.I)
                if m:IOtime+=float(m.group(1).strip())
                
                m=re.search(r'Timing for Writing.+?:\s+(\d\S+)',lines[j],re.I)
                if m:IOtime+=float(m.group(1).strip())
                
                m=re.search(r'Timing for main: time.+?on domain.+?:\s+(\d\S+)',lines[j],re.I)
                if m:iterationWallClockTime.append(float(m.group(1).strip()))
                
                m=re.search(r'WRF NUMBER OF TILES.+?(\d+)',lines[j])
                if m:
                    ompThreads=int(m.group(1).strip())
                    if ompThreads>1:
                        parser.setParameter("Number of OpenMP Threads",ompThreads)
                
                m=re.match(r'^\s+WRF V(\S+) MODEL',lines[j])
                if m:parser.setParameter("App:Version",m.group(1).strip())
                j+=1
            parser.setStatistic("Time Spent on I/O",IOtime, "Second")
        
        if re.search('XDMOD\*\*\*RESULT OF wrfout.+?BEGINS',lines[j])>=0:
            # the output file's header (netCDF dump)
            while j<len(lines):
                if re.search('XDMOD\*\*\*RESULT OF wrfout.+?ENDS',lines[j])>=0:break
                
                m=re.search(r':DX = (\d+)',lines[j],re.I)
                if m:dx=float(m.group(1).strip())*0.001 # in meters
                
                m=re.search(r':DY = (\d+)',lines[j],re.I)
                if m:dy=float(m.group(1).strip())*0.001 # in meters
                
                m=re.search(r':DT = (\d+)',lines[j],re.I)
                if m:
                    simTimePerIteration=float(m.group(1).strip()) # in seconds
                    parser.setParameter("Input:Timestep", simTimePerIteration, "Second per Step" )
                
                m=re.search(r':SIMULATION_START_DATE = "(.+?)"',lines[j],re.I)
                if m:parser.setParameter("Input:Simulation Start Date", (m.group(1).strip()));
                
                m=re.search(r':GRIDTYPE = "(.+?)"',lines[j],re.I)
                if m:
                    solver=m.group(1).strip()
                    if solver=='C':solver = 'Advanced Research WRF (ARW)'
                    if solver=='E':solver =  'Nonhydrostatic Mesoscale Model (NMM)'
                    parser.setParameter("WRF Dynamical Solver", solver)
                
                
                m=re.search(r'Timing for Writing.+?:\s+(\d\S+)',lines[j],re.I)
                if m:IOtime+=float(m.group(1).strip())
                
                m=re.search(r'Timing for main: time.+?on domain.+?:\s+(\d\S+)',lines[j],re.I)
                if m:iterationWallClockTime.append(float(m.group(1).strip()))
                
                m=re.search(r'WRF NUMBER OF TILES.+?(\d+)',lines[j])
                if m:
                    ompThreads=int(m.group(1).strip())
                    if ompThreads>1:
                        parser.setParameter("Number of OpenMP Threads",ompThreads)
                
                m=re.match(r'^\s+WRF V(\S+) MODEL',lines[j])
                if m:parser.setParameter("App:Version",m.group(1).strip())
                j+=1
            if dx and dy:
                if (dx-int(dx))*1000<0.1 and (dy-int(dy))*1000<0.1:#back compatibility with output format
                    parser.setParameter("Input:Grid Resolution","%.0f x %.0f"%(dx,dy), "km^2")
                else:
                    parser.setParameter("Input:Grid Resolution",str(dx)+" x "+str(dy), "km^2")
        
        m=re.search(r'XDMOD\*\*\*FLOATING-POINT PERFORMANCE CONVERSION',lines[j])
        if m:flopsConversion=lines[j+1].strip()
        j+=1
    
    if wallClockTime: parser.successfulRun=True
    else: parser.successfulRun=False
    
    if len(iterationWallClockTime)>0 and simTimePerIteration:
        parser.setParameter( "Input:Simulation Length", ( len(iterationWallClockTime) ) * simTimePerIteration / 3600.0, "Hour" );
        iterationWallClockTime=sorted(iterationWallClockTime)
        iterationWallClockTime.pop()
        
        t = 0.0
        minT = iterationWallClockTime[0]
        for tt in iterationWallClockTime:t+=tt
        t=t/len(iterationWallClockTime)
        parser.setStatistic( "Mean Time To Simulate One Timestep", t,                           "Second" )
        parser.setStatistic( "Average Simulation Speed",           simTimePerIteration / t,    "Simulated Second per Second" )
        parser.setStatistic( "Peak Simulation Speed",              simTimePerIteration / minT, "Simulated Second per Second" )
        
        if flopsConversion:
           flopsConversion=flopsConversion.replace("$","").replace("gflops=","")
           gflops=eval(flopsConversion,{'T':t})
           parser.setStatistic( "Average Floating-Point Performance", 1000.0 * gflops, "MFLOP per Second" )
           gflops=eval(flopsConversion,{'T':minT})
           parser.setStatistic( "Peak Floating-Point Performance", 1000.0 * gflops, "MFLOP per Second" )
        
    if __name__ == "__main__":
        #output for testing purpose
        parsingComplete=parser.parsingComplete(True)
        print "parsing complete:",parsingComplete
        if hasattr(parser, 'successfulRun'):print "successfulRun",parser.successfulRun
        parser.printParsNStatsAsMustHave()
        print parser.getXML()
        
    
    #return complete XML overwize return None
    return parser.getXML()
    
    
if __name__ == "__main__":
    """stand alone testing"""
    jobdir=sys.argv[1]
    print "Proccessing Output From",jobdir
    processAppKerOutput(appstdout=os.path.join(jobdir,"appstdout"),geninfo=os.path.join(jobdir,"gen.info"))
    
    

