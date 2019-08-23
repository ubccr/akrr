#/bin/bash
# extra bc this supposedly also works with hdf5 and all that
run_ior=false;
ior_appsig=false;

run_mdtest=false;
mdtest_appsig=false;
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$LIB_DIR:/opt/intel/impi/2018.3.222/lib64

# goes through each case (2 arguments)
while [[ "$1" != "" ]]; do
	case $1 in
		--run-ior)
			run_ior=true
			;;
		--run-mdtest)
			run_mdtest=true
			;;
		--ior-appsig)
			ior_appsig=true
			;;
		--mdtest-appsig)
			mdtest_appsig=true
			;;
		*)
			echo "unrecognized argument, continuing"
			break
			;;
	esac
	shift
done

if [[ "${ior_appsig}" == "true" ]]; then
	echo "Running IOR appsigcheck..."
	${EXECS_LOC}/bin/appsigcheck.sh ${IOR_EXE_PATH}
	wait
fi

if [[ "${run_ior}" == "true" ]]; then
	echo "Running IOR"
	${IOR_EXE_PATH} $@
	wait
fi

if [[ "${mdtest_appsig}" == "true" ]]; then
        echo "Running MDTEST appsigcheck..."
        ${EXECS_LOC}/bin/appsigcheck.sh ${MDTEST_EXE_PATH}
        wait
fi

if [[ "${run_mdtest}" == "true" ]]; then
        echo "Running MDTEST"
        ${MDTEST_EXE_PATH} $@
        wait
fi


echo "done"






