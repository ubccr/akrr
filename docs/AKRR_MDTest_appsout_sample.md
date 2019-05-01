Example of appstdout from IOR

```text
===ExeBinSignature=== MD5: fbbca3e21e2c19d822c832e89442601d /projects/ccrstaff/general/nikolays/huey/appker/execs/ior-3.2.0/src/mdtest
===ExeBinSignature=== MD5: d74b2178e51775912ac0a754ada35608 /lib64/libgpfs.so
===ExeBinSignature=== MD5: 0f65391c22de4d15744ea80ec857419a /util/academic/intel/18.3/compilers_and_libraries_2018.3.222/linux/mpi/intel64/lib/libmpifort.so.12
===ExeBinSignature=== MD5: b8e568c1e497e59111c23f2e3297de18 /util/academic/intel/18.3/compilers_and_libraries_2018.3.222/linux/mpi/intel64/lib/debug_mt/libmpi.so.12
===ExeBinSignature=== MD5: bbb4814755042554781fce1b1da6fdb1 /lib64/libdl.so.2
===ExeBinSignature=== MD5: 5928d7f9554dde0b45bc87ac09598ad0 /lib64/librt.so.1
===ExeBinSignature=== MD5: 23902bbccc0e350c1fdf09d070f3cd48 /lib64/libpthread.so.0
===ExeBinSignature=== MD5: 2705d15430ebce01274ef94967122bcb /lib64/libm.so.6
===ExeBinSignature=== MD5: c8f2c137eee1a4581bc0be7b63d2c603 /lib64/libgcc_s.so.1
===ExeBinSignature=== MD5: a2737e5fc2c2059bd357ef6015c99262 /lib64/libc.so.6
#Testing single directory
-- started at 05/01/2019 16:07:45 --

mdtest-1.9.3 was launched with 16 total task(s) on 2 node(s)
Command line used: /projects/ccrstaff/general/nikolays/huey/appker/execs/ior/src/mdtest "-I" "32" "-z" "0" "-b" "0" "-i" "10"
Path: /projects/ccrstaff/general/nikolays/huey/tmp/namd.41pJohq2C
FS: 1704.7 TiB   Used FS: 49.3%   Inodes: 2635486.5 Mi   Used Inodes: 36.0%

16 tasks, 512 files/directories

SUMMARY rate: (of 10 iterations)
   Operation                      Max            Min           Mean        Std Dev
   ---------                      ---            ---           ----        -------
   Directory creation:        661.621        661.595        661.613          0.010
   Directory stat    :      21529.737      21508.820      21524.971          8.035
   Directory removal :        434.708        434.696        434.705          0.005
   File creation     :        589.172        589.150        589.165          0.008
   File stat         :      23704.742      23687.223      23695.300          5.008
   File read         :      13809.829      13807.964      13808.870          0.634
   File removal      :        521.333        521.329        521.332          0.002
   Tree creation     :        796.185        534.988        676.757         70.926
   Tree removal      :        586.534        251.819        451.828        107.067

-- finished at 05/01/2019 16:08:33 --
#Testing single directory per process
-- started at 05/01/2019 16:08:34 --

mdtest-1.9.3 was launched with 16 total task(s) on 2 node(s)
Command line used: /projects/ccrstaff/general/nikolays/huey/appker/execs/ior/src/mdtest "-I" "32" "-z" "0" "-b" "0" "-i" "10" "-u"
Path: /projects/ccrstaff/general/nikolays/huey/tmp/namd.41pJohq2C
FS: 1704.7 TiB   Used FS: 49.3%   Inodes: 2635486.5 Mi   Used Inodes: 36.0%

16 tasks, 512 files/directories

SUMMARY rate: (of 10 iterations)
   Operation                      Max            Min           Mean        Std Dev
   ---------                      ---            ---           ----        -------
   Directory creation:       3118.134       3117.441       3117.935          0.245
   Directory stat    :    2404796.918    2296773.955    2335336.847      28944.830
   Directory removal :       1973.558       1973.375       1973.497          0.059
   File creation     :       2557.311       2557.073       2557.210          0.073
   File stat         :    2160446.326    1766022.737    1858309.018     125923.952
   File read         :      11925.032      11923.576      11924.191          0.489
   File removal      :       2590.148       2590.082       2590.122          0.022
   Tree creation     :         42.638          6.654         26.677         11.181
   Tree removal      :         34.058         10.771         22.118          8.100

-- finished at 05/01/2019 16:08:47 --
#Testing single tree directory
-- started at 05/01/2019 16:08:47 --

mdtest-1.9.3 was launched with 16 total task(s) on 2 node(s)
Command line used: /projects/ccrstaff/general/nikolays/huey/appker/execs/ior/src/mdtest "-I" "4" "-z" "4" "-b" "2" "-i" "10"
Path: /projects/ccrstaff/general/nikolays/huey/tmp/namd.41pJohq2C
FS: 1704.7 TiB   Used FS: 49.3%   Inodes: 2635486.5 Mi   Used Inodes: 36.0%

16 tasks, 1984 files/directories

SUMMARY rate: (of 10 iterations)
   Operation                      Max            Min           Mean        Std Dev
   ---------                      ---            ---           ----        -------
   Directory creation:       1152.030       1152.001       1152.022          0.011
   Directory stat    :      47672.648      47621.359      47658.567         18.754
   Directory removal :       1162.957       1162.917       1162.948          0.014
   File creation     :       1805.159       1805.049       1805.128          0.039
   File stat         :      52564.583      52445.321      52507.891         36.079
   File read         :      12880.022      12876.594      12879.241          1.305
   File removal      :       1447.654       1447.647       1447.651          0.002
   Tree creation     :        729.809        281.869        478.611        126.730
   Tree removal      :        649.760        215.787        462.012        130.500

-- finished at 05/01/2019 16:10:07 --
#Testing single tree directory per process
-- started at 05/01/2019 16:10:07 --

mdtest-1.9.3 was launched with 16 total task(s) on 2 node(s)
Command line used: /projects/ccrstaff/general/nikolays/huey/appker/execs/ior/src/mdtest "-I" "4" "-z" "4" "-b" "2" "-i" "10" "-u"
Path: /projects/ccrstaff/general/nikolays/huey/tmp/namd.41pJohq2C
FS: 1704.7 TiB   Used FS: 49.3%   Inodes: 2635486.5 Mi   Used Inodes: 36.0%

16 tasks, 1984 files/directories

SUMMARY rate: (of 10 iterations)
   Operation                      Max            Min           Mean        Std Dev
   ---------                      ---            ---           ----        -------
   Directory creation:       2245.310       2245.185       2245.275          0.045
   Directory stat    :    1970518.384    1952486.893    1961106.252       5396.153
   Directory removal :       1595.862       1595.835       1595.851          0.009
   File creation     :       2063.013       2062.930       2062.995          0.023
   File stat         :    1887817.408    1830107.573    1860217.869      15220.532
   File read         :      13699.971      13695.033      13698.744          1.839
   File removal      :       2087.474       2087.355       2087.448          0.039
   Tree creation     :        104.432         64.254         83.295         12.924
   Tree removal      :         88.930         50.961         70.530         10.983

-- finished at 05/01/2019 16:11:05 --
```