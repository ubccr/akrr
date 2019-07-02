#!/bin/bash
# pass all the arguments into it

run_ior=false
run_appsigcheck=false

proc=8

# so you have to specify --ior-run to actually run the thing, and you can use the appsigcheck flag to run the signature thing
# only goes through until it gets something that it doesn't recognize (regular argument)
while [[ "$1" != "" ]]; do
        case $1 in
                --ior-run)
                        run_ior=true
                        ;;
                --appsigcheck*)
                        run_appsigcheck=true;
                        ;;
		--proc)
			shift
			proc=$1
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
        ${EXECS_LOC}/bin/appsigcheck.sh ${IOR_EXE_PATH}
        wait
fi

if [[ "${run_ior}" == "true" ]]; then
        echo "Running IOR"
        ${MPI_LOC}/mpiexec -n ${proc} ${IOR_EXE_PATH} "$@"
	wait
fi
