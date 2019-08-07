#!/bin/bash

run_ior=false;
run_appsigcheck=false;

# goes through each case (2 arguments)
while [[ "$1" != "" ]]; do
	case $1 in
		--mdtest-run)
			run_ior=true
			;;
		--appsigcheck*)
			run_appsigcheck=true;
			;;
		*)
			echo "unrecognized argument, continuing"
			break
			;;
	esac
	shift
done

if [[ "${run_appsigcheck}" == "true" ]]; then
	echo "Running appsigcheck..."
	${EXECS_LOC}/bin/appsigcheck.sh ${MDTEST_EXE_PATH}
	wait
fi

if [[ "${run_ior}" == "true" ]]; then
	echo "Running MDTEST"
	${MPI_LOC}/mpirun ${MDTEST_EXE_PATH} "$@"
	wait
fi
echo "done"






