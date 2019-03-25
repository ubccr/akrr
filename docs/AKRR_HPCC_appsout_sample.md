Example of appstdout from HPCC

```text
===ExeBinSignature=== MD5: 6c2478d305a2ad108eaffd9cb1125e24 /projects/ccrstaff/general/nikolays/huey/appker/execs/hpcc-1.5.0/hpcc
===ExeBinSignature=== MD5: 23902bbccc0e350c1fdf09d070f3cd48 /lib64/libpthread.so.0
===ExeBinSignature=== MD5: 2705d15430ebce01274ef94967122bcb /lib64/libm.so.6
===ExeBinSignature=== MD5: 0f65391c22de4d15744ea80ec857419a /util/academic/intel/18.3/compilers_and_libraries_2018.3.222/linux/mpi/intel64/lib/libmpifort.so.12
===ExeBinSignature=== MD5: d9196e5f82db2befd02eb55c78747724 /util/academic/intel/18.3/compilers_and_libraries_2018.3.222/linux/mpi/intel64/lib/libmpi.so.12
===ExeBinSignature=== MD5: bbb4814755042554781fce1b1da6fdb1 /lib64/libdl.so.2
===ExeBinSignature=== MD5: 5928d7f9554dde0b45bc87ac09598ad0 /lib64/librt.so.1
===ExeBinSignature=== MD5: c8f2c137eee1a4581bc0be7b63d2c603 /lib64/libgcc_s.so.1
===ExeBinSignature=== MD5: a2737e5fc2c2059bd357ef6015c99262 /lib64/libc.so.6
########################################################################
This is the DARPA/DOE HPC Challenge Benchmark version 1.5.0 October 2012
Produced by Jack Dongarra and Piotr Luszczek
Innovative Computing Laboratory
University of Tennessee Knoxville and Oak Ridge National Laboratory

See the source files for authors of specific codes.
Compiled on Mar 25 2019 at 11:22:03
Current time (1553530013) is Mon Mar 25 12:06:53 2019

Hostname: 'cpn-d13-16.int.ccr.buffalo.edu'
########################################################################
================================================================================
HPLinpack 2.0  --  High-Performance Linpack benchmark  --   September 10, 2008
Written by A. Petitet and R. Clint Whaley,  Innovative Computing Laboratory, UTK
Modified by Piotr Luszczek, Innovative Computing Laboratory, UTK
Modified by Julien Langou, University of Colorado Denver
================================================================================

An explanation of the input/output parameters follows:
T/V    : Wall time / encoded variant.
N      : The order of the coefficient matrix A.
NB     : The partitioning blocking factor.
P      : The number of process rows.
Q      : The number of process columns.
Time   : Time in seconds to solve the linear system.
Gflops : Rate of execution for solving the linear system.

The following parameter values will be used:

N      :   28284 
NB     :     112 
PMAP   : Row-major process mapping
P      :       4 
Q      :       4 
PFACT  :   Right 
NBMIN  :       4 
NDIV   :       3 
RFACT  :   Right 
BCAST  :  2ringM 
DEPTH  :       0 
SWAP   : Mix (threshold = 64)
L1     : transposed form
U      : transposed form
EQUIL  : yes
ALIGN  : 16 double precision words

--------------------------------------------------------------------------------

- The matrix A is randomly generated for each test.
- The following scaled residual check will be computed:
      ||Ax-b||_oo / ( eps * ( || x ||_oo * || A ||_oo + || b ||_oo ) * N )
- The relative machine precision (eps) is taken to be               1.110223e-16
- Computational tests pass if scaled residuals are less than                16.0

Begin of MPIRandomAccess section.
Running on 16 processors (PowerofTwo)
Total Main table size = 2^29 = 536870912 words
PE Main table size = 2^25 = 33554432 words/PE
Default number of updates (RECOMMENDED) = 2147483648
Number of updates EXECUTED = 245540672 (for a TIME BOUND of 60.00 secs)
CPU time used = 34.393506 seconds
Real time used = 55.527851 seconds
0.004421937 Billion(10^9) Updates    per second [GUP/s]
0.000276371 Billion(10^9) Updates/PE per second [GUP/s]
Verification:  CPU time used = 1.561792 seconds
Verification:  Real time used = 1.654344 seconds
Found 0 errors in 536870912 locations (passed).
Current time (1553530076) is Mon Mar 25 12:07:56 2019

End of MPIRandomAccess section.
Begin of StarRandomAccess section.
Main table size   = 2^25 = 33554432 words
Number of updates = 134217728
CPU time used  = 4.997214 seconds
Real time used = 5.040113 seconds
0.026629903 Billion(10^9) Updates    per second [GUP/s]
Found 0 errors in 33554432 locations (passed).
Node(s) with error 0
Minimum GUP/s 0.026630
Average GUP/s 0.029518
Maximum GUP/s 0.032343
Current time (1553530086) is Mon Mar 25 12:08:06 2019

End of StarRandomAccess section.
Begin of SingleRandomAccess section.
Node(s) with error 0
Node selected 1
Single GUP/s 0.046840
Current time (1553530091) is Mon Mar 25 12:08:11 2019

End of SingleRandomAccess section.
Begin of MPIRandomAccess_LCG section.
Running on 16 processors (PowerofTwo)
Total Main table size = 2^29 = 536870912 words
PE Main table size = 2^25 = 33554432 words/PE
Default number of updates (RECOMMENDED) = 2147483648
Number of updates EXECUTED = 264677152 (for a TIME BOUND of 60.00 secs)
CPU time used = 36.820852 seconds
Real time used = 59.383913 seconds
0.004457051 Billion(10^9) Updates    per second [GUP/s]
0.000278566 Billion(10^9) Updates/PE per second [GUP/s]
Verification:  CPU time used = 1.125240 seconds
Verification:  Real time used = 1.135611 seconds
Found 0 errors in 536870912 locations (passed).
Current time (1553530157) is Mon Mar 25 12:09:17 2019

End of MPIRandomAccess_LCG section.
Begin of StarRandomAccess_LCG section.
Main table size   = 2^25 = 33554432 words
Number of updates = 134217728
CPU time used  = 5.069529 seconds
Real time used = 5.141904 seconds
0.026102730 Billion(10^9) Updates    per second [GUP/s]
Found 0 errors in 33554432 locations (passed).
Node(s) with error 0
Minimum GUP/s 0.026103
Average GUP/s 0.029722
Maximum GUP/s 0.031959
Current time (1553530167) is Mon Mar 25 12:09:27 2019

End of StarRandomAccess_LCG section.
Begin of SingleRandomAccess_LCG section.
Node(s) with error 0
Node selected 2
Single GUP/s 0.047724
Current time (1553530172) is Mon Mar 25 12:09:32 2019

End of SingleRandomAccess_LCG section.
Begin of PTRANS section.
M: 14142
N: 14142
MB: 112
NB: 112
P: 4
Q: 4
TIME   M     N    MB  NB  P   Q     TIME   CHECK   GB/s   RESID
---- ----- ----- --- --- --- --- -------- ------ -------- -----
WALL 14142 14142 112 112   4   4     0.62 PASSED    2.588  0.00
CPU  14142 14142 112 112   4   4     0.60 PASSED    2.684  0.00
WALL 14142 14142 112 112   4   4     0.64 PASSED    2.511  0.00
CPU  14142 14142 112 112   4   4     0.62 PASSED    2.592  0.00
WALL 14142 14142 112 112   4   4     0.69 PASSED    2.334  0.00
CPU  14142 14142 112 112   4   4     0.66 PASSED    2.410  0.00
WALL 14142 14142 112 112   4   4     0.63 PASSED    2.334  0.00
CPU  14142 14142 112 112   4   4     0.62 PASSED    2.598  0.00
WALL 14142 14142 112 112   4   4     0.73 PASSED    2.202  0.00
CPU  14142 14142 112 112   4   4     0.71 PASSED    2.264  0.00

Finished    5 tests, with the following results:
    5 tests completed and passed residual checks.
    0 tests completed and failed residual checks.
    0 tests skipped because of illegal input values.

END OF TESTS.
Current time (1553530188) is Mon Mar 25 12:09:48 2019

End of PTRANS section.
Begin of StarDGEMM section.
Scaled residual: 0.0109216
Node(s) with error 0
Minimum Gflop/s 8.224848
Average Gflop/s 8.453829
Maximum Gflop/s 8.549700
Current time (1553530207) is Mon Mar 25 12:10:07 2019

End of StarDGEMM section.
Begin of SingleDGEMM section.
Node(s) with error 0
Node selected 15
Single DGEMM Gflop/s 8.665557
Current time (1553530224) is Mon Mar 25 12:10:24 2019

End of SingleDGEMM section.
Begin of StarSTREAM section.
-------------------------------------------------------------
This system uses 8 bytes per DOUBLE PRECISION word.
-------------------------------------------------------------
Array size = 16666347, Offset = 0
Total memory required = 0.3725 GiB.
Each test is run 10 times.
 The *best* time for each kernel (excluding the first iteration)
 will be used to compute the reported bandwidth.
The SCALAR value used for this run is 0.420000
-------------------------------------------------------------
Your clock granularity/precision appears to be 1 microseconds.
Each test below will take on the order of 53805 microseconds.
   (= 53805 clock ticks)
Increase the size of the arrays if this shows that
you are not getting at least 20 clock ticks per test.
-------------------------------------------------------------
WARNING -- The above is only a rough guideline.
For best results, please be sure you know the
precision of your system timer.
-------------------------------------------------------------
VERBOSE: total setup time for rank 0 = 0.365038 seconds
-------------------------------------------------------------
Function      Rate (GB/s)   Avg time     Min time     Max time
Copy:           3.9271       0.0742       0.0679       0.1241
Scale:          2.6712       0.1010       0.0998       0.1049
Add:            2.9468       0.1387       0.1357       0.1585
Triad:          2.9362       0.1368       0.1362       0.1375
-------------------------------------------------------------
Solution Validates: avg error less than 1.000000e-13 on all three arrays
-------------------------------------------------------------
Node(s) with error 0
Minimum Copy GB/s 3.927148
Average Copy GB/s 3.927148
Maximum Copy GB/s 3.927148
Minimum Scale GB/s 2.671152
Average Scale GB/s 2.671152
Maximum Scale GB/s 2.671152
Minimum Add GB/s 2.946779
Average Add GB/s 2.946779
Maximum Add GB/s 2.946779
Minimum Triad GB/s 2.936196
Average Triad GB/s 2.936196
Maximum Triad GB/s 2.936196
Current time (1553530229) is Mon Mar 25 12:10:29 2019

End of StarSTREAM section.
Begin of SingleSTREAM section.
Node(s) with error 0
Node selected 5
Single STREAM Copy GB/s 8.717262
Single STREAM Scale GB/s 8.642093
Single STREAM Add GB/s 8.839621
Single STREAM Triad GB/s 9.005021
Current time (1553530231) is Mon Mar 25 12:10:31 2019

End of SingleSTREAM section.
Begin of MPIFFT section.
Number of nodes: 16
Vector size:             67108864
Generation time:     0.233
Tuning:     0.354
Computing:     0.731
Inverse FFT:     1.031
max(|x-x0|): 4.056e-15
Gflop/s:    11.934
Current time (1553530234) is Mon Mar 25 12:10:34 2019

End of MPIFFT section.
Begin of StarFFT section.
Vector size: 8388608
Generation time:     0.472
Tuning:     0.198
Computing:     0.524
Inverse FFT:     0.726
max(|x-x0|): 3.587e-15
Node(s) with error 0
Minimum Gflop/s 1.827213
Average Gflop/s 1.888649
Maximum Gflop/s 1.913160
Current time (1553530236) is Mon Mar 25 12:10:36 2019

End of StarFFT section.
Begin of SingleFFT section.
Node(s) with error 0
Node selected 13
Single FFT Gflop/s 2.935837
Current time (1553530238) is Mon Mar 25 12:10:38 2019

End of SingleFFT section.
Begin of LatencyBandwidth section.

------------------------------------------------------------------
Latency-Bandwidth-Benchmark R1.5.1 (c) HLRS, University of Stuttgart
Written by Rolf Rabenseifner, Gerrit Schulz, and Michael Speck, Germany

Details - level 2
-----------------

MPI_Wtime granularity.
Max. MPI_Wtick is 0.000001 sec
wtick is set to   0.000001 sec  

Message Length: 8
Latency   min / avg / max:   0.002190 /   0.002190 /   0.002190 msecs
Bandwidth min / avg / max:      3.652 /      3.652 /      3.652 MByte/s

MPI_Wtime granularity is ok.
message size:                                  8
max time :                             10.000000 secs
latency for msg:                        0.002190 msecs
estimation for ping pong:               0.197142 msecs
max number of ping pong pairs       =      50724
max client pings = max server pongs =        225
stride for latency                  =          1
Message Length: 8
Latency   min / avg / max:   0.000305 /   0.001297 /   0.002113 msecs
Bandwidth min / avg / max:      3.787 /     10.212 /     26.260 MByte/s

Message Length: 2000000
Latency   min / avg / max:   0.985980 /   0.985980 /   0.985980 msecs
Bandwidth min / avg / max:   2028.439 /   2028.439 /   2028.439 MByte/s

MPI_Wtime granularity is ok.
message size:                            2000000
max time :                             30.000000 secs
latency for msg:                        0.985980 msecs
estimation for ping pong:               7.887840 msecs
max number of ping pong pairs       =       3803
max client pings = max server pongs =         61
stride for latency                  =          1
Message Length: 2000000
Latency   min / avg / max:   0.231981 /   0.674685 /   1.002073 msecs
Bandwidth min / avg / max:   1995.862 /   4022.303 /   8621.385 MByte/s

Message Size:                           8 Byte
Natural Order Latency:           0.001597 msec
Natural Order Bandwidth:         5.008124 MB/s
Avg Random Order Latency:        0.001676 msec
Avg Random Order Bandwidth:      4.773516 MB/s

Message Size:                     2000000 Byte
Natural Order Latency:           1.622200 msec
Natural Order Bandwidth:      1232.893592 MB/s
Avg Random Order Latency:        2.855693 msec
Avg Random Order Bandwidth:    700.355280 MB/s

Execution time (wall clock)      =     2.655 sec on 16 processes
 - for cross ping_pong latency   =     0.072 sec
 - for cross ping_pong bandwidth =     1.397 sec
 - for ring latency              =     0.020 sec
 - for ring bandwidth            =     1.167 sec

------------------------------------------------------------------
Latency-Bandwidth-Benchmark R1.5.1 (c) HLRS, University of Stuttgart
Written by Rolf Rabenseifner, Gerrit Schulz, and Michael Speck, Germany

Major Benchmark results:
------------------------

Max Ping Pong Latency:                 0.002113 msecs
Randomly Ordered Ring Latency:         0.001676 msecs
Min Ping Pong Bandwidth:            1995.862003 MB/s
Naturally Ordered Ring Bandwidth:   1232.893592 MB/s
Randomly  Ordered Ring Bandwidth:    700.355280 MB/s

------------------------------------------------------------------

Detailed benchmark results:
Ping Pong:
Latency   min / avg / max:   0.000305 /   0.001297 /   0.002113 msecs
Bandwidth min / avg / max:   1995.862 /   4022.303 /   8621.385 MByte/s
Ring:
On naturally ordered ring: latency=      0.001597 msec, bandwidth=   1232.893592 MB/s
On randomly  ordered ring: latency=      0.001676 msec, bandwidth=    700.355280 MB/s

------------------------------------------------------------------

Benchmark conditions:
 The latency   measurements were done with        8 bytes
 The bandwidth measurements were done with  2000000 bytes
 The ring communication was done in both directions on 16 processes
 The Ping Pong measurements were done on 
  -         240 pairs of processes for latency benchmarking, and 
  -         240 pairs of processes for bandwidth benchmarking, 
 out of 16*(16-1) =        240 possible combinations on 16 processes.
 (1 MB/s = 10**6 byte/sec)

------------------------------------------------------------------
Current time (1553530241) is Mon Mar 25 12:10:41 2019

End of LatencyBandwidth section.
Begin of HPL section.
================================================================================
HPLinpack 2.0  --  High-Performance Linpack benchmark  --   September 10, 2008
Written by A. Petitet and R. Clint Whaley,  Innovative Computing Laboratory, UTK
Modified by Piotr Luszczek, Innovative Computing Laboratory, UTK
Modified by Julien Langou, University of Colorado Denver
================================================================================

An explanation of the input/output parameters follows:
T/V    : Wall time / encoded variant.
N      : The order of the coefficient matrix A.
NB     : The partitioning blocking factor.
P      : The number of process rows.
Q      : The number of process columns.
Time   : Time in seconds to solve the linear system.
Gflops : Rate of execution for solving the linear system.

The following parameter values will be used:

N      :   28284 
NB     :     112 
PMAP   : Row-major process mapping
P      :       4 
Q      :       4 
PFACT  :   Right 
NBMIN  :       4 
NDIV   :       3 
RFACT  :   Right 
BCAST  :  2ringM 
DEPTH  :       0 
SWAP   : Mix (threshold = 64)
L1     : transposed form
U      : transposed form
EQUIL  : yes
ALIGN  : 16 double precision words

--------------------------------------------------------------------------------

- The matrix A is randomly generated for each test.
- The following scaled residual check will be computed:
      ||Ax-b||_oo / ( eps * ( || x ||_oo * || A ||_oo + || b ||_oo ) * N )
- The relative machine precision (eps) is taken to be               1.110223e-16
- Computational tests pass if scaled residuals are less than                16.0

================================================================================
T/V                N    NB     P     Q               Time                 Gflops
--------------------------------------------------------------------------------
WR03R3R4       28284   112     4     4             125.29              1.204e+02
--------------------------------------------------------------------------------
||Ax-b||_oo/(eps*(||A||_oo*||x||_oo+||b||_oo)*N)=        0.0036127 ...... PASSED
================================================================================

Finished      1 tests with the following results:
              1 tests completed and passed residual checks,
              0 tests completed and failed residual checks,
              0 tests skipped because of illegal input values.
--------------------------------------------------------------------------------

End of Tests.
================================================================================
Current time (1553530370) is Mon Mar 25 12:12:50 2019

End of HPL section.
Begin of Summary section.
VersionMajor=1
VersionMinor=5
VersionMicro=0
VersionRelease=f
LANG=C
Success=1
sizeof_char=1
sizeof_short=2
sizeof_int=4
sizeof_long=8
sizeof_void_ptr=8
sizeof_size_t=8
sizeof_float=4
sizeof_double=8
sizeof_s64Int=8
sizeof_u64Int=8
sizeof_struct_double_double=16
CommWorldProcs=16
MPI_Wtick=1.000000e-06
HPL_Tflops=0.120409
HPL_time=125.287
HPL_eps=1.11022e-16
HPL_RnormI=4.03936e-10
HPL_Anorm1=7165.05
HPL_AnormI=7166.43
HPL_Xnorm1=25369.1
HPL_XnormI=4.96841
HPL_BnormI=0.499984
HPL_N=28284
HPL_NB=112
HPL_nprow=4
HPL_npcol=4
HPL_depth=0
HPL_nbdiv=3
HPL_nbmin=4
HPL_cpfact=R
HPL_crfact=R
HPL_ctop=3
HPL_order=R
HPL_dMACH_EPS=1.110223e-16
HPL_dMACH_SFMIN=2.225074e-308
HPL_dMACH_BASE=2.000000e+00
HPL_dMACH_PREC=2.220446e-16
HPL_dMACH_MLEN=5.300000e+01
HPL_dMACH_RND=1.000000e+00
HPL_dMACH_EMIN=-1.021000e+03
HPL_dMACH_RMIN=2.225074e-308
HPL_dMACH_EMAX=1.024000e+03
HPL_dMACH_RMAX=1.797693e+308
HPL_sMACH_EPS=5.960464e-08
HPL_sMACH_SFMIN=1.175494e-38
HPL_sMACH_BASE=2.000000e+00
HPL_sMACH_PREC=1.192093e-07
HPL_sMACH_MLEN=2.400000e+01
HPL_sMACH_RND=1.000000e+00
HPL_sMACH_EMIN=-1.250000e+02
HPL_sMACH_RMIN=1.175494e-38
HPL_sMACH_EMAX=1.280000e+02
HPL_sMACH_RMAX=3.402823e+38
dweps=1.110223e-16
sweps=5.960464e-08
HPLMaxProcs=16
HPLMinProcs=16
DGEMM_N=4081
StarDGEMM_Gflops=8.45383
SingleDGEMM_Gflops=8.66556
PTRANS_GBs=2.20197
PTRANS_time=0.726607
PTRANS_residual=0
PTRANS_n=14142
PTRANS_nb=112
PTRANS_nprow=4
PTRANS_npcol=4
MPIRandomAccess_LCG_N=536870912
MPIRandomAccess_LCG_time=59.3839
MPIRandomAccess_LCG_CheckTime=1.13561
MPIRandomAccess_LCG_Errors=0
MPIRandomAccess_LCG_ErrorsFraction=0
MPIRandomAccess_LCG_ExeUpdates=264677152
MPIRandomAccess_LCG_GUPs=0.00445705
MPIRandomAccess_LCG_TimeBound=60
MPIRandomAccess_LCG_Algorithm=0
MPIRandomAccess_N=536870912
MPIRandomAccess_time=55.5279
MPIRandomAccess_CheckTime=1.65434
MPIRandomAccess_Errors=0
MPIRandomAccess_ErrorsFraction=0
MPIRandomAccess_ExeUpdates=245540672
MPIRandomAccess_GUPs=0.00442194
MPIRandomAccess_TimeBound=60
MPIRandomAccess_Algorithm=0
RandomAccess_LCG_N=33554432
StarRandomAccess_LCG_GUPs=0.0297224
SingleRandomAccess_LCG_GUPs=0.0477238
RandomAccess_N=33554432
StarRandomAccess_GUPs=0.0295179
SingleRandomAccess_GUPs=0.0468403
STREAM_VectorSize=16666347
STREAM_Threads=1
StarSTREAM_Copy=3.92715
StarSTREAM_Scale=2.67115
StarSTREAM_Add=2.94678
StarSTREAM_Triad=2.9362
SingleSTREAM_Copy=8.71726
SingleSTREAM_Scale=8.64209
SingleSTREAM_Add=8.83962
SingleSTREAM_Triad=9.00502
FFT_N=8388608
StarFFT_Gflops=1.88865
SingleFFT_Gflops=2.93584
MPIFFT_N=67108864
MPIFFT_Gflops=11.9337
MPIFFT_maxErr=4.05607e-15
MPIFFT_Procs=16
MaxPingPongLatency_usec=2.11265
RandomlyOrderedRingLatency_usec=1.67591
MinPingPongBandwidth_GBytes=1.99586
NaturallyOrderedRingBandwidth_GBytes=1.23289
RandomlyOrderedRingBandwidth_GBytes=0.700355
MinPingPongLatency_usec=0.304646
AvgPingPongLatency_usec=1.29715
MaxPingPongBandwidth_GBytes=8.62139
AvgPingPongBandwidth_GBytes=4.0223
NaturallyOrderedRingLatency_usec=1.5974
FFTEnblk=16
FFTEnp=8
FFTEl2size=1048576
M_OPENMP=-1
omp_get_num_threads=0
omp_get_max_threads=0
omp_get_num_procs=0
MemProc=-1
MemSpec=-1
MemVal=-1
MPIFFT_time0=0
MPIFFT_time1=0
MPIFFT_time2=0
MPIFFT_time3=0
MPIFFT_time4=0
MPIFFT_time5=0
MPIFFT_time6=0
CPS_HPCC_FFT_235=0
CPS_HPCC_FFTW_ESTIMATE=0
CPS_HPCC_MEMALLCTR=0
CPS_HPL_USE_GETPROCESSTIMES=0
CPS_RA_SANDIA_NOPT=0
CPS_RA_SANDIA_OPT2=0
CPS_USING_FFTW=1
End of Summary section.
########################################################################
End of HPC Challenge tests.
Current time (1553530370) is Mon Mar 25 12:12:50 2019

########################################################################

```