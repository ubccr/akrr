import os
import sys
import re
import subprocess
from . import log

import akrr.pexpect as pexpect

def run_cmd_getoutput(cmd):
    return subprocess.check_output(cmd,stderr=subprocess.STDOUT,shell=True).decode('utf-8')

def print_importent_env():
    msg="Some environment values:\n"
    
    #which akrr
    try:
        which_akrr=run_cmd_getoutput("which akrr").strip()
        msg=msg+"\twhich akrr: "+str(which_akrr)+"\n"
    except:
        msg=msg+"\twhich akrr: None\n"
    #which python3
    which_python3=run_cmd_getoutput("which python3").strip()
    msg=msg+"\twhich python3: "+str(which_python3)+"\n"
    #AKRR_CONF
    akrr_cfg=os.getenv("AKRR_CONF")
    msg=msg+"\tAKRR_CONF: "+str(akrr_cfg)+"\n"
    
    log.info(msg)



regcolorremove = re.compile("\033\[[0-9;]+m") 
def ClearOutputText(s):
    "remove special symbols"
    if s == None: return None
    replacements = {
        '\u2018': "'",
        '\u2019': "'"
    }
    for src, dest in replacements.items():
        s = s.replace(src, dest)
    s=regcolorremove.sub('',s)
    return s
    
class ShellSpawn(pexpect.spawn):
    def __init__(self, command, args=[], timeout=5, maxread=2000,
                 searchwindowsize=None, logfile=None, cwd=None, env=None,
                 ignore_sighup=False, echo=True, preexec_fn=None,
                 encoding='utf-8', codec_errors='strict', dimensions=None,
                 use_poll=False):
        "difference is that encoding='utf-8' and timeout=5"
        super(ShellSpawn, self).__init__(command, args=args, timeout=timeout, maxread=maxread, searchwindowsize=searchwindowsize, logfile=logfile, cwd=cwd, env=env, ignore_sighup=ignore_sighup, echo=echo, preexec_fn=preexec_fn, encoding=encoding, codec_errors=codec_errors, dimensions=dimensions)
    
    def runcmd(self,cmd,clearSpecialSymbols=True,printOutput=False, addAfter=False):
        
        self.sendline(cmd)
        self.expect(self.prompt)
        self.lastcmd=cmd+"\n"
        output=self.getCmdOutput(clearSpecialSymbols=clearSpecialSymbols,addAfter=addAfter,replaceCMD=False)
        if hasattr(self, 'output'):self.output+=output
        if printOutput:
            if self.echo:
                log.info(output)
            else:
                log.info("command: `{}` output: \n{}".format(cmd,output))
            sys.stdout.flush()
        else:
            if self.echo:
                log.debug2(output)
            else:
                log.debug2("command: `{}` output: \n{}".format(cmd,output))
            sys.stdout.flush()
        return output
    
    def getPromptBefore(self,clearSpecialSymbols=False, addAfter=False):
        s=self.prompt+" "+self.before
        if addAfter and isinstance(self.after, str):
            s+=self.after
        s=s.replace("\r",'')
        if clearSpecialSymbols:
            return ClearOutputText(s)
        else:
            return s
    def getCmdOutput(self,clearSpecialSymbols=True, addAfter=False,replaceCMD=True):
        s=self.before
        if addAfter and isinstance(self.after, str):
            s+=self.after
        s=s.replace("\r",'')
        if replaceCMD:
            s=s.replace(self.lastcmd,'',1)
        if clearSpecialSymbols:
            return ClearOutputText(s)
        else:
            return s
    def justExpect(self,pattern,timeoutMessage="EOF or TIMEOUT",replaceCMD=False,addAfter=True,**kwargs):
        """custom expect helper.
        It added EOF and TIMEOUT patterns and raise excemption with timeoutMessage message in match case. 
        It also print to stdout the output if verbosity>=3.
        If a pattern is list return index of match
        If pattern is not list return output cleared from special symbols"""
        
        p=[pexpect.EOF, pexpect.TIMEOUT]
        if type(pattern) is list:
            p+=pattern
        else:
            p.append(pattern)
        imatch=self.expect(p,**kwargs)
        output=self.getCmdOutput(clearSpecialSymbols=False,addAfter=addAfter,replaceCMD=False)
        if hasattr(self, 'output'):self.output+=output
        log.debug(output)
        if imatch==0 or imatch==1:
            msg=timeoutMessage
            if hasattr(self, 'timeoutMessage') and timeoutMessage=="EOF or TIMEOUT":
                msg=self.timeoutMessage
            raise Exception(msg)
        
        if type(pattern) is list:
            return imatch-2
        else:
            return self.getCmdOutput(clearSpecialSymbols=True, addAfter=addAfter,replaceCMD=replaceCMD)
        
    def sendlineExpect(self,cmd,pattern,timeoutMessage="EOF or TIMEOUT",replaceCMD=True,addAfter=True,**kwargs):
        """custom expect helper.
        It added EOF and TIMEOUT patterns and raise excemption with timeoutMessage message in match case. 
        It also print to stdout the output if verbosity>=3.
        If a pattern is list return index of match
        If pattern is not list return output cleared from special symbols"""
        self.lastcmd=cmd+"\n"
        self.sendline(cmd)
        
        p=[pexpect.EOF, pexpect.TIMEOUT]
        if type(pattern) is list:
            p+=pattern
        else:
            p.append(pattern)
        imatch=self.expect(p,**kwargs)
        output=self.getCmdOutput(clearSpecialSymbols=False,addAfter=addAfter,replaceCMD=False)
        if hasattr(self, 'output'):self.output+=output
        log.debug(output)
        if imatch==0 or imatch==1:
            msg=timeoutMessage
            if hasattr(self, 'timeoutMessage') and timeoutMessage=="EOF or TIMEOUT":
                msg=self.timeoutMessage
            raise Exception(msg)
        
        if type(pattern) is list:
            return imatch-2
        else:
            return self.getCmdOutput(clearSpecialSymbols=True, addAfter=addAfter,replaceCMD=replaceCMD)
    
    def expectSendline(self,pattern,cmd,timeoutMessage="EOF or TIMEOUT",replaceCMD=True,addAfter=True,**kwargs):
        """custom expect helper.
        It added EOF and TIMEOUT patterns and raise excemption with timeoutMessage message in match case. 
        It also print to stdout the output if verbosity>=3.
        If a pattern is list return index of match
        If pattern is not list return output cleared from special symbols"""
        
        p=[pexpect.EOF, pexpect.TIMEOUT]
        if type(pattern) is list:
            p+=pattern
        else:
            p.append(pattern)
        imatch=self.expect(p,**kwargs)
        output=self.getCmdOutput(clearSpecialSymbols=False,addAfter=addAfter,replaceCMD=False)
        if hasattr(self, 'output'):self.output+=output
        log.debug(output)
        if imatch==0 or imatch==1:
            msg=timeoutMessage
            if hasattr(self, 'timeoutMessage') and timeoutMessage=="EOF or TIMEOUT":
                msg=self.timeoutMessage
            raise Exception(msg)
        
        self.lastcmd=cmd+"\n"
        self.sendline(cmd)
        
        if type(pattern) is list:
            return imatch-2
        else:
            return self.getCmdOutput(clearSpecialSymbols=True, addAfter=addAfter,replaceCMD=replaceCMD)
    def startcmd(self,cmd):
        self.lastcmd=cmd+"\n"
        self.sendline(cmd)

def get_bash(prompt="FancyPrompt123",set_env_from_parant=True):
    "start bash interactive session"
    bash = ShellSpawn('bash')
    bash.prompt=prompt
    
    bash.sendline(' export PS1="{}"'.format(prompt))
    #bash.sendline('echo abra_cadabra_and_vualla')
    #prompt from input
    bash.expect(prompt)
    #prompt from input echo
    bash.expect(prompt)
    #prompt from new prompt
    try:
        #in some terminals there is no echo
        bash.expect(prompt,timeout=0.5)
    except:
        pass
    #set PATH if asked
    if set_env_from_parant:
        bash.runcmd(
            'export PATH="{}"'.format(
                os.getenv('PATH','/usr/local/bin:/usr/local/sbin:/usr/bin:/usr/sbin:/bin:/sbin')),
            printOutput=False)
        bash.runcmd('export LD_LIBRARY_PATH="{}"'.format(os.getenv('LD_LIBRARY_PATH','')),printOutput=False)
    
    return bash





