import sys
import json
import os
import inspect
import tarfile
import shutil
import re

from src.util import logging as log
import fnmatch

# DEFINE: the directory that this script currently livese in.
cur_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(os.path.join(cur_dir,"src"))
import akrrversion

    

build_dir=os.path.join(cur_dir,'build')


include_files={
                "items": [
                    "3rd_party/",
                    "appker_repo/",
                    "bin/",                   
                    "cfg/",
                    "setup/",
                    "src/",
                    "data/",
                    "comptasks/",
                    "docs"
                ],
                "filters": (
                    "bin/getkeys.sh",
                    "cfg/install.conf",
                    "cfg/akrr.inp.py",
                    "cfg/resources/*",
                    "cfg/server.pem",
                    "src/rest_cli.py",
                    "appker_repo/execs",
                    "appker_repo/inputs",
                    '*.pyc'
                )
            }

def copy_to_arch(arch_dir):
    "copy file to archives using dirs and filter from include_files"
    src_dir=cur_dir
    #set filters
    filter={}
    filter_all=[]
    
    filter_tmp={}
    for f in include_files['filters']:
        s=f.strip('/').split('/')
        if len(s)==1:
            filter_all.append(s[0])
        else:
            d="/".join(s[:-1])
            if d not in filter_tmp:filter_tmp[d]=[]
            filter_tmp[d].append(s[-1])
    for k,v in filter_tmp.iteritems():
        filter[os.path.abspath(os.path.join(src_dir,k))]=filter_tmp[k]+filter_all
    
    
    def my_ignore(dir, files):
        "creates ignore list for specific directory"
        absdir=os.path.abspath(dir)
        m_filter=None
        if absdir in filter:
            m_filter=filter[absdir]
        else:
            m_filter=filter_all
        
        ingore_list=[]
        for f in os.listdir(absdir):
            for i in m_filter:
               if fnmatch.fnmatch(f,i):
                    ingore_list.append(f)
                    break
        return ingore_list
    
    #copy files
    for item in include_files["items"]:
        if os.path.isdir(os.path.join(cur_dir,item)):
            #os.mkdir(os.path.join(arch_dir,item))
            shutil.copytree(os.path.join(cur_dir,item),os.path.join(arch_dir,item),ignore = my_ignore)
                            #shutil.ignore_patterns(*include_files["filters"]))
        elif os.path.isfile(os.path.join(cur_dir,item)):
            shutil.copy(os.path.join(cur_dir,item),os.path.join(arch_dir,item))
        else:
            if item[-1]=='/':
                os.mkdir(os.path.join(arch_dir,item))
   
def make_sample_app_inp(arch_dir):
    "makes sample from app ker inputs"
    log.info("makes sample from app ker inputs and removing XSEDE specific runScript")
    dir=os.path.join(arch_dir,"cfg","apps")
    for f in os.listdir(dir):
        if f=="test.app.inp.py":continue
        
        if fnmatch.fnmatch(f,"*.app.inp.py"):
            newname=f.replace(".app.inp.py",".example.inp.py")
            shutil.copy(os.path.join(dir,f),os.path.join(dir,newname))
            
            #new remove all runScript
            fin=open(os.path.join(dir,newname),"r")
            lines=fin.readlines()
            fin.close()
            
            fout=open(os.path.join(dir,f),"w")
            for l in lines:           
                m=re.match("runScript\[\s*['\"](.*)['\"]\s*\]\s*=",l)
                if m:
                    #print "="*80
                    if m.groups()[0]!='default':
                        break
                fout.write(l)
            fout.close()
            
    
        
def package(archname):
    arch_dir=os.path.join(build_dir,archname)
    src_dir=cur_dir
    arch_file=arch_dir+"-"+akrrversion.akrrversion+".tar.gz"
    log.info("Archiving directory: {}",arch_dir)
    
    if not os.path.isdir(build_dir):
        os.mkdir(build_dir)
    if os.path.exists(arch_file):
        os.remove(arch_file)
    
    if os.path.isdir(arch_dir):
        print "remove packaging directory first: rm",arch_dir
        shutil.rmtree(arch_dir)
        #exit()
    
    os.mkdir(arch_dir)
    
    copy_to_arch(arch_dir)
    
    
    #now compressw
    log.info("Compressing!")
    tar = tarfile.open(arch_file, "w:gz")
    tar.add(arch_dir,arcname=archname)
    tar.close()
    log.info("Packaging complete! "+arch_file)

if __name__ == '__main__':
    
    package('akrr')
    
