import re
import os
import sys

#Set proper path for stand alone test runs
if __name__ == "__main__":
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),'../..'))

import akrr.appkernelsparsers.akrrappkeroutputparser
from akrr.appkernelsparsers.akrrappkeroutputparser import AppKerOutputParser

def processAppKerOutput(appstdout=None,stdout=None,stderr=None,geninfo=None,appKerNResVars=None):
    #set App Kernel Description
    parser=AppKerOutputParser(
        name             = 'xdmod.app.astro.enzo',
        version          = 1,
        description      = "Enzo: an Adaptive Mesh Refinement Code for Astrophysics",
        url              = 'http://enzo-project.org',
        measurement_name = 'Enzo'
    )
    #set obligatory parameters and statistics
    #set common parameters and statistics
    parser.add_common_must_have_params_and_stats()
    #set app kernel custom sets  
    parser.add_must_have_parameter('App:Version')
    parser.add_must_have_statistic('Wall Clock Time')
    
    #parse common parameters and statistics
    parser.parse_common_params_and_stats(appstdout, stdout, stderr, geninfo)
    
    #read output
    lines=[]
    if os.path.isfile(appstdout):
        fin=open(appstdout,"rt")
        lines=fin.readlines()
        fin.close()
    parser.set_parameter("App:Version", "unknown")
    #process the output
    successfulRun=False
    j=0
    while j<len(lines):
        m=re.match(r'^Mercurial Branch\s+(\S+)',lines[j])
        if m:
            branch=m.group(1)
            revision=""
            if j+1<len(lines):
                m=re.match(r'^Mercurial Revision\s+(\S+)',lines[j+1])
                if m:revision=m.group(1)
            parser.set_parameter("App:Version", "Branch:" + branch + " Revision:" + revision)

       
        m=re.match(r'^Time\s*=\s*([0-9\.]+)\s+CycleNumber\s*=\s*([0-9]+)\s+Wallclock\s*=\s*([0-9\.]+)',lines[j])
        if m:
            parser.set_statistic("Final Simulation Time", m.group(1), "Enzo Time Unit")
            parser.set_statistic("Total Cycles", m.group(2))
            parser.set_statistic("Wall Clock Time", m.group(3), "Second")
            successfulRun=True
       
        m=re.match(r'^Successful run, exiting.',lines[j])
        if m:
            successfulRun=True
       
        #performance
        m=re.match(r'^Cycle_Number\s+([0-9]+)',lines[j])
        if m:
            j+=1
            performanceMetrics={}
            while j<len(lines):
                if lines[j].strip()!="":
                    v=lines[j].strip().split()
                    if v[0] not in performanceMetrics:
                        performanceMetrics[v[0]]=float(v[1])
                    else:
                        performanceMetrics[v[0]]+=float(v[1])
                else:
                    if j+1<len(lines):
                        m=re.match(r'^Cycle_Number\s+([0-9]+)',lines[j+1])
                        if m: pass
                        else: break
                    else:
                        break
                j+=1
           
            metric="CommunicationTranspose"
            if metric in performanceMetrics:parser.set_statistic("Communication Transpose Time", performanceMetrics[metric], "Second")
            
            metric="ComputePotentialFieldLevelZero"
            if metric in performanceMetrics:parser.set_statistic("Gravitational Potential Field Computing Time", performanceMetrics[metric], "Second")
            
            metric="EvolvePhotons"
            if metric in performanceMetrics:parser.set_statistic("Radiative Transfer Calculation Time", performanceMetrics[metric], "Second")
            
            metric="Group_WriteAllData"
            if metric in performanceMetrics:parser.set_statistic("All Data Group Write Time", performanceMetrics[metric], "Second")
            
            metric="Level_00"
            if metric in performanceMetrics:parser.set_statistic("All Grid Level 00 Calculation Time", performanceMetrics[metric], "Second")
            
            metric="Level_01"
            if metric in performanceMetrics:parser.set_statistic("All Grid Level 01 Calculation Time", performanceMetrics[metric], "Second")
            
            metric="Level_02"
            if metric in performanceMetrics:parser.set_statistic("All Grid Level 02 Calculation Time", performanceMetrics[metric], "Second")
            
            metric="RebuildHierarchy"
            if metric in performanceMetrics:parser.set_statistic("Grid Hierarchy Rebuilding Time", performanceMetrics[metric], "Second")
           
            metric="SetBoundaryConditions"
            if metric in performanceMetrics:parser.set_statistic("Boundary Conditions Setting Time", performanceMetrics[metric], "Second")
            
            metric="SolveForPotential"
            if metric in performanceMetrics:parser.set_statistic("Poisson Equation Solving Time", performanceMetrics[metric], "Second")
            
            metric="SolveHydroEquations"
            if metric in performanceMetrics:parser.set_statistic("Hydro Equations Solving Time", performanceMetrics[metric], "Second")
            
            metric="Total"
            if metric in performanceMetrics:parser.set_statistic("Total Time Spent in Cycles", performanceMetrics[metric], "Second")
            
        j+=1
    
    if __name__ == "__main__":
        #output for testing purpose
        print(("parsing complete:",parser.parsing_complete()))
        parser.print_params_stats_as_must_have()
        print((parser.get_xml()))
    
    #return complete XML overwize return None
    return parser.get_xml()
    
    
if __name__ == "__main__":
    """stand alone testing"""
    jobdir=sys.argv[1]
    print(("Proccessing Output From",jobdir))
    processAppKerOutput(appstdout=os.path.join(jobdir,"appstdout"),geninfo=os.path.join(jobdir,"gen.info"))
    
    

