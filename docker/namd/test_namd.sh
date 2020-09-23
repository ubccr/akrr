#!/usr/bin/env bash

DIROUT=namd_out
APPKER=namd
RUN_APPKER='./namd.simg'
ALL_TARGETS='x86_64 sandybridge haswell skylake_avx512'
ALL_CONFIGS='gcc_fftw_multicore icc_mkl_multicore gcc_fftw_netlrts icc_mkl_netlrts v215_icc_mkl_multicore v215_icc_mkl_netlrts'
ALL_VIEWS='namd_prebuild_multicore'

APPKER_OPT='-e INPUT_PARAM apoa1_nve_long'

mkdir -p ${DIROUT}

for i in {1..10}
do
    for configuration in ${ALL_CONFIGS}
    do
        for target in ${ALL_TARGETS}
        do
            view=${APPKER}_${configuration}_${target}
            ${RUN_APPKER} -view ${view} ${APPKER_OPT} > ${DIROUT}/${view}_${i}.out
        done
    done
    for view in ${ALL_VIEWS}
    do
        ${RUN_APPKER} -view ${view} ${APPKER_OPT} > ${DIROUT}/${view}_${i}.out
    done

    for configuration in ${ALL_CONFIGS}
    do
        for target in ${ALL_TARGETS}
        do
            view=${APPKER}_${configuration}_${target}
            ${RUN_APPKER} -view ${view} --pin ${APPKER_OPT} > ${DIROUT}/${view}_${i}_pinned.out
        done
    done
    for view in ${ALL_VIEWS}
    do
        ${RUN_APPKER} -view ${view} --pin ${APPKER_OPT} > ${DIROUT}/${view}_${i}_pinned.out
    done
done
