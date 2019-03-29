Example of appstdout from HPCG

```text
===ExeBinSignature=== MD5: 5b516c03c0fa3b890ed486faf51bca30 /util/academic/intel/18.3/compilers_and_libraries_2018.3.222/linux/mkl/benchmarks/hpcg/bin/xhpcg_skx
===ExeBinSignature=== MD5: 071ea8658daf96a77a828111b40261de /util/academic/intel/18.3/lib/intel64/libiomp5.so
===ExeBinSignature=== MD5: feab72427f8b450080810684189d30e6 /util/academic/intel/18.3/compilers_and_libraries_2018.3.222/linux/mkl/lib/intel64/libmkl_intel_lp64.so
===ExeBinSignature=== MD5: e247ad6304a22dd21b69e1203889f6df /util/academic/intel/18.3/compilers_and_libraries_2018.3.222/linux/mkl/lib/intel64/libmkl_intel_thread.so
===ExeBinSignature=== MD5: 8d910a2a99c55892275240801efe5adc /util/academic/intel/18.3/compilers_and_libraries_2018.3.222/linux/mkl/lib/intel64/libmkl_core.so
===ExeBinSignature=== MD5: ebc6518301d43233b1de262f6cfdbfcc /util/academic/intel/18.3/compilers_and_libraries_2018.3.222/linux/mpi/intel64/lib/libmpicxx.so.12
===ExeBinSignature=== MD5: 0f65391c22de4d15744ea80ec857419a /util/academic/intel/18.3/compilers_and_libraries_2018.3.222/linux/mpi/intel64/lib/libmpifort.so.12
===ExeBinSignature=== MD5: d9196e5f82db2befd02eb55c78747724 /util/academic/intel/18.3/compilers_and_libraries_2018.3.222/linux/mpi/intel64/lib/libmpi.so.12
===ExeBinSignature=== MD5: bbb4814755042554781fce1b1da6fdb1 /lib64/libdl.so.2
===ExeBinSignature=== MD5: 5928d7f9554dde0b45bc87ac09598ad0 /lib64/librt.so.1
===ExeBinSignature=== MD5: 23902bbccc0e350c1fdf09d070f3cd48 /lib64/libpthread.so.0
===ExeBinSignature=== MD5: b06038960f153e36545ed9ea947f80f6 /lib64/libstdc++.so.6
===ExeBinSignature=== MD5: 2705d15430ebce01274ef94967122bcb /lib64/libm.so.6
===ExeBinSignature=== MD5: c8f2c137eee1a4581bc0be7b63d2c603 /lib64/libgcc_s.so.1
===ExeBinSignature=== MD5: a2737e5fc2c2059bd357ef6015c99262 /lib64/libc.so.6
HPCG result is VALID with a GFLOP/s rating of 3.289080
====== n104-8p-1t-V3.0_2019.03.29.09.40.35.yaml Start ======
n104-8p-1t version: V3.0
Release date: November 11, 2015
Machine Summary: 
  Distributed Processes: 8
  Threads per processes: 1
Global Problem Dimensions: 
  Global nx: 208
  Global ny: 208
  Global nz: 208
Processor Dimensions: 
  npx: 2
  npy: 2
  npz: 2
Local Domain Dimensions: 
  nx: 104
  ny: 104
  nz: 104
########## Problem Summary  ##########: 
Setup Information: 
  Setup Time: 2.33234
Linear System Information: 
  Number of Equations: 8998912
  Number of Nonzero Terms: 240641848
Multigrid Information: 
  Number of coarse grid levels: 3
  Coarse Grids: 
    Grid Level: 1
    Number of Equations: 1124864
    Number of Nonzero Terms: 29791000
    Number of Presmoother Steps: 1
    Number of Postsmoother Steps: 1
    Grid Level: 2
    Number of Equations: 140608
    Number of Nonzero Terms: 3652264
    Number of Presmoother Steps: 1
    Number of Postsmoother Steps: 1
    Grid Level: 3
    Number of Equations: 17576
    Number of Nonzero Terms: 438976
    Number of Presmoother Steps: 1
    Number of Postsmoother Steps: 1
########## Memory Use Summary  ##########: 
Memory Use Information: 
  Total memory used for data (Gbytes): 6.43715
  Memory used for OptimizeProblem data (Gbytes): 0
  Bytes per equation (Total memory / Number of Equations): 715.326
  Memory used for linear system and CG (Gbytes): 5.66451
  Coarse Grids: 
    Grid Level: 1
    Memory used: 0.677201
    Grid Level: 2
    Memory used: 0.0848009
    Grid Level: 3
    Memory used: 0.0106403
########## V&V Testing Summary  ##########: 
Spectral Convergence Tests: 
  Result: PASSED
  Unpreconditioned: 
    Maximum iteration count: 11
    Expected iteration count: 12
  Preconditioned: 
    Maximum iteration count: 2
    Expected iteration count: 2
Departure from Symmetry |x'Ay-y'Ax|/(2*||x||*||A||*||y||)/epsilon: 
  Result: PASSED
  Departure for SpMV: 9.14792e-11
  Departure for MG: 1.82958e-10
########## Iterations Summary  ##########: 
Iteration Count Information: 
  Result: PASSED
  Reference CG iterations per set: 50
  Optimized CG iterations per set: 50
  Total number of reference iterations: 50
  Total number of optimized iterations: 50
########## Reproducibility Summary  ##########: 
Reproducibility Information: 
  Result: PASSED
  Scaled residual mean: 0.000253249
  Scaled residual variance: 0
########## Performance Summary (times in sec) ##########: 
Benchmark Time Summary: 
  Optimization phase: 2.45575
  DDOT: 0.146045
  WAXPBY: 0.157862
  SpMV: 6.83073
  MG: 33.8221
  ALL_reduce: 9.3723
  Total: 50.3291
Floating Point Operations Summary: 
  Raw DDOT: 2.71767e+09
  Raw WAXPBY: 2.71767e+09
  Raw SpMV: 2.45455e+10
  Raw MG: 1.3713e+11
  Total: 1.67111e+11
  Total with convergence overhead: 1.67111e+11
GB/s Summary: 
  Raw Read B/W: 20.456
  Raw Write B/W: 4.72735
  Raw Total B/W: 25.1834
  Total with convergence and optimization phase overhead: 24.9461
GFLOP/s Summary: 
  Raw DDOT: 18.6085
  Raw WAXPBY: 17.2155
  Raw SpMV: 3.59339
  Raw MG: 4.05446
  Raw Total: 3.32037
  Total with convergence overhead: 3.32037
  Total with convergence and optimization phase overhead: 3.28908
User Optimization Overheads: 
  Problem setup time (sec): 2.33234
  Optimization phase time (sec): 2.45575
  Optimization phase time vs reference SpMV+MG time: 1.51912
DDOT Timing Variations: 
  Min DDOT MPI_Allreduce time: 1.58
  Max DDOT MPI_Allreduce time: 9.78806
  Avg DDOT MPI_Allreduce time: 5.68243
__________ Final Summary __________: 
  HPCG result is VALID with a GFLOP/s rating of: 3.28908
      HPCG 2.4 Rating (for historical value) is: 3.30425
  Reference version of ComputeDotProduct used: Performance results are most likely suboptimal
  Results are valid but execution time (sec) is: 50.3291
       You have selected the QuickPath option: Results are official for legacy installed systems with confirmation from the HPCG Benchmark leaders.
       After confirmation please upload results from the YAML file contents to: http://hpcg-benchmark.org
====== n104-8p-1t-V3.0_2019.03.29.09.40.35.yaml End   ======
====== hpcg_log_2019.03.29.09.37.14.txt Start ======
WARNING: PERFORMING UNPRECONDITIONED ITERATIONS OPT
Call [0] Number of Iterations [11] Scaled Residual [5.85705e-14]
WARNING: PERFORMING UNPRECONDITIONED ITERATIONS OPT
Call [1] Number of Iterations [11] Scaled Residual [5.85705e-14]
Call [0] Number of Iterations [2] Scaled Residual [2.49486e-17]
Call [1] Number of Iterations [2] Scaled Residual [2.49486e-17]
Departure from symmetry (scaled) for SpMV abs(x'*A*y - y'*A*x) = 9.14792e-11
Departure from symmetry (scaled) for MG abs(x'*Minv*y - y'*Minv*x) = 1.82958e-10
SpMV call [0] Residual [0]
SpMV call [1] Residual [0]
Call [0] Scaled Residual [0.000253249]
====== hpcg_log_2019.03.29.09.37.14.txt End   ======
```