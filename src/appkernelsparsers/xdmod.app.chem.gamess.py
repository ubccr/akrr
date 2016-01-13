import re
import os
import sys
import time

#Set proper path for stand alone test runs
if __name__ == "__main__":
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),'../../src'))

import akrrappkeroutputparser
from akrrappkeroutputparser import AppKerOutputParser,total_seconds

def processAppKerOutput(appstdout=None,stdout=None,stderr=None,geninfo=None,appKerNResVars=None):
    #set App Kernel Description
    parser=AppKerOutputParser(
        name             = 'xdmod.app.chem.gamess',
        version          = 1,
        description      = "Gamess: General Atomic and Molecular Electronic Structure System",
        url              = 'http://www.msg.ameslab.gov',
        measurement_name = 'Gamess'
    )
    #set obligatory parameters and statistics
    #set common parameters and statistics
    parser.setCommonMustHaveParsAndStats()
    #set app kernel custom sets  
    parser.setMustHaveParameter('App:Version')
    
    parser.setMustHaveStatistic('Wall Clock Time')
    parser.setMustHaveStatistic('User Time')
    parser.setMustHaveStatistic('Time Spent in MP2 Energy Calculation')
    parser.setMustHaveStatistic('Time Spent in Restricted Hartree-Fock Calculation')
    #parse common parameters and statistics
    parser.parseCommonParsAndStats(appstdout,stdout,stderr,geninfo)
    
    #read output
    lines=[]
    if os.path.isfile(appstdout):
        fin=open(appstdout,"rt")
        lines=fin.readlines()
        fin.close()
    
    #process the output
    startTime=None
    endTime=None
    MP2EnergyCalculationTime=0.0
    RHFCalculationTime=0.0
    efficiency=None
    j=0
    while j<len(lines):
       
       m=re.search(r'GAMESS VERSION = ([^*]+)',lines[j])
       if m:parser.setParameter("App:Version",m.group(1).strip())
       
       m=re.search(r'PARALLEL VERSION RUNNING ON\s*([\d\.]+) PROCESSORS IN\s*([\d\.]+) NODE',lines[j])
       if m:
           parser.setParameter("App:NCores",m.group(1).strip())
           parser.setParameter("App:NNodes",m.group(2).strip())
       
       m=re.search(r'EXECUTION OF GAMESS BEGUN (.+)',lines[j])
       if m:startTime=parser.getDateTimeLocal(m.group(1).strip())
       
       m=re.search(r'EXECUTION OF GAMESS TERMINATED NORMALLY (.+)',lines[j])
       if m:endTime=parser.getDateTimeLocal(m.group(1).strip())
       
       if re.search(r'DONE WITH MP2 ENERGY',lines[j]):
           j+=1
           m=re.search(r'STEP CPU TIME=\s*([\d\.]+)',lines[j])
           if m:MP2EnergyCalculationTime+=float(m.group(1).strip())
           
       if re.search(r'END OF RHF CALCULATION',lines[j]):
           j+=1
           m=re.search(r'STEP CPU TIME=\s*([\d\.]+)',lines[j])
           if m:RHFCalculationTime+=float(m.group(1).strip())
       
       m=re.search(r'TOTAL WALL CLOCK TIME.+CPU UTILIZATION IS\s+([\d\.]+)',lines[j])
       if m:efficiency=float(m.group(1).strip())  
       
       j+=1
    
    if startTime and endTime:
        wallTime=total_seconds(endTime-startTime)
        if wallTime >= 0.0:
            parser.setStatistic('Wall Clock Time', str(wallTime), "Second" )
            if efficiency:
                parser.setStatistic( "User Time", str((0.01 * efficiency * wallTime)), "Second" )
    
    parser.setStatistic("Time Spent in MP2 Energy Calculation", str(MP2EnergyCalculationTime), "Second" )
    parser.setStatistic("Time Spent in Restricted Hartree-Fock Calculation", str(RHFCalculationTime),"Second" )
    
    if "attemptsToLaunch" in parser.geninfo:
        parser.setStatistic("Attempts to Launch", parser.geninfo['attemptsToLaunch'] )
    else:
        parser.setStatistic("Attempts to Launch", 1 )
    
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
    
    

