#!/bin/bash
# pass all the arguments into it

run_ior=false
run_appsigcheck=false
run_mdtest=false
run_appsig_ior=false
run_appsig_mdtest=false

proc=8

host_file_path=""

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
		--proc)
			shift
			proc=$1
			;;
		--host-file-path)
			shift
			host_file_path=$1
			;;
                *)
                        echo "unrecognized argument, continuing"
                        break
                        ;;
        esac
        shift
done

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

#export I_MPI_DEBUG=5


if [[ "${run_ior}" == "true" ]]; then
        echo "Running IOR"
        ${MPI_DIR}/mpiexec -n ${proc} ${IOR_EXE_PATH} "$@"
	wait
fi

if [[ "${run_mdtest}" == "true" ]]; then
	echo "Running Mdtest"
	${MPI_DIR}/mpirun ${MDTEST_EXE_PATH} "$@"
	wait
fi


