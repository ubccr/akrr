import os
import shutil

import akrrcfg
import util.logging as logging

verbose=False

def app_add(resource,appkernel,verbose=False):
    globals()['verbose']=verbose
    
    logging.info("Generating application kernel configuration for %s on %s"%(appkernel,resource))
    
    try:
        akrrcfg.FindResourceByName(resource)
    except Exception:
        logging.error("Can not find resource: "+resource)
        exit(1)
    try:
        akrrcfg.FindAppByName(appkernel)
    except Exception:
        logging.error("Can not find application kernel: "+appkernel)
        exit(1)
    
    cfgFilename=os.path.join(akrrcfg.cfg_dir,'resources',resource,appkernel+".app.conf")
    cfgTemplateFilename=os.path.join(akrrcfg.templates_dir,appkernel+".app.conf")
    
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



if __name__ == '__main__':
    import argparse
    # TIME: to get to parsing
    parser = argparse.ArgumentParser('Initial configuration generation for application kernel on resource')
    # SETUP: the arguments that we're going to support
    parser.add_argument('-v', '--verbose', action='store_true', help="turn on verbose logging")
    parser.add_argument('resource', help="name of resource")
    parser.add_argument('appkernel', help="name of application kernel")
    # PARSE: them arguments
    args = parser.parse_args()
    
    app_add(args.resource,args.appkernel,verbose=args.verbose)
