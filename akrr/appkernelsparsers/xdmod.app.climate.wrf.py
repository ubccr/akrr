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
    parser.add_common_must_have_params_and_stats()
    #set app kernel custom sets  
    parser.add_must_have_parameter('App:Version')
    parser.add_must_have_parameter('Input:Grid Resolution')
    parser.add_must_have_parameter('Input:Simulation Length')
    parser.add_must_have_parameter('Input:Simulation Start Date')
    parser.add_must_have_parameter('Input:Timestep')
    parser.add_must_have_parameter('RunEnv:Nodes')
    parser.add_must_have_parameter('WRF Dynamical Solver')
    
    #parser.add_must_have_statistic('Average Floating-Point Performance')
    parser.add_must_have_statistic('Average Simulation Speed')
    parser.add_must_have_statistic('Mean Time To Simulate One Timestep')
    parser.add_must_have_statistic('Output Data Size')
    #parser.add_must_have_statistic('Peak Floating-Point Performance')
    parser.add_must_have_statistic('Peak Simulation Speed')
    parser.add_must_have_statistic('Time Spent on I/O')
    parser.add_must_have_statistic('Wall Clock Time')
    
    
    #parse common parameters and statistics
    parser.parse_common_params_and_stats(appstdout, stdout, stderr, geninfo)
    
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
        if m and IOsize:parser.set_statistic("Output Data Size",
                                             (int(m.group(1).strip())-IOsize) / 1024.0 / 1024.0, "MByte");
        
        m=re.search(r'XDMOD\*\*\*WRF RUN BEGINS HERE --(.+)',lines[j])
        if m:wallClockTime=parser.get_datetime_local(m.group(1).strip())
        
        m=re.search(r'XDMOD\*\*\*WRF RUN HAS FINISHED --(.+)',lines[j])
        if m and wallClockTime:
            wallClockTime= parser.get_datetime_local(m.group(1).strip()) - wallClockTime
            parser.set_statistic("Wall Clock Time", wallClockTime.total_seconds(), "Second");
        
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
                        parser.set_parameter("Number of OpenMP Threads", ompThreads)
                
                m=re.match(r'^\s+WRF V(\S+) MODEL',lines[j])
                if m:parser.set_parameter("App:Version", m.group(1).strip())
                j+=1
            parser.set_statistic("Time Spent on I/O", IOtime, "Second")
        
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
                    parser.set_parameter("Input:Timestep", simTimePerIteration, "Second per Step")
                
                m=re.search(r':SIMULATION_START_DATE = "(.+?)"',lines[j],re.I)
                if m:parser.set_parameter("Input:Simulation Start Date", (m.group(1).strip()));
                
                m=re.search(r':GRIDTYPE = "(.+?)"',lines[j],re.I)
                if m:
                    solver=m.group(1).strip()
                    if solver=='C':solver = 'Advanced Research WRF (ARW)'
                    if solver=='E':solver =  'Nonhydrostatic Mesoscale Model (NMM)'
                    parser.set_parameter("WRF Dynamical Solver", solver)
                
                
                m=re.search(r'Timing for Writing.+?:\s+(\d\S+)',lines[j],re.I)
                if m:IOtime+=float(m.group(1).strip())
                
                m=re.search(r'Timing for main: time.+?on domain.+?:\s+(\d\S+)',lines[j],re.I)
                if m:iterationWallClockTime.append(float(m.group(1).strip()))
                
                m=re.search(r'WRF NUMBER OF TILES.+?(\d+)',lines[j])
                if m:
                    ompThreads=int(m.group(1).strip())
                    if ompThreads>1:
                        parser.set_parameter("Number of OpenMP Threads", ompThreads)
                
                m=re.match(r'^\s+WRF V(\S+) MODEL',lines[j])
                if m:parser.set_parameter("App:Version", m.group(1).strip())
                j+=1
            if dx and dy:
                if (dx-int(dx))*1000<0.1 and (dy-int(dy))*1000<0.1:#back compatibility with output format
                    parser.set_parameter("Input:Grid Resolution", "%.0f x %.0f" % (dx, dy), "km^2")
                else:
                    parser.set_parameter("Input:Grid Resolution", str(dx) + " x " + str(dy), "km^2")
        
        m=re.search(r'XDMOD\*\*\*FLOATING-POINT PERFORMANCE CONVERSION',lines[j])
        if m:flopsConversion=lines[j+1].strip()
        j+=1
    
    if wallClockTime: parser.successfulRun=True
    else: parser.successfulRun=False
    
    if len(iterationWallClockTime)>0 and simTimePerIteration:
        parser.set_parameter("Input:Simulation Length", (len(iterationWallClockTime)) * simTimePerIteration / 3600.0, "Hour");
        iterationWallClockTime=sorted(iterationWallClockTime)
        iterationWallClockTime.pop()
        
        t = 0.0
        minT = iterationWallClockTime[0]
        for tt in iterationWallClockTime:t+=tt
        t=t/len(iterationWallClockTime)
        parser.set_statistic("Mean Time To Simulate One Timestep", t, "Second")
        parser.set_statistic("Average Simulation Speed", simTimePerIteration / t, "Simulated Second per Second")
        parser.set_statistic("Peak Simulation Speed", simTimePerIteration / minT, "Simulated Second per Second")
        
        if flopsConversion:
           flopsConversion=flopsConversion.replace("$","").replace("gflops=","")
           gflops=eval(flopsConversion,{'T':t})
           parser.set_statistic("Average Floating-Point Performance", 1000.0 * gflops, "MFLOP per Second")
           gflops=eval(flopsConversion,{'T':minT})
           parser.set_statistic("Peak Floating-Point Performance", 1000.0 * gflops, "MFLOP per Second")
        
    if __name__ == "__main__":
        #output for testing purpose
        parsingComplete=parser.parsing_complete(True)
        print("parsing complete:",parsingComplete)
        if hasattr(parser, 'successfulRun'):print("successfulRun",parser.successfulRun)
        parser.print_params_stats_as_must_have()
        print(parser.get_xml())
        
    
    #return complete XML overwize return None
    return parser.get_xml()
    
    
if __name__ == "__main__":
    """stand alone testing"""
    jobdir=sys.argv[1]
    print("Proccessing Output From",jobdir)
    processAppKerOutput(appstdout=os.path.join(jobdir,"appstdout"),geninfo=os.path.join(jobdir,"gen.info"))
    
    

