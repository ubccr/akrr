import re
import os
import sys

#Set proper path for stand alone test runs
if __name__ == "__main__":
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),'../../src'))

import akrrappkeroutputparser
from akrrappkeroutputparser import AppKerOutputParser

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
    parser.setCommonMustHaveParsAndStats()
    #set app kernel custom sets  
    parser.setMustHaveParameter('App:Version')
    parser.setMustHaveStatistic('Wall Clock Time')
    
    #parse common parameters and statistics
    parser.parseCommonParsAndStats(appstdout,stdout,stderr,geninfo)
    
    #read output
    lines=[]
    if os.path.isfile(appstdout):
        fin=open(appstdout,"rt")
        lines=fin.readlines()
        fin.close()
    parser.setParameter("App:Version","unknown")
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
            parser.setParameter("App:Version","Branch:"+branch+" Revision:"+revision)

       
        m=re.match(r'^Time\s*=\s*([0-9\.]+)\s+CycleNumber\s*=\s*([0-9]+)\s+Wallclock\s*=\s*([0-9\.]+)',lines[j])
        if m:
            parser.setStatistic("Final Simulation Time", m.group(1), "Enzo Time Unit")
            parser.setStatistic("Total Cycles", m.group(2))
            parser.setStatistic("Wall Clock Time", m.group(3), "Second")
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
            if metric in performanceMetrics:parser.setStatistic("Communication Transpose Time", performanceMetrics[metric], "Second")
            
            metric="ComputePotentialFieldLevelZero"
            if metric in performanceMetrics:parser.setStatistic("Gravitational Potential Field Computing Time", performanceMetrics[metric], "Second")
            
            metric="EvolvePhotons"
            if metric in performanceMetrics:parser.setStatistic("Radiative Transfer Calculation Time", performanceMetrics[metric], "Second")
            
            metric="Group_WriteAllData"
            if metric in performanceMetrics:parser.setStatistic("All Data Group Write Time", performanceMetrics[metric], "Second")
            
            metric="Level_00"
            if metric in performanceMetrics:parser.setStatistic("All Grid Level 00 Calculation Time", performanceMetrics[metric], "Second")
            
            metric="Level_01"
            if metric in performanceMetrics:parser.setStatistic("All Grid Level 01 Calculation Time", performanceMetrics[metric], "Second")
            
            metric="Level_02"
            if metric in performanceMetrics:parser.setStatistic("All Grid Level 02 Calculation Time", performanceMetrics[metric], "Second")
            
            metric="RebuildHierarchy"
            if metric in performanceMetrics:parser.setStatistic("Grid Hierarchy Rebuilding Time", performanceMetrics[metric], "Second")
           
            metric="SetBoundaryConditions"
            if metric in performanceMetrics:parser.setStatistic("Boundary Conditions Setting Time", performanceMetrics[metric], "Second")
            
            metric="SolveForPotential"
            if metric in performanceMetrics:parser.setStatistic("Poisson Equation Solving Time", performanceMetrics[metric], "Second")
            
            metric="SolveHydroEquations"
            if metric in performanceMetrics:parser.setStatistic("Hydro Equations Solving Time", performanceMetrics[metric], "Second")
            
            metric="Total"
            if metric in performanceMetrics:parser.setStatistic("Total Time Spent in Cycles", performanceMetrics[metric], "Second")
            
        j+=1
    
    if __name__ == "__main__":
        #output for testing purpose
        print "parsing complete:",parser.parsingComplete()
        parser.printParsNStatsAsMustHave()
        print parser.getXML()
    
    #return complete XML overwize return None
    return parser.getXML()
    
    
if __name__ == "__main__":
    """stand alone testing"""
    jobdir=sys.argv[1]
    print "Proccessing Output From",jobdir
    processAppKerOutput(appstdout=os.path.join(jobdir,"appstdout"),geninfo=os.path.join(jobdir,"gen.info"))
    
    

