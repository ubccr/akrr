name = """xdmod.benchmark.hpcc"""
info = """HPC Challenge Benchmark suite.

http://icl.cs.utk.edu/hpcc/

It consists of 
a) High Performance LINPACK, which solves a linear system of equations and measures the floating-point performance, 
b) Parallel Matrix Transpose (PTRANS), which measures total communications capacity of the interconnect, 
c) MPI Random Access, which measures the rate of random updates of remote memory, 
d) Fast Fourier Transform, which measures the floating-point performance of double-precision complex one-dimensional Discrete Fourier Transform.

Version 1.4.1
"""

nickname = """xdmod.benchmark.hpcc.@nnodes@"""

walllimit=20

executable="execs/hpcc/hpcc"
input="inputs/hpcc/hpccinf.txt.{akrrPPN}x{akrrNNodes}"

runScriptPreRun="""#create working dir
mkdir workdir
cd workdir

#Copy inputs
cp {appKerDir}/{input} ./hpccinf.txt

#Generate AppKer signature
appsigcheck.sh {appKerDir}/{executable}
"""

runScriptPostRun="""echo "\\\"cpuSpeed\\\":\\\"\\\"\\\""`grep "cpu MHz" /proc/cpuinfo`\\\"\\\"\\\""," >> ../gen.info
mv hpccoutf.txt ../$AKRR_APP_STDOUT_FILE

#clean-up
cd ..
if [ "${{AKRR_DEBUG=no}}" = "no" ]
then
        echo "Deleting input files"
        rm -rf workdir
fi

"""

runScript={}
runScript['edge12core']="""
#Load application enviroment
. $MODULESHOME/init/sh
module purge
module load intel/13.0
module load intel-mpi/4.1.0
module list
MKLROOT=/panfs/panfs.ccr.buffalo.edu/projects/ccrstaff/general/appker/edge12core/execs/lib/mkl
source $MKLROOT/bin/mklvars.sh intel64

{runScriptPreRun}

#Execute AppKer
mpirun -n {akrrNCores} {appKerDir}/{executable}

{runScriptPostRun}
"""


#theoreticalGFlopsPerCore={
#    'edge':2.27*4, #Note that edge has two diffrent CPU types
#    'edge12core':2.4*4,
#}


#/panfs/panfs.ccr.buffalo.edu/projects/ccrstaff/general/appker/edge12core/execs/hpcc-1.4.2/hpl
#
#module load intel/13.0
#module load intel-mpi/4.1.0