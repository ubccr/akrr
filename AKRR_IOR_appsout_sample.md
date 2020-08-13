Example of appstdout from IOR

```text
===ExeBinSignature=== MD5: 256844ae824a4d38bd23d6b4cc2dd11b /projects/ccrstaff/general/nikolays/huey/appker/execs/ior/src/ior
===ExeBinSignature=== MD5: 2705d15430ebce01274ef94967122bcb /lib64/libm.so.6
===ExeBinSignature=== MD5: 0f65391c22de4d15744ea80ec857419a /util/academic/intel/18.3/compilers_and_libraries_2018.3.222/linux/mpi/intel64/lib/libmpifort.so.12
===ExeBinSignature=== MD5: d9196e5f82db2befd02eb55c78747724 /util/academic/intel/18.3/compilers_and_libraries_2018.3.222/linux/mpi/intel64/lib/libmpi.so.12
===ExeBinSignature=== MD5: bbb4814755042554781fce1b1da6fdb1 /lib64/libdl.so.2
===ExeBinSignature=== MD5: 5928d7f9554dde0b45bc87ac09598ad0 /lib64/librt.so.1
===ExeBinSignature=== MD5: 23902bbccc0e350c1fdf09d070f3cd48 /lib64/libpthread.so.0
===ExeBinSignature=== MD5: a2737e5fc2c2059bd357ef6015c99262 /lib64/libc.so.6
===ExeBinSignature=== MD5: c8f2c137eee1a4581bc0be7b63d2c603 /lib64/libgcc_s.so.1
Using /projects/ccrstaff/general/nikolays/huey/tmp/ior.4B5i3sf5v for test....
File System To Test: nfs ifs-x410.cbls.ccr.buffalo.edu:/ifs/projects /projects
# Starting Test: -a POSIX 
executing: mpiexec -n 16 -f all_nodes /projects/ccrstaff/general/nikolays/huey/appker/execs/ior/src/ior -vv  -Z -b 200m -t 20m -a POSIX  -w -k -o /projects/ccrstaff/general/nikolays/huey/tmp/ior.4B5i3sf5v/ior_test_file__a_POSIX
IOR-3.0.1: MPI Coordinated Test of Parallel I/O

Began: Fri Mar 22 12:41:45 2019
Command line used: /projects/ccrstaff/general/nikolays/huey/appker/execs/ior/src/ior -vv -Z -b 200m -t 20m -a POSIX -w -k -o /projects/ccrstaff/general/nikolays/huey/tmp/ior.4B5i3sf5v/ior_test_file__a_POSIX
Machine: Linux cpn-d13-16.int.ccr.buffalo.edu 3.10.0-957.1.3.el7.x86_64 #1 SMP Thu Nov 29 14:49:43 UTC 2018 x86_64
Using synchronized MPI timer
Start time skew across all tasks: 0.00 sec

Test 0 started: Fri Mar 22 12:41:45 2019
Path: /projects/ccrstaff/general/nikolays/huey/tmp/ior.4B5i3sf5v
FS: 1704.7 TiB   Used FS: 48.3%   Inodes: 2635486.5 Mi   Used Inodes: 35.2%
Participating tasks: 16
task 0 on cpn-d13-16.int.ccr.buffalo.edu
task 1 on cpn-d13-16.int.ccr.buffalo.edu
task 10 on cpn-d13-17.int.ccr.buffalo.edu
task 11 on cpn-d13-17.int.ccr.buffalo.edu
task 12 on cpn-d13-17.int.ccr.buffalo.edu
task 13 on cpn-d13-17.int.ccr.buffalo.edu
task 14 on cpn-d13-17.int.ccr.buffalo.edu
task 15 on cpn-d13-17.int.ccr.buffalo.edu
task 2 on cpn-d13-16.int.ccr.buffalo.edu
task 3 on cpn-d13-16.int.ccr.buffalo.edu
task 4 on cpn-d13-16.int.ccr.buffalo.edu
task 5 on cpn-d13-16.int.ccr.buffalo.edu
task 6 on cpn-d13-16.int.ccr.buffalo.edu
task 7 on cpn-d13-16.int.ccr.buffalo.edu
task 8 on cpn-d13-17.int.ccr.buffalo.edu
task 9 on cpn-d13-17.int.ccr.buffalo.edu
Summary:
        api                = POSIX
        test filename      = /projects/ccrstaff/general/nikolays/huey/tmp/ior.4B5i3sf5v/ior_test_file__a_POSIX
        access             = single-shared-file
        pattern            = segmented (1 segment)
        ordering in a file = sequential offsets
        ordering inter file= random task offsets >= 1, seed=0
        clients            = 16 (8 per node)
        repetitions        = 1
        xfersize           = 20 MiB
        blocksize          = 200 MiB
        aggregate filesize = 3.12 GiB
Using Time Stamp 1553272905 (0x5c951049) for Data Signature

access    bw(MiB/s)  block(KiB) xfer(KiB)  open(s)    wr/rd(s)   close(s)   total(s)   iter
------    ---------  ---------- ---------  --------   --------   --------   --------   ----
Commencing write performance test: Fri Mar 22 12:41:45 2019
write     158.39     204800     20480      0.003322   1.47       20.06      20.20      0   

Max Write: 158.39 MiB/sec (166.09 MB/sec)

Summary of all tests:
Operation   Max(MiB)   Min(MiB)  Mean(MiB)     StdDev    Mean(s) Test# #Tasks tPN reps fPP reord reordoff reordrand seed segcnt blksiz xsize aggsize API RefNum
write         158.39     158.39     158.39       0.00   20.20281 0 16 8 1 0 0 1 1 0 1 209715200 20971520 3355443200 POSIX 0

Finished: Fri Mar 22 12:42:05 2019
# Starting Test: -a POSIX -F 
executing: mpiexec -n 16 -f all_nodes /projects/ccrstaff/general/nikolays/huey/appker/execs/ior/src/ior -vv  -Z -b 200m -t 20m -a POSIX -F  -w -k -o /projects/ccrstaff/general/nikolays/huey/tmp/ior.4B5i3sf5v/ior_test_file__a_POSIX__F
IOR-3.0.1: MPI Coordinated Test of Parallel I/O

Began: Fri Mar 22 12:42:06 2019
Command line used: /projects/ccrstaff/general/nikolays/huey/appker/execs/ior/src/ior -vv -Z -b 200m -t 20m -a POSIX -F -w -k -o /projects/ccrstaff/general/nikolays/huey/tmp/ior.4B5i3sf5v/ior_test_file__a_POSIX__F
Machine: Linux cpn-d13-16.int.ccr.buffalo.edu 3.10.0-957.1.3.el7.x86_64 #1 SMP Thu Nov 29 14:49:43 UTC 2018 x86_64
Using synchronized MPI timer
Start time skew across all tasks: 0.00 sec

Test 0 started: Fri Mar 22 12:42:06 2019
Path: /projects/ccrstaff/general/nikolays/huey/tmp/ior.4B5i3sf5v
FS: 1704.7 TiB   Used FS: 48.3%   Inodes: 2635486.5 Mi   Used Inodes: 35.2%
Participating tasks: 16
task 0 on cpn-d13-16.int.ccr.buffalo.edu
task 1 on cpn-d13-16.int.ccr.buffalo.edu
task 10 on cpn-d13-17.int.ccr.buffalo.edu
task 11 on cpn-d13-17.int.ccr.buffalo.edu
task 12 on cpn-d13-17.int.ccr.buffalo.edu
task 13 on cpn-d13-17.int.ccr.buffalo.edu
task 14 on cpn-d13-17.int.ccr.buffalo.edu
task 15 on cpn-d13-17.int.ccr.buffalo.edu
task 2 on cpn-d13-16.int.ccr.buffalo.edu
task 3 on cpn-d13-16.int.ccr.buffalo.edu
task 4 on cpn-d13-16.int.ccr.buffalo.edu
task 5 on cpn-d13-16.int.ccr.buffalo.edu
task 6 on cpn-d13-16.int.ccr.buffalo.edu
task 7 on cpn-d13-16.int.ccr.buffalo.edu
task 8 on cpn-d13-17.int.ccr.buffalo.edu
task 9 on cpn-d13-17.int.ccr.buffalo.edu
Summary:
        api                = POSIX
        test filename      = /projects/ccrstaff/general/nikolays/huey/tmp/ior.4B5i3sf5v/ior_test_file__a_POSIX__F
        access             = file-per-process
        pattern            = segmented (1 segment)
        ordering in a file = sequential offsets
        ordering inter file= random task offsets >= 1, seed=0
        clients            = 16 (8 per node)
        repetitions        = 1
        xfersize           = 20 MiB
        blocksize          = 200 MiB
        aggregate filesize = 3.12 GiB
Using Time Stamp 1553272926 (0x5c95105e) for Data Signature

access    bw(MiB/s)  block(KiB) xfer(KiB)  open(s)    wr/rd(s)   close(s)   total(s)   iter
------    ---------  ---------- ---------  --------   --------   --------   --------   ----
Commencing write performance test: Fri Mar 22 12:42:06 2019
write     227.31     204800     20480      0.027671   0.223688   13.89      14.08      0   

Max Write: 227.31 MiB/sec (238.35 MB/sec)

Summary of all tests:
Operation   Max(MiB)   Min(MiB)  Mean(MiB)     StdDev    Mean(s) Test# #Tasks tPN reps fPP reord reordoff reordrand seed segcnt blksiz xsize aggsize API RefNum
write         227.31     227.31     227.31       0.00   14.07764 0 16 8 1 1 0 1 1 0 1 209715200 20971520 3355443200 POSIX 0

Finished: Fri Mar 22 12:42:20 2019
# Starting Test: -a POSIX 
executing: mpiexec -n 16 -f all_nodes_offset /projects/ccrstaff/general/nikolays/huey/appker/execs/ior/src/ior -vv  -Z -b 200m -t 20m -a POSIX  -r -o /projects/ccrstaff/general/nikolays/huey/tmp/ior.4B5i3sf5v/ior_test_file__a_POSIX
IOR-3.0.1: MPI Coordinated Test of Parallel I/O

Began: Fri Mar 22 12:42:21 2019
Command line used: /projects/ccrstaff/general/nikolays/huey/appker/execs/ior/src/ior -vv -Z -b 200m -t 20m -a POSIX -r -o /projects/ccrstaff/general/nikolays/huey/tmp/ior.4B5i3sf5v/ior_test_file__a_POSIX
Machine: Linux cpn-d13-17.int.ccr.buffalo.edu 3.10.0-957.1.3.el7.x86_64 #1 SMP Thu Nov 29 14:49:43 UTC 2018 x86_64
Using synchronized MPI timer
Start time skew across all tasks: 0.00 sec

Test 0 started: Fri Mar 22 12:42:21 2019
Path: /projects/ccrstaff/general/nikolays/huey/tmp/ior.4B5i3sf5v
FS: 1704.7 TiB   Used FS: 48.3%   Inodes: 2635486.5 Mi   Used Inodes: 35.2%
Participating tasks: 16
task 0 on cpn-d13-17.int.ccr.buffalo.edu
task 1 on cpn-d13-17.int.ccr.buffalo.edu
task 10 on cpn-d13-16.int.ccr.buffalo.edu
task 11 on cpn-d13-16.int.ccr.buffalo.edu
task 12 on cpn-d13-16.int.ccr.buffalo.edu
task 13 on cpn-d13-16.int.ccr.buffalo.edu
task 14 on cpn-d13-16.int.ccr.buffalo.edu
task 15 on cpn-d13-16.int.ccr.buffalo.edu
task 2 on cpn-d13-17.int.ccr.buffalo.edu
task 3 on cpn-d13-17.int.ccr.buffalo.edu
task 4 on cpn-d13-17.int.ccr.buffalo.edu
task 5 on cpn-d13-17.int.ccr.buffalo.edu
task 6 on cpn-d13-17.int.ccr.buffalo.edu
task 7 on cpn-d13-17.int.ccr.buffalo.edu
task 8 on cpn-d13-16.int.ccr.buffalo.edu
task 9 on cpn-d13-16.int.ccr.buffalo.edu
Summary:
        api                = POSIX
        test filename      = /projects/ccrstaff/general/nikolays/huey/tmp/ior.4B5i3sf5v/ior_test_file__a_POSIX
        access             = single-shared-file
        pattern            = segmented (1 segment)
        ordering in a file = sequential offsets
        ordering inter file= random task offsets >= 1, seed=0
        clients            = 16 (8 per node)
        repetitions        = 1
        xfersize           = 20 MiB
        blocksize          = 200 MiB
        aggregate filesize = 3.12 GiB
Using Time Stamp 1553272941 (0x5c95106d) for Data Signature

access    bw(MiB/s)  block(KiB) xfer(KiB)  open(s)    wr/rd(s)   close(s)   total(s)   iter
------    ---------  ---------- ---------  --------   --------   --------   --------   ----
#File Hits Dist: 6 6 3 0 1
Commencing read performance test: Fri Mar 22 12:42:21 2019
read      263.36     204800     20480      0.002154   12.15      12.06      12.15      0   
remove    -          -          -          -          -          -          0.182582   0   

Max Read:  263.36 MiB/sec (276.16 MB/sec)

Summary of all tests:
Operation   Max(MiB)   Min(MiB)  Mean(MiB)     StdDev    Mean(s) Test# #Tasks tPN reps fPP reord reordoff reordrand seed segcnt blksiz xsize aggsize API RefNum
read          263.36     263.36     263.36       0.00   12.15054 0 16 8 1 0 0 1 1 0 1 209715200 20971520 3355443200 POSIX 0

Finished: Fri Mar 22 12:42:33 2019
# Starting Test: -a POSIX -F 
executing: mpiexec -n 16 -f all_nodes_offset /projects/ccrstaff/general/nikolays/huey/appker/execs/ior/src/ior -vv  -Z -b 200m -t 20m -a POSIX -F  -r -o /projects/ccrstaff/general/nikolays/huey/tmp/ior.4B5i3sf5v/ior_test_file__a_POSIX__F
IOR-3.0.1: MPI Coordinated Test of Parallel I/O

Began: Fri Mar 22 12:42:34 2019
Command line used: /projects/ccrstaff/general/nikolays/huey/appker/execs/ior/src/ior -vv -Z -b 200m -t 20m -a POSIX -F -r -o /projects/ccrstaff/general/nikolays/huey/tmp/ior.4B5i3sf5v/ior_test_file__a_POSIX__F
Machine: Linux cpn-d13-17.int.ccr.buffalo.edu 3.10.0-957.1.3.el7.x86_64 #1 SMP Thu Nov 29 14:49:43 UTC 2018 x86_64
Using synchronized MPI timer
Start time skew across all tasks: 0.00 sec

Test 0 started: Fri Mar 22 12:42:34 2019
Path: /projects/ccrstaff/general/nikolays/huey/tmp/ior.4B5i3sf5v
FS: 1704.7 TiB   Used FS: 48.3%   Inodes: 2635486.5 Mi   Used Inodes: 35.2%
Participating tasks: 16
task 0 on cpn-d13-17.int.ccr.buffalo.edu
task 1 on cpn-d13-17.int.ccr.buffalo.edu
task 10 on cpn-d13-16.int.ccr.buffalo.edu
task 11 on cpn-d13-16.int.ccr.buffalo.edu
task 12 on cpn-d13-16.int.ccr.buffalo.edu
task 13 on cpn-d13-16.int.ccr.buffalo.edu
task 14 on cpn-d13-16.int.ccr.buffalo.edu
task 15 on cpn-d13-16.int.ccr.buffalo.edu
task 2 on cpn-d13-17.int.ccr.buffalo.edu
task 3 on cpn-d13-17.int.ccr.buffalo.edu
task 4 on cpn-d13-17.int.ccr.buffalo.edu
task 5 on cpn-d13-17.int.ccr.buffalo.edu
task 6 on cpn-d13-17.int.ccr.buffalo.edu
task 7 on cpn-d13-17.int.ccr.buffalo.edu
task 8 on cpn-d13-16.int.ccr.buffalo.edu
task 9 on cpn-d13-16.int.ccr.buffalo.edu
Summary:
        api                = POSIX
        test filename      = /projects/ccrstaff/general/nikolays/huey/tmp/ior.4B5i3sf5v/ior_test_file__a_POSIX__F
        access             = file-per-process
        pattern            = segmented (1 segment)
        ordering in a file = sequential offsets
        ordering inter file= random task offsets >= 1, seed=0
        clients            = 16 (8 per node)
        repetitions        = 1
        xfersize           = 20 MiB
        blocksize          = 200 MiB
        aggregate filesize = 3.12 GiB
Using Time Stamp 1553272954 (0x5c95107a) for Data Signature

access    bw(MiB/s)  block(KiB) xfer(KiB)  open(s)    wr/rd(s)   close(s)   total(s)   iter
------    ---------  ---------- ---------  --------   --------   --------   --------   ----
#File Hits Dist: 6 6 3 0 1
Commencing read performance test: Fri Mar 22 12:42:34 2019
read      468.59     204800     20480      0.002584   6.83       6.74       6.83       0   
remove    -          -          -          -          -          -          0.484296   0   

Max Read:  468.59 MiB/sec (491.36 MB/sec)

Summary of all tests:
Operation   Max(MiB)   Min(MiB)  Mean(MiB)     StdDev    Mean(s) Test# #Tasks tPN reps fPP reord reordoff reordrand seed segcnt blksiz xsize aggsize API RefNum
read          468.59     468.59     468.59       0.00    6.82894 0 16 8 1 1 0 1 1 0 1 209715200 20971520 3355443200 POSIX 0

Finished: Fri Mar 22 12:42:41 2019
```