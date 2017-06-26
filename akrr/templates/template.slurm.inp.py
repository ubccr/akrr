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
networkScratch="/scratch/$USER/akrrdata"
#Local scratch only locally visible (absolute path or/and shell environment variable)
localScratch="$SLURMTMPDIR"
#Locations for app. kernels working directories (can or even should be on scratch space)
akrrData="/scratch/akrrdata"
#Location of executables and input for app. kernels
appKerDir="/home/username/appker/resource"

#batch options
batchScheduler = "slurm"

#job script header
batchJobHeaderTemplate="""#!/bin/bash
#SBATCH --partition=general-compute 
#SBATCH --nodes={akrrNNodes}
#SBATCH --ntasks-per-node={akrrPPN}
#SBATCH --time={akrrWallTimeLimit}
#SBATCH --output={akrrTaskWorkingDir}/stdout
#SBATCH --error={akrrTaskWorkingDir}/stderr
#SBATCH --constraint="CPU-L5520|CPU-L5630"
#SBATCH --exclusive
"""
