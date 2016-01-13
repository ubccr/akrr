import inspect
import sys
import os
import getpass
import cStringIO
import traceback
import re
#modify python_path so that we can get /src on the path
curdir=os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
if (curdir+"/../../src") not in sys.path:
    sys.path.append(curdir+"/../../src")

try:
    import argparse
except:
    #add argparse directory to path and try again
    curdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    argparsedir=os.path.abspath(os.path.join(curdir,"..","..","3rd_party","argparse-1.3.0"))
    if argparsedir not in sys.path:sys.path.append(argparsedir)
    import argparse

import akrr
import util.logging as logging
import shutil

verbose=False

if __name__ == '__main__':
    # TIME: to get to parsing
    parser = argparse.ArgumentParser('Initial configuration generation for application kernel on resource')
    # SETUP: the arguments that we're going to support
    parser.add_argument('-v', '--verbose', action='store_true', help="turn on verbose logging")
    parser.add_argument('resource', help="name of resource")
    parser.add_argument('appkernel', help="name of application kernel")
    # PARSE: them arguments
    args = parser.parse_args()
    
    verbose=args.verbose
    resource=args.resource
    appkernel=args.appkernel
    
    logging.info("Generating application kernel configuration for %s on %s"%(appkernel,resource))
    
    try:
        akrr.FindResourceByName(resource)
    except Exception,e:
        logging.error("Can not find resource: "+resource)
        exit(1)
    try:
        akrr.FindAppByName(appkernel)
    except Exception,e:
        logging.error("Can not find application kernel: "+appkernel)
        exit(1)
    
    cfgFilename=os.path.join(akrr.akrrcfgdir,'resources',resource,appkernel+".app.inp.py")
    cfgTemplateFilename=os.path.join(akrr.curdir,'templates',appkernel+".app.inp.py")
    
    if os.path.isfile(cfgFilename):
        logging.error("Configuration file for %s on %s already exist. For regeneration delete it"%(appkernel,resource))
        print "Application kernel configuration for %s on %s is in: \n\t%s"%(appkernel,resource,cfgFilename)
        exit(1)
    
    if not os.path.isfile(cfgTemplateFilename):
        logging.error("Can not find template file for application kernel: "+cfgTemplateFilename)
        exit(1)
    
    shutil.copyfile(cfgTemplateFilename,cfgFilename)
    if os.path.isfile(cfgFilename):
        logging.info("Application kernel configuration for %s on %s is in: \n\t%s"%(appkernel,resource,cfgFilename))



