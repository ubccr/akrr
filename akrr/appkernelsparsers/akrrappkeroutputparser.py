# Part of XDMoD=>AKRR
# parser AK output processing
#
# author: Nikolay Simakov
#

import re
import os
import datetime




import xml.etree.ElementTree as ET
import xml.dom.minidom
import traceback


#add total_seconds function to datetime.timedelta if python is old
def total_seconds(d):
    return d.days*3600*24 + d.seconds + d.microseconds/1000000.0

class AppKerOutputParser:
    def __init__(self,name='',version=1, description='', url='', measurement_name=''):
        self.name=name
        self.version=version
        self.description=description
        self.url=url
        if measurement_name!='':
            self.measurement_name=measurement_name
        else:
            self.measurement_name=name
        self.parameters=[]
        self.statistics=[]
        self.mustHaveParameters=[]
        self.mustHaveStatistics=[]
        #complete 
        self.completeOnPartialMustHaveStatistics=False
        
    def setParameter(self,name,val,units=None):
        if not isinstance(val, str):
            val=str(val)
        self.parameters.append([name,val,units])
   
    def setStatistic(self,name,val,units=None):
        if not isinstance(val, str):
            val=str(val)
        self.statistics.append([name,val,units])  
        
    def getParameter(self,name):
        for p in self.parameters:
            if p[0]==name:
                return p[1]
        return None
    def getStatistic(self,name):
        for p in self.statistics:
            if p[0]==name:
                return p[1]
        return None
    
    def __str__(self):
        s=""
        s+="name: %s\n"%self.name
        s+="version: %s\n"%self.version
        s+="description: %s\n"%self.description
        s+="measurement_name: %s\n"%self.measurement_name
        
        s+="parameters:\n"
        for p in self.parameters:
            s+="\t%s: %s %s\n"%(p[0],p[1],str(p[2]))
        s+="statistics:\n"
        for p in self.statistics:
            s+="\t%s: %s %s\n"%(p[0],p[1],str(p[2]))
        
        return s
    def getUniqueParameters(self):
        r=[]
        names=[]
        for i in range(len(self.parameters)-1,-1,-1):
            if names.count(self.parameters[i][0])==0:
                r.append(self.parameters[i])
                names.append(self.parameters[i][0])
        r.sort(key=lambda x: x[0])
        return r
    def getUniqueStatistic(self):
        r=[]
        names=[]
        for i in range(len(self.statistics)-1,-1,-1):
            if names.count(self.statistics[i][0])==0:
                r.append(self.statistics[i])
                names.append(self.statistics[i][0])
        r.sort(key=lambda x: x[0])
        return r
        
    def setMustHaveParameter(self,name):
        self.mustHaveParameters.append(name)
        
    def setMustHaveStatistic(self,name):
        self.mustHaveStatistics.append(name)
        
    def setCommonMustHaveParsAndStats(self):
        self.setMustHaveParameter('App:ExeBinSignature')
        self.setMustHaveParameter('RunEnv:Nodes')
    def parseCommonParsAndStats(self,appstdout=None,stdout=None,stderr=None,geninfo=None):
        #retreave node lists and set respective parameter
        self.nodesList=""
        try:
            if geninfo!=None:
                if os.path.isfile(geninfo):
                    fin=open(geninfo,"r")
                    d=fin.read()
                    fin.close()
                    #replace old names for compatibility
                    d=d.replace('NodeList','nodeList')
                    d=d.replace('StartTime','startTime')
                    d=d.replace('EndTime','endTime')
                    d=d.replace('appKerstartTime','appKerStartTime')
                    d=d.replace('appKerendTime','appKerEndTime')
                    
                    gi=eval("{"+d+"}")
                    if 'nodeList' in gi:
                        self.nodesList=os.popen('echo "%s"|gzip -9|base64 -w 0'%(gi['nodeList'])).read()
                    if 'startTime' in gi:
                        self.startTime=self.getDateTimeLocal(gi['startTime'])
                    if 'endTime' in gi:
                        self.endTime=self.getDateTimeLocal(gi['endTime'])
                    if 'startTime' in gi and 'endTime' in gi:
                        self.wallClockTime=self.endTime-self.startTime
                    if 'appKerStartTime' in gi and 'appKerEndTime' in gi:
                        self.appKerWallClockTime=self.getDateTimeLocal(gi['appKerEndTime'])-self.getDateTimeLocal(gi['appKerStartTime'])
                        
                    self.geninfo=gi
        except:
            print "ERROR: Can not process gen.info file"
            print traceback.format_exc()
        self.setParameter("RunEnv:Nodes",self.nodesList)
        
        if appstdout!=None:
            #read output
            lines=[]
            if os.path.isfile(appstdout):
                fin=open(appstdout,"rt")
                lines=fin.readlines()
                fin.close()
            
            #process the output
            ExeBinSignature=''
            
            j=0
            while j<len(lines):
                m=re.search(r'===ExeBinSignature===(.+)',lines[j])
                if m:ExeBinSignature+=m.group(1).strip()+'\n'
                j+=1
            
            
            ExeBinSignature=os.popen('echo "%s"|gzip -9|base64 -w 0'%(ExeBinSignature)).read()
            self.setParameter("App:ExeBinSignature",ExeBinSignature)
        
        if stdout!=None:
            #read output
            lines=""
            if os.path.isfile(stdout):
                fin=open(stdout,"rt")
                lines=fin.read()
                fin.close()
            
            #process the output
            self.filesExistance={}
            self.dirAccess={}
            
            filesDesc=["App kernel executable",
                       "App kernel input",
                       "Task working directory",
                       "Network scratch directory",
                       "local scratch directory"]
            dirsDesc=["Task working directory",
                       "Network scratch directory",
                       "local scratch directory"]
            
            for dirDesc in dirsDesc:
                m=re.search(r'AKRR:ERROR: '+dirDesc+' is not writable',lines)
                if m:self.dirAccess[dirDesc]=False
                else:self.dirAccess[dirDesc]=True
            
            for fileDesc in filesDesc:
                m=re.search(r'AKRR:ERROR: '+fileDesc+' does not exists',lines)
                if m:
                    self.filesExistance[fileDesc]=False
                    if fileDesc in dirsDesc:
                        self.dirAccess[dirDesc]=False
                else:
                    self.filesExistance[fileDesc]=True
                
            
            
            
            
            print lines
            print self.filesExistance
            print self.dirAccess

    def parsingComplete(self,Verbose=False):
        """i.e. app output was having all mandatory parameters and statistics"""
        complete=True
        
        p=[]
        for v in self.parameters:p.append(v[0])
        for v in self.mustHaveParameters:
            if p.count(v)==0:
                if Verbose: print "Must have parameter, %s, is not present"%(v,)
                complete=False
        p=[]
        for v in self.statistics:p.append(v[0])
        for v in self.mustHaveStatistics:
            if p.count(v)==0:
                if Verbose: print "Must have statistic, %s, is not present"%(v,)
                complete=False
        if self.completeOnPartialMustHaveStatistics and complete==False:
            
            if 'Number of Tests Passed' in self.mustHaveStatistics and 'Number of Tests Started' in self.mustHaveStatistics:
                if   self.getStatistic('Number of Tests Passed')==None or self.getStatistic('Number of Tests Started')==None :
                    complete=False
                else:
                    if self.getStatistic('Number of Tests Passed')>0:
                        complete=True
            else:
                complete=True
        
        return complete
    def getXML(self):
        root=ET.Element('rep:report')
        root.attrib['xmlns:rep']='report'
        body = ET.SubElement(root,'body')
        performance = ET.SubElement(body,'performance')
        performanceID = ET.SubElement(performance, 'ID')
        performanceID.text=self.measurement_name
        benchmark = ET.SubElement(performance, 'benchmark')
        benchmarkID = ET.SubElement(benchmark, 'ID')
        benchmarkID.text=self.measurement_name
        
        parameters = ET.SubElement(benchmark, 'parameters')
        pars=self.getUniqueParameters()
        for par in pars:
            e=ET.SubElement(parameters, 'parameter')
            ET.SubElement(e, 'ID').text=par[0]
            ET.SubElement(e, 'value').text=par[1]
            if par[2]:ET.SubElement(e, 'units').text=par[2]
        
        statistics = ET.SubElement(benchmark, 'statistics')
        pars=self.getUniqueStatistic()
        for par in pars:
            e=ET.SubElement(statistics, 'statistic')
            ET.SubElement(e, 'ID').text=par[0]
            ET.SubElement(e, 'value').text=par[1]
            if par[2]:ET.SubElement(e, 'units').text=par[2]
        exitStatus=ET.SubElement(root,'exitStatus')
        completed=ET.SubElement(exitStatus,'completed')
        if hasattr(self, 'successfulRun'):
            if self.parsingComplete(True) and self.successfulRun: completed.text="true"
            else: completed.text="false"
        else:
            if self.parsingComplete(True): completed.text="true"
            else: completed.text="false"
        return xml.dom.minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
        #return xml.dom.minidom.parseString(ET.tostring(root)).toprettyxml().replace("rep12345report","rep:report")#.replace("""<?xml version="1.0" ?>\n""","")
        #return "<?xml version='1.0'?>\n"+ET.tostring(root)+"\n"
    def printParsNStatsAsMustHave(self):
        """print set parameters and statistics as part of code to set them as must have"""
        pars=self.getUniqueParameters()
        for par in pars:
            print "parser.setMustHaveParameter('%s')"%(par[0],)
        print
        pars=self.getUniqueStatistic()
        for par in pars:
            print "parser.setMustHaveStatistic('%s')"%(par[0],)
    def getDateTimeLocal(self,datestr):
        """Return local datatime, will convert the other zones to local. If original datestr does not have
        zone information assuming it is already local"""
        datestrLoc=os.popen('date -d "'+datestr+'" +"%a %b %d %H:%M:%S %Y"').read().strip()
        r=datetime.datetime.strptime(datestrLoc,"%a %b %d %H:%M:%S %Y")
        return r

def testParser(jobdir,processAppKerOutput):
    import akrr.akrrtask
    taskHandler=akrr.akrrtask.akrrGetTaskHandlerFromJobDir(jobdir)
    if taskHandler!=None:
        appKerNResVars={}
        appKerNResVars['resource']=taskHandler.resource
        appKerNResVars['resource'].update(taskHandler.resourceParam)
        appKerNResVars['app']=taskHandler.app
        appKerNResVars['app'].update(taskHandler.appParam)
    else:
        appKerNResVars=None
    
    processAppKerOutput(appstdout=os.path.join(jobdir,"appstdout"),geninfo=os.path.join(jobdir,"gen.info"),appKerNResVars=appKerNResVars)
