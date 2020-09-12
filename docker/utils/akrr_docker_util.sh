#!/usr/bin/env bash

akrr_get_arch_target () {
    # return x86_64 sandybridge haswell skylake_avx512 based on vector instructions
    # skx is avx512f avx512dq avx512cd avx512bw avx512vl
    # knl is avx512f avx512pf avx512er avx512cd
    if [ "$(grep flags /proc/cpuinfo|head -n 1|awk '/avx512f/ && /avx512dq/ && /avx512cd/ && /avx512bw/ && /avx512vl/'|wc -l)" -eq "1" ]
    then
        echo "skylake_avx512"
    elif [ "$(grep flags /proc/cpuinfo|head -n 1|awk '/avx512f/ && /avx512pf/ && /avx512er/ && /avx512cd/'|wc -l)" -eq "1" ]
    then
        echo "mic_knl"
    elif [ "$(grep flags /proc/cpuinfo|head -n 1|grep avx2|wc -l)" -eq "1" ]
    then
        echo "haswell"
    elif [ "$(grep flags /proc/cpuinfo|head -n 1|grep avx|wc -l)" -eq "1" ]
    then
        echo "sandybridge"
    elif [ "$(grep flags /proc/cpuinfo|head -n 1|grep sse2|wc -l)" -eq "1" ]
    then
        echo "x86_64"
    else
        echo "unknown"
    fi
}

# allows script to continue if the argument passed in is a valid number
validate_number()
{
	# checking if the given argument is an integer
	re='^[0-9]+$'
	if ! [[ ${1} =~ ${re} ]] ; then
   		echo "error: ${2:-Entry} is not an integer, as expected" >&2
   		exit 1
	fi
}
