#!/bin/bash
# pass all the arguments into it

run_ior=false
run_appsigcheck=false
run_mdtest=false
run_appsig_ior=false
run_appsig_mdtest=false

# gets the number of cores of this machine automatically
echo "Checking number of cores to determine number of processes to run"
cpu_cores="$(grep ^cpu\\scores /proc/cpuinfo | uniq |  awk '{print $4}')"
if [[ "${cpu_cores}" == "1" ]]; then
        echo "Detected only one core. Counting processors instead"
        cpu_cores="$(grep "processor" /proc/cpuinfo | wc -l)"
fi

echo "Number of processes set: ${cpu_cores}"

proc=8

host_file_path=""

# help text essentially
usage()
{
        echo "usage: setup_hpcc_inputs.sh [-h] [-i] [--norun] [-n NODES] [-ppn PROC_PER_NODE] [--pin]"
        echo "None are required."
        echo ""
        echo " Options:"
        echo "  -h | --help                     Display help text"
        echo "  -v | --verbose                  increase verbosity of output (does a set -x)"
        echo "  -i | --interactive              Start a bash session after the run (need to also do -it after docker run)"
        echo "  --norun                         Set if you don't want to immediately run hpcc "
        echo "  -n NODES | --nodes NODES        Specify number of nodes hpcc will be running on"
        echo "  -ppn PROC_PER_NODE | "
        echo "  --proc_per_node PROC_PER_NODE   Specify nymber of processes/cores per node" 
        echo "                                  (if not specified, number of cpu cores is used,"
        echo "                                  as found in /proc/cpuinfo)"
        echo "  --pin                           Turn on process pinning for mpi (I_MPI_PIN)"
        echo "  -d DEBUG_LEVEL | "
        echo "  --debug DEBUG_LEVEL             Set the mpi debug level to the given value (0-5+, default 0)"
	echo " --run-ior			Runs the ior executable at the end"
	echo " --run-mdtest			Runs the mdtest executable at the end"
	echo " --ior-appsig			Runs the ior appsigcheck"
	echo " --mdtest-appsig			Runs the mdtest appsigcheck"
} 


# setting default values for variables
set_defaults()
{
        nodes=1
        ppn=${cpu_cores}
        verbose=false
        interactive=false
        run_hpcc=true
        I_MPI_PIN=0
        I_MPI_DEBUG=0
}

set_defaults
# so you have to specify --ior-run to actually run the thing, and you can use the appsigcheck flag to run the signature thing
# only goes through until it gets something that it doesn't recognize (regular argument)
while [[ "$1" != "" ]]; do
        case $1 in
                --run-ior)
                        run_ior=true
                        ;;
		--run-mdtest)
			run_mdtest=true
			;;
                --ior-appsig)
                        run_appsig_ior=true;
                        ;;
		--mdtest-appsig)
			run_appsig_mdtest=true;
			;;
		--host-file-path)
			shift
			host_file_path=$1
			;;
                -h | --help)
                        usage
                        exit
                        ;;
                -v | --verbose)
                        echo "Verbose arg detected, running set -x after arg processing"
                        verbose=true
                        ;;
                -i | --interactive)
                        echo "Interactive arg detected, starting bash session at end of script"
                        interactive=true
                        ;;
                --norun)
                        echo "Norun arg detected, will not run hpcc executable"
                        run_hpcc=false
                        ;;
                -n | --nodes)
                        echo "Nodes arg detected. Purely used to determine hpcc input file"
                        echo "Using the docker image assumes you're working on one node"
                        shift
                        nodes=${1}
                        ;;
                -ppn | --proc_per_node)
                        echo "Processes Per Node arg detected, overwriting previous processes value found from looking at number of cores"
                        shift
                        ppn=${1}
                        ;;
                --pin)
                        echo "Pin arg detected, setting I_MPI_PIN to 1"
                        I_MPI_PIN=1
                        ;;
                -d | --debug)
                        echo "Debug arg detected, setting I_MPI_DEBUG to value after it"
                        shift
                        I_MPI_DEBUG=${1}
                        ;;
                *)
                        echo "unrecognized argument, continuing"
                        break
                        ;;
        esac
        shift # to go to next argument
done

if [[ "${verbose}" == "true" ]]; then
        set -x
fi
   
export I_MPI_DEBUG
export I_MPI_PIN

if [[ "${run_appsig_ior}" == "true" ]]; then
        echo "Running appsigcheck..."
        ${EXECS_DIR}/bin/appsigcheck.sh ${IOR_EXE_PATH}
        wait
fi

if [[ "${run_appsig_mdtest}" == "true" ]]; then
        echo "Running appsigcheck..."
        ${EXECS_DIR}/bin/appsigcheck.sh ${MDTEST_EXE_PATH}
        wait
fi

if [[ "${run_ior}" == "true" ]]; then
        echo "Running IOR"
        ${MPI_DIR}/mpiexec -n ${ppn} ${IOR_EXE_PATH} "$@"
	wait
fi

if [[ "${run_mdtest}" == "true" ]]; then
	echo "Running Mdtest"
	${MPI_DIR}/mpirun -n ${ppn} ${MDTEST_EXE_PATH} "$@"
	wait
fi

# if user sets interactive flag, starts up bash at end
if [[ "${interactive}" == "true" ]]; then
        echo "Launching /bin/bash"
        /bin/bash
fi

