import unittest
import copy
from test_util import *


#add check_output fuction to subprocess module if python is old
if "check_output" not in dir( subprocess ): # duck punch it in!
    def f(*popenargs, **kwargs):
        if 'stdout' in kwargs:
            raise ValueError('stdout argument not allowed, it will be overridden.')
        process = subprocess.Popen(stdout=subprocess.PIPE, *popenargs, **kwargs)
        output, unused_err = process.communicate()
        retcode = process.poll()
        if retcode:
            cmd = kwargs.get("args")
            if cmd is None:
                cmd = popenargs[0]
            raise subprocess.CalledProcessError(retcode, cmd)
        return output
    subprocess.check_output = f

#Test parameters
akrr_tar_gz=os.path.abspath(os.path.join(akrr_arch_home, "build","akrr.tar.gz"))

default_akrr_db_user='akrruser'

class TestInstallation(TestCase):
    """Test AKRR installation process"""
    def setUp(self):
        pass
    def tearDown(self):
        if hasattr(self, 'timeoutMessage'): delattr(self, 'timeoutMessage')
    def getBash(self,setAKRRenv=False,cdToAKRR_HOME=False):
        if (not hasattr(self, 'bash')) or  self.bash==None:
            bash = ShellSpawn('bash')
            bash.sendline('export PS1="{prompt}"'.format(prompt=prompt))
            bash.expect(prompt)
            bash.expect(prompt)
            bash.prompt=prompt
            output=bash.runcmd('',printOutput=True)
            self.bash=bash
        #if verbosity>=3: print bash.before
        if setAKRRenv:
            output=self.bash.runcmd('export AKRR_HOME={akrr_home}'.format(akrr_home=cfg.akrr_home),printOutput=True)
        if cdToAKRR_HOME:
            output=self.bash.runcmd('cd $AKRR_HOME',printOutput=True)
        
        return self.bash

    def test_packager(self):
        """Testing AKRR packager"""
        if os.path.isfile(akrr_tar_gz):
            os.remove(akrr_tar_gz) 
        
        output=subprocess.check_output("""
            cd {akrr_home}
            {python_bin} akrrpackager.py
            """.format(akrr_home=akrr_arch_home,python_bin=python_bin), shell=True)
        if verbosity>=3:
            print "\n"+"~"*80
            print output
            print "~"*80
        output=ClearOutputText(output)
        #test the outcome
        self.assertNotEqual(re.search(r'\[INFO\]: Packaging complete!',output),None, "AKRR distribution archive was NOT created")
        self.assertEqual(os.path.isfile(akrr_tar_gz), True, "AKRR distribution archive was NOT created")
        self.assertEqual(os.path.getsize(akrr_tar_gz)>1024, True, "AKRR distribution archive was created, but too small to be true")
    
    def test_unpack(self):
        """Testing unpacking of AKRR distribution archive"""
        if not os.path.isfile(akrr_tar_gz):
            raise Exception("Should do test_packager first")
        
        if os.path.exists(cfg.akrr_home):
            shutil.rmtree(cfg.akrr_home)
            
        if verbosity>=3: print "\n"+"~"*80
        
        #start bash shell
        bash = self.getBash()
        
        output=bash.runcmd('tar -xvf {akrr_tar_gz} -C {above_akrr_home}'.format(akrr_tar_gz=akrr_tar_gz,above_akrr_home=os.path.abspath(os.path.join(cfg.akrr_home, ".."))),printOutput=True)
        output=bash.runcmd('export AKRR_HOME={akrr_home}'.format(akrr_home=cfg.akrr_home),printOutput=True)
        output=bash.runcmd('cd $AKRR_HOME',printOutput=True)
        output=bash.runcmd('pwd',printOutput=True)
        
        if verbosity>=3: print "~"*80
        #test some files presence
        filesToCheck=['src/akrr.py',
        'src/akrrscheduler.py']
        for f in filesToCheck:
            self.assertEqual(os.path.isfile(os.path.abspath(os.path.join(cfg.akrr_home, f))), True, "AKRR distribution archive can not be unpacked")
    def run_setup(self,
                 akrr_db_user,
                 akrr_db_passwd,
                 xd_db_user,
                 xd_db_passwd,
                 akrr_db_admin_user,
                 akrr_db_admin_passwd,
                 cron_email=None,
                 testMissmatchingPassword=False,
                 testInvalidAdministrativeDatabaseUser=False):    
        """Run Preparatory Script"""
        #start bash shell
        bash = self.getBash(setAKRRenv=True,cdToAKRR_HOME=True)
        bash.output=""
        bash.timeoutMessage='Unexpected behavior of prep.sh (premature EOF or TIMEOUT)'
        
        fasttimeout=3
        
        #start prep script
        bash.startcmd("$AKRR_HOME/setup/setup.sh")
        
        #set python
        bash.expectSendline(r'\[.*INPUT.*]: Please specify a path to the python binary you want to use:.*\n\[.*\]',
                                   '',timeout=fasttimeout)
        
        #set database user for AKRR
        bash.expectSendline(r'\[.*INPUT.*]: Please specify a database user for AKRR \(This user will be created if it does not already exist\):.*\n\[akrruser\]',
                                  '' if akrr_db_user==default_akrr_db_user else akrr_db_user,timeout=fasttimeout)
        bash.justExpect("\n")
        
        if testMissmatchingPassword:
            printNote("Entering not matching password")
            bash.expectSendline(r'\[.*INPUT.*]: Please specify a password for the AKRR database user:.*\n',
                                'password',timeout=fasttimeout)
            bash.expectSendline(r'\[.*INPUT.*]: Please reenter password:.*\n',
                                'passwordpassword',timeout=fasttimeout)
            bash.justExpect(r'\[.*ERROR.*]: Entered passwords do not match. Please try again.',timeout=fasttimeout)
            printNote("\nEntering matching password")
        bash.expectSendline(r'\[.*INPUT.*]: Please specify a password for the AKRR database user:.*\n',
                                   akrr_db_passwd,timeout=fasttimeout)
        bash.expectSendline(r'\[.*INPUT.*]: Please reenter password:.*\n',
                                   akrr_db_passwd,timeout=fasttimeout)
        
        #set XDMoD database user
        bash.expectSendline(r'\[.*INPUT.*]: Please specify the user that will be connecting to the XDMoD database \(modw\):.*\n\[akrruser\]',
                                   '' if xd_db_user==default_akrr_db_user else xd_db_user,timeout=fasttimeout)
        bash.justExpect("\n",timeout=fasttimeout)
        
        if akrr_db_user!=xd_db_user:
            if testMissmatchingPassword:
                printNote("Entering not matching password")
                bash.expectSendline(r'\[.*INPUT.*]: Please specify the password:.*\n',
                                   'xd_db_passwd',timeout=fasttimeout)
                bash.expectSendline(r'\[.*INPUT.*]: Please reenter password:.*\n',
                                   'xd_db_passwd123',timeout=fasttimeout)
                bash.justExpect(r'\[.*ERROR.*]: Entered passwords do not match. Please try again.',timeout=fasttimeout)
                printNote("\nEntering matching password")
                
            bash.expectSendline(r'\[.*INPUT.*]: Please specify the password:.*\n',
                                   xd_db_passwd,timeout=fasttimeout)
            bash.expectSendline(r'\[.*INPUT.*]: Please reenter password:.*\n',
                                   xd_db_passwd,timeout=fasttimeout)
        
        #set AKRR database root user
        if testInvalidAdministrativeDatabaseUser:
            printNote("Entering invalid administrative database user")
            bash.expectSendline(r'\[.*INPUT.*]: Please provide an administrative database user under which the installation sql script should.*\n?.*run \(This user must have privileges to create users and databases\):.*\n',
                                   "invalid",timeout=fasttimeout)
            bash.expectSendline(r'\[.*INPUT.*]: Please provide the password for the the user which you previously entered:.*\n',
                                   "invalid",timeout=fasttimeout)
            bash.justExpect(r'\[.*ERROR.*]: Entered credential is not valid. Please try again.',timeout=fasttimeout)
            printNote("\nEntering valid administrative database user")
            
        bash.expectSendline(r'\[.*INPUT.*]: Please provide an administrative database user under which the installation sql script should.*\n?.*run \(This user must have privileges to create users and databases\):.*\n',
                                   akrr_db_admin_user,timeout=fasttimeout)
        bash.expectSendline(r'\[.*INPUT.*]: Please provide the password for the the user which you previously entered:.*\n',
                                   akrr_db_admin_passwd,timeout=fasttimeout)
        
        bash.expectSendline(r'\[.*INPUT.*]: Please enter the e-mail where cron will send messages.*\n',
                            "" if cron_email==None else cron_email)
        #wait for prompt
        output=bash.justExpect(bash.prompt)
         
        delattr(bash, 'timeoutMessage')
        return copy.deepcopy(bash.output)
    def run_init_new_resource(self,
            name,
            xd_resource_id,
            ppn,
            sshUserName,
            remoteAccessNode,
            localScratch,
            networkScratch,
            akrrData,
            appKerDir,
            batchScheduler,
            authMeth=None,
            sshPassword = None,
            sshPrivateKeyFile = None,
            sshPrivateKeyPassword = None
            ):
        """Run new resource initiation script
        authMeth=None, default
              0  The private and public keys was generated manually, right now. Try again.
              1  Use existing private and public key.
              2  Generate new private and public key.
              3  Use password directly.  
        
        """
        #start bash shell
        bash = self.getBash(setAKRRenv=True,cdToAKRR_HOME=True)
        bash.output=""
        bash.timeoutMessage='Unexpected behavior of init_new_resource.sh (premature EOF or TIMEOUT)'
        
        fasttimeout=3
        slowtimeout=30
        #start prep script
        bash.startcmd("$AKRR_HOME/setup/scripts/init_new_resource.sh")
        
        bash.expectSendline(r'\[.*INPUT.*]: Enter resource_id for import \(enter 0 for no match\):.*\n',
                                   '0' if xd_resource_id==None else str(xd_resource_id),timeout=fasttimeout)
        
        bash.expectSendline(r'\[.*INPUT.*]: Enter AKRR resource name, hit enter to use same name as in XDMoD Database \[.*\]:.*\n',
                                   '' if name==None else name,timeout=fasttimeout)
        
        bash.expectSendline(r'\[.*INPUT.*]: Enter queuing system on resource \(slurm or pbs\):.*\n',
                                   '' if batchScheduler==None else batchScheduler,timeout=fasttimeout)
        
        bash.expectSendline(r'\[.*INPUT.*]: Enter Resource head node \(access node\) full name \(e.g. headnode.somewhere.org\):.*\n',
                                   '' if remoteAccessNode==None else remoteAccessNode,timeout=fasttimeout)
        
        bash.expectSendline(r'\[.*INPUT.*]: Enter username for resource access:.*\n',
                                   '' if sshUserName==None else sshUserName,timeout=fasttimeout)
        
        iMatch=bash.justExpect([r'\[.*INFO.*\]: Can access resource without password',
                         r'\[.*INFO.*\]: Can not access resource without password'],
                        timeout=fasttimeout)
        if iMatch==0:
            if authMeth!=None:
                #i.e. the test is to go throurg list
                raise Exception("Passwordless access is already set-up, but expectation is to set new access method")
        elif iMatch==1:
            #Select authentication method:
            #  0  The private and public keys was generated manually, right now. Try again.
            #  1  Use existing private and public key.
            #  2  Generate new private and public key.
            #  3  Use password directly.
            #[INPUT]: Select option from list above:
            bash.expectSendline(r'\[.*INPUT.*]: Select option from list above:.*\n\[.*\]',
                                   '' if authMeth==None else str(authMeth),timeout=fasttimeout)
            
            if authMeth==None or authMeth==2:
                bash.expectSendline(r'\[.*INPUT.*]: Enter password for.*\n',
                                   '' if sshPassword==None else str(sshPassword),timeout=fasttimeout)
                bash.expectSendline(r'\[.*INPUT.*]: Enter private key name:.*\n\[.*\]',
                                   '' if sshPrivateKeyFile==None else str(sshPrivateKeyFile),timeout=fasttimeout)
                bash.expectSendline(r'\[.*INPUT.*]: Enter passphrase for new key \(leave empty for passwordless access\):.*\n',
                                   '' if sshPrivateKeyPassword==None else str(sshPrivateKeyPassword),timeout=fasttimeout)
            elif authMeth==3:
                bash.expectSendline(r'\[.*INPUT.*]: Enter password for.*\n',
                                   '' if sshPassword==None else str(sshPassword),timeout=fasttimeout)
            elif authMeth==1:
                output=bash.justExpect(r'\[.*INPUT.*]: Select key number from list above:.*\n',timeout=fasttimeout)
                if sshPrivateKeyFile!=None:
                    pkeys={}
                    for l in output.splitlines():
                        m=re.match(r'^\s*(\d+) \s*(\S+)',l)
                        if m:
                            pkeys[m.group(2)]=m.group(1)
                    if sshPrivateKeyFile not in pkeys:
                        raise Exception("Unknown private key: "+sshPrivateKeyFile)
                    bash.startcmd(str(pkeys[sshPrivateKeyFile]))
                else:
                    bash.startcmd('0')
                
                bash.expectSendline(r'\[.*INPUT.*]: Enter password for.*\n',
                                   '' if sshPassword==None else str(sshPassword),timeout=fasttimeout)
                #sshPrivateKeyPassword
        bash.expectSendline(r'\[.*INPUT.*]: Enter processors \(cores\) per node count:.*\n',
                            '' if ppn==None else str(ppn),timeout=slowtimeout)
        
        bash.expectSendline(r'\[.*INPUT.*]: Enter location of local scratch \(visible only to single node\):.*\n\[.*\]',
                                   '' if localScratch==None else str(localScratch),timeout=fasttimeout)

        bash.expectSendline(r'\[.*INPUT.*]: Enter location of network scratch \(visible only to all nodes\), used for temporary storage of app kernel input/output:.*\n',
                                   '' if networkScratch==None else str(networkScratch),timeout=fasttimeout)
        bash.justExpect(r'\[.*INFO.*\]: Directory exist and accessible for read/write')

        bash.expectSendline(r'\[.*INPUT.*]: Enter future location of app kernels input and executable files:.*\n\[.*\]',
                                   '' if appKerDir==None else str(appKerDir),timeout=fasttimeout)
        bash.justExpect(r'\[.*INFO.*\]: Directory exist and accessible for read/write')

        bash.expectSendline(r'\[.*INPUT.*\]: Enter future locations for app kernels working directories \(can or even should be on scratch space\):.*\n\[.*\]',
                                   '' if akrrData==None else str(akrrData),timeout=fasttimeout)
        bash.justExpect(r'\[.*INFO.*\]: Directory exist and accessible for read/write')
        
        #wait for prompt
        output=bash.justExpect(bash.prompt,timeout=slowtimeout)
         
        delattr(bash, 'timeoutMessage')
        return copy.deepcopy(bash.output)
    def test_setup(self):    
        """Testing Setup Script"""
        if verbosity>=3: print "\n"+"~"*80
        
        output=ClearOutputText(self.run_setup(
            akrr_db_user=cfg.akrr_db_user,
            akrr_db_passwd=cfg.akrr_db_passwd,
            xd_db_user=cfg.xd_db_user,
            xd_db_passwd=cfg.xd_db_passwd,
            akrr_db_admin_user=cfg.akrr_db_admin_user,
            akrr_db_admin_passwd=cfg.akrr_db_admin_passwd,
            cron_email=cfg.cron_email,
            testMissmatchingPassword=True,
            testInvalidAdministrativeDatabaseUser=True
        ))
        self.patternsToHave(output,[
            r'\[INFO\]: AKRR Installed Successfully!',
            r'\[INFO\]: Generating self-signed certificate for REST-API.*writing new private key to',
            r'\[INFO\]: New self-signed certificate have been generated',
            r'\[INFO\]: Generating Settings File',
            r'\[INFO\]: Settings written to:',
            r'\[INFO\]: Removing access for group members and everybody for all files as it might contain sensitive information.',
            r'AKRR Server successfully reached the loop',
            r'\[INFO\]: Beginning check of the AKRR Rest API',
            r'\[INFO\]: REST API is up and running!',
        ],re.DOTALL)
        
        #test that DB has all tables and access is ok
        
        if verbosity>=3: print "\n"+"~"*80
    def test_new_resource(self):
        """Testing new resource installation"""
        if verbosity>=3: print "\n"+"~"*80
        for resource in cfg.new_resources:
            args=copy.deepcopy(resource)
            self.run_init_new_resource(**args)
        if verbosity>=3: print "\n"+"~"*80
def suite():
    tests = [
             #'test_packager',
             #'test_unpack',
             #'test_setup',
             'test_new_resource',
             ]

    return unittest.TestSuite(map(TestInstallation, tests))

if __name__ == '__main__':
    # TIME: to get to parsing
    parser = argparse.ArgumentParser('Test AKRR installation process')

    # SETUP: the arguments that we're going to support
    parser.add_argument('-v', '--verbosity', default=2,type=int, help="verbosity level")
    
    parser.add_argument('-clear-db', '--clear-db', action='store_true',
                        help="Clear DB only, don't test installation. ")
    parser.add_argument('-clear', '--clear', action='store_true',
                        help="Clear installation, don't install. ")
    parser.add_argument('-set-modw', '--set-modw', action='store_true',
                        help="Set fake XDMoD modw database. ")
    
    
    parser.add_argument('-install', '--install', action='store_true',
                        help="Pack archive and install, don't test. ")
    
    
    parser.add_argument('cfg', help="installation test configuration'")
    # PARSE: them arguments
    args = parser.parse_args()
    
    verbosity=args.verbosity
    testUtilSetVerbosity(verbosity)
    
    #load configuration
    loadInstallationCfg(args.cfg)
    cfg=InstallationCfg(args.cfg)
    
    dontTest=False
    
    if args.clear_db:
        print "Clean DB only, don't test installation. "
        clearInstallation(
            stopAKRR=False,
            clearBashRC=False,
            clearCronTab=False,
            clearCronTabMailTo=False,
            dropAKRR_DB=True,
            dropAKRR_DB_User=True,
            dropXD_DB=True,
            dropXD_DB_User=True,
            drop_modw_DB=True,
            rmBuildDir=False,
            rmTestAKRRHome=False
        )
        dontTest=True
    
    if args.clear:
        print "Clear installation."
        clearInstallation(
            stopAKRR=True,
            clearBashRC=True,
            clearCronTab=True,
            clearCronTabMailTo=True,
            dropAKRR_DB=True,
            dropAKRR_DB_User=True,
            dropXD_DB=True,
            dropXD_DB_User=True,
            drop_modw_DB=True,
            rmBuildDir=True,
            rmTestAKRRHome=True
        )
        dontTest=True
    if args.set_modw:
        set_modw()
    if args.install:
        print "Pack archive and install."
        tests=TestInstallation(methodName='test_packager')
        tests.test_packager()
        tests.test_unpack()
        tests.test_setup()
        dontTest=True
    #clear installation
    if 0:
        clearInstallation(
            stopAKRR=True,
            clearBashRC=True,
            clearCronTab=True,
            clearCronTabMailTo=True,
            dropAKRR_DB=True,
            dropAKRR_DB_User=True,
            dropXD_DB=True,
            dropXD_DB_User=True,
            drop_modw_DB=True,
            rmBuildDir=True,
            rmTestAKRRHome=True
        )
        set_modw()
    #run tests
    #clearInstallation(emptyResourceTables=True)
    if dontTest==False:
        unittest.TextTestRunner(verbosity=verbosity).run(suite())
    
