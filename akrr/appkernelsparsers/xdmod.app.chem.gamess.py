import re
import os
import sys
import time

#Set proper path for stand alone test runs
if __name__ == "__main__":
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),'../..'))

import akrr.appkernelsparsers.akrrappkeroutputparser
from akrr.appkernelsparsers.akrrappkeroutputparser import AppKerOutputParser,total_seconds

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
    parser.add_common_must_have_params_and_stats()
    #set app kernel custom sets  
    parser.add_must_have_parameter('App:Version')
    
    parser.add_must_have_statistic('Wall Clock Time')
    parser.add_must_have_statistic('User Time')
    parser.add_must_have_statistic('Time Spent in MP2 Energy Calculation')
    parser.add_must_have_statistic('Time Spent in Restricted Hartree-Fock Calculation')
    #parse common parameters and statistics
    parser.parse_common_params_and_stats(appstdout, stdout, stderr, geninfo)
    
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
       if m:parser.set_parameter("App:Version", m.group(1).strip())
       
       m=re.search(r'PARALLEL VERSION RUNNING ON\s*([\d\.]+) PROCESSORS IN\s*([\d\.]+) NODE',lines[j])
       if m:
           parser.set_parameter("App:NCores", m.group(1).strip())
           parser.set_parameter("App:NNodes", m.group(2).strip())
       
       m=re.search(r'EXECUTION OF GAMESS BEGUN (.+)',lines[j])
       if m:startTime=parser.get_datetime_local(m.group(1).strip())
       
       m=re.search(r'EXECUTION OF GAMESS TERMINATED NORMALLY (.+)',lines[j])
       if m:endTime=parser.get_datetime_local(m.group(1).strip())
       
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
            parser.set_statistic('Wall Clock Time', str(wallTime), "Second")
            if efficiency:
                parser.set_statistic("User Time", str((0.01 * efficiency * wallTime)), "Second")
    
    parser.set_statistic("Time Spent in MP2 Energy Calculation", str(MP2EnergyCalculationTime), "Second")
    parser.set_statistic("Time Spent in Restricted Hartree-Fock Calculation", str(RHFCalculationTime), "Second")
    
    if "attemptsToLaunch" in parser.geninfo:
        parser.set_statistic("Attempts to Launch", parser.geninfo['attemptsToLaunch'])
    else:
        parser.set_statistic("Attempts to Launch", 1)
    
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
    
    

