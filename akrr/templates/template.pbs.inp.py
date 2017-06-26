#Resource parameters

#Processors (cores) per node
ppn = 8

#head node for remote access
remoteAccessNode = "headnode.somewhere.org"
#Remote access method to the resource (default ssh)
remoteAccessMethod = "ssh"
#Remote copy method to the resource (default scp)
remoteCopyMethod="scp"

#Access authentication
sshUserName = "username"
sshPassword = "not recommended"
sshPrivateKeyFile = "/home/xdtas/.ssh/id_dsa"
sshPrivateKeyPassword="passphrase"

#Scratch visible across all nodes (absolute path or/and shell environment variable)
networkScratch="/scratch/akrrdata"
#Local scratch only locally visible (absolute path or/and shell environment variable)
localScratch="/tmp"
#Locations for app. kernels working directories (can or even should be on scratch space)
akrrData="/scratch/akrrdata"
#Location of executables and input for app. kernels
appKerDir="/home/username/appker/resource"

#batch options
batchScheduler = "pbs"

#job script header
batchJobHeaderTemplate="""#!/bin/bash
#PBS -l nodes={akrrNNodes}:ppn={akrrPPN}:native
#PBS -m n
#PBS -q normal
#PBS -S /bin/sh
#PBS -e stderr
#PBS -o stdout
#PBS -l walltime={akrrWallTimeLimit}
#PBS -W x=NACCESSPOLICY:SINGLEJOB
#PBS -u xdtas
#PBS -A ACCOUNT10
"""



