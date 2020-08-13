Example of appstdout from NWChem

```text
===ExeBinSignature=== MD5: 8404c107e770525c3f2fbb173ec6ad64 /util/academic/nwchem/nwchem-6.8/bin/LINUX64/nwchem
===ExeBinSignature=== MD5: fc7521ec0d9841e0b02405a3c6f14ac7 /util/academic/intel/18.3/compilers_and_libraries_2018.3.222/linux/mkl/lib/intel64/libmkl_intel_ilp64.so
===ExeBinSignature=== MD5: f69324cf9d6d73ccd17e71804fd72f8f /util/academic/intel/18.3/compilers_and_libraries_2018.3.222/linux/mkl/lib/intel64/libmkl_sequential.so
===ExeBinSignature=== MD5: 8d910a2a99c55892275240801efe5adc /util/academic/intel/18.3/compilers_and_libraries_2018.3.222/linux/mkl/lib/intel64/libmkl_core.so
===ExeBinSignature=== MD5: 23902bbccc0e350c1fdf09d070f3cd48 /lib64/libpthread.so.0
===ExeBinSignature=== MD5: 0f65391c22de4d15744ea80ec857419a /util/academic/intel/18.3/compilers_and_libraries_2018.3.222/linux/mpi/intel64/lib/libmpifort.so.12
===ExeBinSignature=== MD5: d9196e5f82db2befd02eb55c78747724 /util/academic/intel/18.3/compilers_and_libraries_2018.3.222/linux/mpi/intel64/lib/libmpi.so.12
===ExeBinSignature=== MD5: bbb4814755042554781fce1b1da6fdb1 /lib64/libdl.so.2
===ExeBinSignature=== MD5: 5928d7f9554dde0b45bc87ac09598ad0 /lib64/librt.so.1
===ExeBinSignature=== MD5: ff8b935e40bcd5cb1024a6b2819a47bc /util/academic/intel/18.3/compilers_and_libraries_2018.3.222/linux/mpi/intel64/lib/libmpi_ilp64.so.4
===ExeBinSignature=== MD5: 2705d15430ebce01274ef94967122bcb /lib64/libm.so.6
===ExeBinSignature=== MD5: a2737e5fc2c2059bd357ef6015c99262 /lib64/libc.so.6
===ExeBinSignature=== MD5: c8f2c137eee1a4581bc0be7b63d2c603 /lib64/libgcc_s.so.1
 argument  1 = aump2.nw
                                         
                                         
 
 
              Northwest Computational Chemistry Package (NWChem) 6.8
              ------------------------------------------------------
 
 
                    Environmental Molecular Sciences Laboratory
                       Pacific Northwest National Laboratory
                                Richland, WA 99352
 
                              Copyright (c) 1994-2017
                       Pacific Northwest National Laboratory
                            Battelle Memorial Institute
 
             NWChem is an open-source computational chemistry package
                        distributed under the terms of the
                      Educational Community License (ECL) 2.0
             A copy of the license is included with this distribution
                              in the LICENSE.TXT file
 
                                  ACKNOWLEDGMENT
                                  --------------

            This software and its documentation were developed at the
            EMSL at Pacific Northwest National Laboratory, a multiprogram
            national laboratory, operated for the U.S. Department of Energy
            by Battelle under Contract Number DE-AC05-76RL01830. Support
            for this work was provided by the Department of Energy Office
            of Biological and Environmental Research, Office of Basic
            Energy Sciences, and the Office of Advanced Scientific Computing.


           Job information
           ---------------

    hostname        = cpn-d13-16.int.ccr.buffalo.edu
    program         = /util/academic/nwchem/nwchem-6.8/bin/LINUX64/nwchem
    date            = Mon Mar 25 15:46:10 2019

    compiled        = Tue_Nov_06_14:59:08_2018
    source          = /util/academic/nwchem/nwchem-6.8
    nwchem branch   = 6.8
    nwchem revision = v6.8-47-gdf6c956
    ga revision     = ga-5.6.3
    use scalapack   = F
    input           = aump2.nw
    prefix          = Au+.
    data base       = /projects/ccrstaff/general/nikolays/huey/tmp/nwchem.mMfYjJzv0/Au+.db
    status          = startup
    nproc           =       14
    time left       =     -1s



           Memory information
           ------------------

    heap     =   13107200 doubles =    100.0 Mbytes
    stack    =   13107197 doubles =    100.0 Mbytes
    global   =   26214400 doubles =    200.0 Mbytes (distinct from heap & stack)
    total    =   52428797 doubles =    400.0 Mbytes
    verify   = yes
    hardfail = no 


           Directory information
           ---------------------
 
  0 permanent = /projects/ccrstaff/general/nikolays/huey/tmp/nwchem.mMfYjJzv0
  0 scratch   = /projects/ccrstaff/general/nikolays/huey/tmp/nwchem.mMfYjJzv0
 
 
 
 
                                NWChem Input Module
                                -------------------
 
 
               Au+, Au(14s,10p,8d,3f,2g,1h) -> [11s,10p,8d,3f,2g,1h]
               -----------------------------------------------------
 
 
                             Geometry "geometry" -> ""
                             -------------------------
 
 Output coordinates in a.u. (scale by  1.000000000 to convert to a.u.)
 
  No.       Tag          Charge          X              Y              Z
 ---- ---------------- ---------- -------------- -------------- --------------
    1 Au                  79.0000     0.00000000     0.00000000     0.00000000
 
      Atomic Mass 
      ----------- 
 
      Au               196.966600
 

 Effective nuclear repulsion energy (a.u.)       0.0000000000

            Nuclear Dipole moment (a.u.) 
            ----------------------------
        X                 Y               Z
 ---------------- ---------------- ----------------
     0.0000000000     0.0000000000     0.0000000000
 
      Symmetry information
      --------------------
 
 Group name             D2h       
 Group number             26
 Group order               8
 No. of unique centers     1
 
      Symmetry unique atoms
 
     1
 
 
            XYZ format geometry
            -------------------
     1
 geometry
 Au                    0.00000000     0.00000000     0.00000000
 
  warning:::::::::::::: from_environment
  NWCHEM_BASIS_LIBRARY set to: <
 /util/academic/nwchem/nwchem-6.8/src/basis/libraries>
  but file does not exist !
  using .nwchemrc or compiled library
  warning:::::::::::::: from_environment
  NWCHEM_BASIS_LIBRARY set to: <
 /util/academic/nwchem/nwchem-6.8/src/basis/libraries>
  but file does not exist !
  using .nwchemrc or compiled library
                 ECP       "ecp basis" -> "" (spherical)
                -----
  Au (Gold) Replaces    60 electrons
  ----------------------------------
             Channel    R-exponent     Exponent     Coefficients
         ------------ ---------------------------------------------------------
  1 U-s       Both         2.00       13.205100     426.709840
  1 U-s       Both         2.00        6.602550      35.938820
 
  2 U-p       Both         2.00       10.452020     261.161020
  2 U-p       Both         2.00        5.226010      26.626280
 
  3 U-d       Both         2.00        7.851100     124.756830
  3 U-d       Both         2.00        3.925550      15.772260
 
  4 U-f       Both         2.00        4.789800      30.568470
  4 U-f       Both         2.00        2.394910       5.183770
 
                                 NWChem SCF Module
                                 -----------------
 
 
               Au+, Au(14s,10p,8d,3f,2g,1h) -> [11s,10p,8d,3f,2g,1h]
 
 

  ao basis        = "ao basis"
  functions       =   131
  atoms           =     1
  closed shells   =     9
  open shells     =     0
  charge          =   1.00
  wavefunction    = RHF 
  input vectors   = atomic
  output vectors  = /projects/ccrstaff/general/nikolays/huey/tmp/nwchem.mMfYjJzv0/Au+.movecs
  use symmetry    = T
  symmetry adapt  = T


 Summary of "ao basis" -> "ao basis" (spherical)
 ------------------------------------------------------------------------------
       Tag                 Description            Shells   Functions and Types
 ---------------- ------------------------------  ------  ---------------------
 Au                      user specified             35      131   11s10p8d3f2g1h


      Symmetry analysis of basis
      --------------------------
 
        ag         33
        au          5
        b1g        12
        b1u        19
        b2g        12
        b2u        19
        b3g        12
        b3u        19
 

 Forming initial guess at       1.0s

 
      Superposition of Atomic Density Guess
      -------------------------------------
 
 Sum of atomic energies:        -152.70213399

 Renormalizing density from      19.00 to     18
 
      Non-variational initial energy
      ------------------------------

 Total energy =    -132.677517
 1-e energy   =    -224.969612
 2-e energy   =      92.292095
 HOMO         =      -1.065906
 LUMO         =      -0.690489
 
 
      Symmetry analysis of molecular orbitals - initial
      -------------------------------------------------
 

 !! scf_movecs_sym_adapt:  116 vectors were symmetry contaminated

  Symmetry fudging

 !! scf_movecs_sym_adapt:   92 vectors were symmetry contaminated

  Numbering of irreducible representations: 
 
     1 ag          2 au          3 b1g         4 b1u         5 b2g     
     6 b2u         7 b3g         8 b3u     
 
  Orbital symmetries:
 
     1 ag          2 b3u         3 b1u         4 b2u         5 b3g     
     6 ag          7 ag          8 b2g         9 b1g        10 ag      
    11 b2u        12 b3u        13 b1u        14 ag         15 b1u     
    16 b2u        17 b3u        18 b1g        19 ag      
 

 Starting SCF solution at       1.5s



 ----------------------------------------------
         Quadratically convergent ROHF

 Convergence threshold     :          1.000E-06
 Maximum no. of iterations :           30
 Final Fock-matrix accuracy:          1.000E-08
 ----------------------------------------------


 Integral file          = /projects/ccrstaff/general/nikolays/huey/tmp/nwchem.mMfYjJzv0/Au+.aoints.00
 Record size in doubles =    65536    No. of integs per rec  =    43688
 Max. records in memory =       15    Max. records in file   = ********
 No. of bits per label  =        8    No. of bits per value  =       64


 #quartets = 1.988D+05 #integrals = 3.637D+06 #direct =  0.0% #cached =100.0%


File balance: exchanges=     7  moved=    11  time=   0.0


              iter       energy          gnorm     gmax       time
             ----- ------------------- --------- --------- --------
                 1     -134.4929368359  2.43D+00  5.95D-01      1.8
                 2     -134.6756063375  4.21D-01  1.13D-01      1.9
                 3     -134.6837419679  1.54D-01  4.38D-02      2.0
                 4     -134.6843339171  1.68D-03  3.81D-04      2.1
                 5     -134.6843340439  1.63D-07  4.56D-08      2.3


       Final RHF  results 
       ------------------ 

         Total SCF energy =   -134.684334043865
      One-electron energy =   -233.466922512879
      Two-electron energy =     98.782588469014
 Nuclear repulsion energy =      0.000000000000

        Time for solution =      1.6s


 
       Symmetry analysis of molecular orbitals - final
       -----------------------------------------------
 
  Numbering of irreducible representations: 
 
     1 ag          2 au          3 b1g         4 b1u         5 b2g     
     6 b2u         7 b3g         8 b3u     
 
  Orbital symmetries:
 
     1 ag          2 b3u         3 b2u         4 b1u         5 b1g     
     6 ag          7 b2g         8 b3g         9 ag         10 ag      
    11 b3u        12 b2u        13 b1u        14 ag         15 b2g     
    16 b3g        17 b1g        18 ag         19 ag      
 
             Final eigenvalues
             -----------------

              1      
    1   -5.0081
    2   -3.0370
    3   -3.0370
    4   -3.0370
    5   -0.7664
    6   -0.7664
    7   -0.7664
    8   -0.7664
    9   -0.7664
   10   -0.2738
   11   -0.1241
   12   -0.1241
   13   -0.1241
   14   -0.0832
   15   -0.0460
   16   -0.0460
   17   -0.0460
   18   -0.0460
   19   -0.0460
 
                       ROHF Final Molecular Orbital Analysis
                       -------------------------------------
 
 Vector    2  Occ=2.000000D+00  E=-3.036992D+00  Symmetry=b3u
              MO Center=  2.5D-17, -2.1D-32,  1.3D-32, r^2= 3.8D-01
   Bfn.  Coefficient  Atom+Function         Bfn.  Coefficient  Atom+Function  
  ----- ------------  ---------------      ----- ------------  ---------------
    24      0.691291  1 Au px                18     -0.358797  1 Au px         
    21      0.309698  1 Au px                27      0.220256  1 Au px         
 
 Vector    3  Occ=2.000000D+00  E=-3.036992D+00  Symmetry=b2u
              MO Center= -2.1D-32, -4.5D-17,  2.7D-32, r^2= 3.8D-01
   Bfn.  Coefficient  Atom+Function         Bfn.  Coefficient  Atom+Function  
  ----- ------------  ---------------      ----- ------------  ---------------
    25      0.691291  1 Au py                19     -0.358797  1 Au py         
    22      0.309698  1 Au py                28      0.220256  1 Au py         
 
 Vector    4  Occ=2.000000D+00  E=-3.036992D+00  Symmetry=b1u
              MO Center=  2.9D-33, -1.5D-32,  5.7D-17, r^2= 3.8D-01
   Bfn.  Coefficient  Atom+Function         Bfn.  Coefficient  Atom+Function  
  ----- ------------  ---------------      ----- ------------  ---------------
    26      0.691291  1 Au pz                20     -0.358797  1 Au pz         
    23      0.309698  1 Au pz                29      0.220256  1 Au pz         
 
 Vector    5  Occ=2.000000D+00  E=-7.663507D-01  Symmetry=b1g
              MO Center= -4.8D-31, -1.2D-31,  6.3D-33, r^2= 8.0D-01
   Bfn.  Coefficient  Atom+Function         Bfn.  Coefficient  Atom+Function  
  ----- ------------  ---------------      ----- ------------  ---------------
    57      0.500457  1 Au d -2              62      0.345319  1 Au d -2       
    52      0.273449  1 Au d -2       
 
 Vector    6  Occ=2.000000D+00  E=-7.663507D-01  Symmetry=ag
              MO Center=  4.1D-21,  1.8D-20,  8.1D-22, r^2= 8.0D-01
   Bfn.  Coefficient  Atom+Function         Bfn.  Coefficient  Atom+Function  
  ----- ------------  ---------------      ----- ------------  ---------------
    61      0.500457  1 Au d  2              66      0.345319  1 Au d  2       
    56      0.273448  1 Au d  2       
 
 Vector    7  Occ=2.000000D+00  E=-7.663507D-01  Symmetry=b2g
              MO Center=  1.7D-31, -1.8D-32,  3.0D-31, r^2= 8.0D-01
   Bfn.  Coefficient  Atom+Function         Bfn.  Coefficient  Atom+Function  
  ----- ------------  ---------------      ----- ------------  ---------------
    60      0.500457  1 Au d  1              65      0.345319  1 Au d  1       
    55      0.273449  1 Au d  1       
 
 Vector    8  Occ=2.000000D+00  E=-7.663507D-01  Symmetry=b3g
              MO Center= -1.2D-32, -4.9D-31, -4.9D-31, r^2= 8.0D-01
   Bfn.  Coefficient  Atom+Function         Bfn.  Coefficient  Atom+Function  
  ----- ------------  ---------------      ----- ------------  ---------------
    58      0.500457  1 Au d -1              63      0.345319  1 Au d -1       
    53      0.273449  1 Au d -1       
 
 Vector    9  Occ=2.000000D+00  E=-7.663507D-01  Symmetry=ag
              MO Center=  5.6D-19, -6.0D-18,  1.4D-17, r^2= 8.0D-01
   Bfn.  Coefficient  Atom+Function         Bfn.  Coefficient  Atom+Function  
  ----- ------------  ---------------      ----- ------------  ---------------
    59      0.500457  1 Au d  0              64      0.345319  1 Au d  0       
    54      0.273448  1 Au d  0       
 
 Vector   10  Occ=0.000000D+00  E=-2.737631D-01  Symmetry=ag
              MO Center=  4.9D-16, -1.6D-15,  8.1D-16, r^2= 3.2D+00
   Bfn.  Coefficient  Atom+Function         Bfn.  Coefficient  Atom+Function  
  ----- ------------  ---------------      ----- ------------  ---------------
     7      0.534858  1 Au s                  8      0.451885  1 Au s          
     4     -0.439693  1 Au s                  2      0.338801  1 Au s          
     5     -0.179639  1 Au s                  6      0.170929  1 Au s          
 
 Vector   11  Occ=0.000000D+00  E=-1.240633D-01  Symmetry=b3u
              MO Center= -6.2D-14, -3.5D-28,  8.9D-29, r^2= 9.0D+00
   Bfn.  Coefficient  Atom+Function         Bfn.  Coefficient  Atom+Function  
  ----- ------------  ---------------      ----- ------------  ---------------
    36      0.475151  1 Au px                39      0.326236  1 Au px         
    33      0.273921  1 Au px         
 
 Vector   12  Occ=0.000000D+00  E=-1.240633D-01  Symmetry=b2u
              MO Center= -2.4D-28, -5.6D-14, -1.7D-29, r^2= 9.0D+00
   Bfn.  Coefficient  Atom+Function         Bfn.  Coefficient  Atom+Function  
  ----- ------------  ---------------      ----- ------------  ---------------
    37      0.475151  1 Au py                40      0.326236  1 Au py         
    34      0.273921  1 Au py         
 
 Vector   13  Occ=0.000000D+00  E=-1.240633D-01  Symmetry=b1u
              MO Center= -1.5D-29,  5.3D-30,  4.2D-15, r^2= 9.0D+00
   Bfn.  Coefficient  Atom+Function         Bfn.  Coefficient  Atom+Function  
  ----- ------------  ---------------      ----- ------------  ---------------
    38      0.475151  1 Au pz                41      0.326236  1 Au pz         
    35      0.273921  1 Au pz         
 
 Vector   14  Occ=0.000000D+00  E=-8.315755D-02  Symmetry=ag
              MO Center=  4.1D-13,  2.5D-13, -8.4D-14, r^2= 2.7D+01
   Bfn.  Coefficient  Atom+Function         Bfn.  Coefficient  Atom+Function  
  ----- ------------  ---------------      ----- ------------  ---------------
    10      0.989237  1 Au s                  8     -0.568065  1 Au s          
     7     -0.281727  1 Au s                  9      0.247978  1 Au s          
     4      0.157285  1 Au s          
 
 Vector   15  Occ=0.000000D+00  E=-4.596356D-02  Symmetry=b2g
              MO Center= -4.9D-30,  7.4D-33,  4.2D-30, r^2= 2.1D+01
   Bfn.  Coefficient  Atom+Function         Bfn.  Coefficient  Atom+Function  
  ----- ------------  ---------------      ----- ------------  ---------------
    80      1.035266  1 Au d  1       
 
 Vector   16  Occ=0.000000D+00  E=-4.596356D-02  Symmetry=b3g
              MO Center=  3.5D-33,  6.1D-31, -5.1D-31, r^2= 2.1D+01
   Bfn.  Coefficient  Atom+Function         Bfn.  Coefficient  Atom+Function  
  ----- ------------  ---------------      ----- ------------  ---------------
    78      1.035266  1 Au d -1       
 
 Vector   17  Occ=0.000000D+00  E=-4.596356D-02  Symmetry=b1g
              MO Center=  5.9D-30, -3.8D-29, -5.8D-33, r^2= 2.1D+01
   Bfn.  Coefficient  Atom+Function         Bfn.  Coefficient  Atom+Function  
  ----- ------------  ---------------      ----- ------------  ---------------
    77      1.035266  1 Au d -2       
 
 Vector   18  Occ=0.000000D+00  E=-4.596356D-02  Symmetry=ag
              MO Center=  8.4D-24,  5.0D-23,  1.3D-24, r^2= 2.1D+01
   Bfn.  Coefficient  Atom+Function         Bfn.  Coefficient  Atom+Function  
  ----- ------------  ---------------      ----- ------------  ---------------
    81      1.035266  1 Au d  2       
 
 Vector   19  Occ=0.000000D+00  E=-4.596356D-02  Symmetry=ag
              MO Center= -1.8D-18,  1.1D-17, -3.0D-17, r^2= 2.1D+01
   Bfn.  Coefficient  Atom+Function         Bfn.  Coefficient  Atom+Function  
  ----- ------------  ---------------      ----- ------------  ---------------
    79      1.035266  1 Au d  0       
 
 Vector   20  Occ=0.000000D+00  E=-4.114152D-02  Symmetry=ag
              MO Center= -4.5D-14,  2.2D-14,  1.1D-14, r^2= 9.0D+01
   Bfn.  Coefficient  Atom+Function         Bfn.  Coefficient  Atom+Function  
  ----- ------------  ---------------      ----- ------------  ---------------
    10      2.625479  1 Au s                 11     -2.483015  1 Au s          
     8     -0.295336  1 Au s                  7     -0.274571  1 Au s          
 
 Vector   21  Occ=0.000000D+00  E=-4.037265D-02  Symmetry=b3u
              MO Center= -2.9D-13, -1.3D-27,  3.8D-28, r^2= 2.6D+01
   Bfn.  Coefficient  Atom+Function         Bfn.  Coefficient  Atom+Function  
  ----- ------------  ---------------      ----- ------------  ---------------
    39      1.704342  1 Au px                36     -1.480350  1 Au px         
    30     -0.204256  1 Au px         
 
 Vector   22  Occ=0.000000D+00  E=-4.037265D-02  Symmetry=b2u
              MO Center= -8.9D-28, -1.9D-13, -9.9D-28, r^2= 2.6D+01
   Bfn.  Coefficient  Atom+Function         Bfn.  Coefficient  Atom+Function  
  ----- ------------  ---------------      ----- ------------  ---------------
    40      1.704342  1 Au py                37     -1.480350  1 Au py         
    31     -0.204256  1 Au py         
 
 Vector   23  Occ=0.000000D+00  E=-4.037265D-02  Symmetry=b1u
              MO Center= -6.8D-29,  2.6D-28,  6.7D-14, r^2= 2.6D+01
   Bfn.  Coefficient  Atom+Function         Bfn.  Coefficient  Atom+Function  
  ----- ------------  ---------------      ----- ------------  ---------------
    41      1.704342  1 Au pz                38     -1.480350  1 Au pz         
    32     -0.204256  1 Au pz         
 
 Vector   24  Occ=0.000000D+00  E= 1.843183D-03  Symmetry=ag
              MO Center=  1.6D-14,  3.1D-14, -8.3D-15, r^2= 6.3D+01
   Bfn.  Coefficient  Atom+Function         Bfn.  Coefficient  Atom+Function  
  ----- ------------  ---------------      ----- ------------  ---------------
     9      8.129307  1 Au s                 10     -7.410495  1 Au s          
     8     -3.954529  1 Au s                 11      2.790947  1 Au s          
     7      0.778871  1 Au s                  6     -0.513723  1 Au s          
     5      0.275756  1 Au s          
 
 Vector   25  Occ=0.000000D+00  E= 7.575540D-02  Symmetry=b3g
              MO Center=  3.2D-32,  2.0D-28,  1.3D-28, r^2= 1.5D+01
   Bfn.  Coefficient  Atom+Function         Bfn.  Coefficient  Atom+Function  
  ----- ------------  ---------------      ----- ------------  ---------------
    73      1.754774  1 Au d -1              78     -1.130510  1 Au d -1       
    68     -0.375168  1 Au d -1       
 
 Vector   26  Occ=0.000000D+00  E= 7.575540D-02  Symmetry=b2g
              MO Center= -5.1D-29,  2.7D-32, -5.7D-29, r^2= 1.5D+01
   Bfn.  Coefficient  Atom+Function         Bfn.  Coefficient  Atom+Function  
  ----- ------------  ---------------      ----- ------------  ---------------
    75      1.754774  1 Au d  1              80     -1.130510  1 Au d  1       
    70     -0.375168  1 Au d  1       
 
 Vector   27  Occ=0.000000D+00  E= 7.575540D-02  Symmetry=ag
              MO Center=  2.8D-21,  1.8D-20, -5.2D-23, r^2= 1.5D+01
   Bfn.  Coefficient  Atom+Function         Bfn.  Coefficient  Atom+Function  
  ----- ------------  ---------------      ----- ------------  ---------------
    76      1.754774  1 Au d  2              81     -1.130510  1 Au d  2       
    71     -0.375168  1 Au d  2       
 
 Vector   28  Occ=0.000000D+00  E= 7.575540D-02  Symmetry=b1g
              MO Center=  1.7D-28, -1.4D-28, -1.6D-32, r^2= 1.5D+01
   Bfn.  Coefficient  Atom+Function         Bfn.  Coefficient  Atom+Function  
  ----- ------------  ---------------      ----- ------------  ---------------
    72      1.754774  1 Au d -2              77     -1.130510  1 Au d -2       
    67     -0.375168  1 Au d -2       
 
 Vector   29  Occ=0.000000D+00  E= 7.575540D-02  Symmetry=ag
              MO Center= -2.5D-16,  1.6D-15, -4.4D-15, r^2= 1.5D+01
   Bfn.  Coefficient  Atom+Function         Bfn.  Coefficient  Atom+Function  
  ----- ------------  ---------------      ----- ------------  ---------------
    74      1.754774  1 Au d  0              79     -1.130510  1 Au d  0       
    69     -0.375168  1 Au d  0       
 
 Vector   30  Occ=0.000000D+00  E= 1.134408D-01  Symmetry=b3u
              MO Center= -1.4D-14, -2.5D-29, -2.5D-29, r^2= 1.5D+01
   Bfn.  Coefficient  Atom+Function         Bfn.  Coefficient  Atom+Function  
  ----- ------------  ---------------      ----- ------------  ---------------
    36      3.449203  1 Au px                33     -2.928930  1 Au px         
    39     -1.465915  1 Au px                30      0.678850  1 Au px         
    24      0.293066  1 Au px                27     -0.224024  1 Au px         
 
 Vector   31  Occ=0.000000D+00  E= 1.134408D-01  Symmetry=b2u
              MO Center=  4.9D-29, -6.2D-14,  1.3D-28, r^2= 1.5D+01
   Bfn.  Coefficient  Atom+Function         Bfn.  Coefficient  Atom+Function  
  ----- ------------  ---------------      ----- ------------  ---------------
    37      3.449203  1 Au py                34     -2.928930  1 Au py         
    40     -1.465915  1 Au py                31      0.678850  1 Au py         
    25      0.293066  1 Au py                28     -0.224024  1 Au py         
 
 Vector   32  Occ=0.000000D+00  E= 1.134408D-01  Symmetry=b1u
              MO Center= -2.1D-29,  2.3D-29,  1.7D-14, r^2= 1.5D+01
   Bfn.  Coefficient  Atom+Function         Bfn.  Coefficient  Atom+Function  
  ----- ------------  ---------------      ----- ------------  ---------------
    38      3.449203  1 Au pz                35     -2.928930  1 Au pz         
    41     -1.465915  1 Au pz                32      0.678850  1 Au pz         
    26      0.293066  1 Au pz                29     -0.224024  1 Au pz         
 
 Vector   33  Occ=0.000000D+00  E= 1.657851D-01  Symmetry=ag
              MO Center=  3.6D-15, -7.3D-15,  1.4D-15, r^2= 2.2D+01
   Bfn.  Coefficient  Atom+Function         Bfn.  Coefficient  Atom+Function  
  ----- ------------  ---------------      ----- ------------  ---------------
     8     11.273819  1 Au s                  9     -9.477172  1 Au s          
     7     -7.531369  1 Au s                 10      4.977360  1 Au s          
     6      2.351631  1 Au s                 11     -1.378540  1 Au s          
     5     -0.762507  1 Au s                  4      0.701169  1 Au s          
     2     -0.194479  1 Au s          
 
 Vector   34  Occ=0.000000D+00  E= 4.669842D-01  Symmetry=ag
              MO Center=  9.9D-22, -2.7D-20, -1.3D-21, r^2= 7.0D+00
   Bfn.  Coefficient  Atom+Function         Bfn.  Coefficient  Atom+Function  
  ----- ------------  ---------------      ----- ------------  ---------------
    71      2.204840  1 Au d  2              76     -1.705734  1 Au d  2       
    66     -0.753111  1 Au d  2              81      0.618145  1 Au d  2       
    56     -0.181088  1 Au d  2       
 
 Vector   35  Occ=0.000000D+00  E= 4.669842D-01  Symmetry=b2g
              MO Center=  6.7D-30, -2.1D-31,  7.3D-30, r^2= 7.0D+00
   Bfn.  Coefficient  Atom+Function         Bfn.  Coefficient  Atom+Function  
  ----- ------------  ---------------      ----- ------------  ---------------
    70      2.204840  1 Au d  1              75     -1.705735  1 Au d  1       
    65     -0.753111  1 Au d  1              80      0.618145  1 Au d  1       
    55     -0.181088  1 Au d  1       
 
 Vector   36  Occ=0.000000D+00  E= 4.669842D-01  Symmetry=b3g
              MO Center= -3.1D-31, -9.1D-30, -1.2D-29, r^2= 7.0D+00
   Bfn.  Coefficient  Atom+Function         Bfn.  Coefficient  Atom+Function  
  ----- ------------  ---------------      ----- ------------  ---------------
    68      2.204840  1 Au d -1              73     -1.705735  1 Au d -1       
    63     -0.753111  1 Au d -1              78      0.618145  1 Au d -1       
    53     -0.181088  1 Au d -1       
 
 Vector   37  Occ=0.000000D+00  E= 4.669842D-01  Symmetry=b1g
              MO Center= -1.4D-29, -2.2D-30,  7.0D-32, r^2= 7.0D+00
   Bfn.  Coefficient  Atom+Function         Bfn.  Coefficient  Atom+Function  
  ----- ------------  ---------------      ----- ------------  ---------------
    67      2.204840  1 Au d -2              72     -1.705735  1 Au d -2       
    62     -0.753111  1 Au d -2              77      0.618145  1 Au d -2       
    52     -0.181088  1 Au d -2       
 
 Vector   38  Occ=0.000000D+00  E= 4.669842D-01  Symmetry=ag
              MO Center= -2.2D-17, -1.4D-16,  4.0D-16, r^2= 7.0D+00
   Bfn.  Coefficient  Atom+Function         Bfn.  Coefficient  Atom+Function  
  ----- ------------  ---------------      ----- ------------  ---------------
    69      2.204840  1 Au d  0              74     -1.705734  1 Au d  0       
    64     -0.753111  1 Au d  0              79      0.618145  1 Au d  0       
    54     -0.181088  1 Au d  0       
 
 Vector   39  Occ=0.000000D+00  E= 5.011874D-01  Symmetry=b3u
              MO Center=  7.7D-20, -2.4D-32,  1.1D-35, r^2= 3.0D+00
   Bfn.  Coefficient  Atom+Function         Bfn.  Coefficient  Atom+Function  
  ----- ------------  ---------------      ----- ------------  ---------------
   102      0.997316  1 Au f  3       
 

 center of mass
 --------------
 x =   0.00000000 y =   0.00000000 z =   0.00000000

 moments of inertia (a.u.)
 ------------------
           0.000000000000           0.000000000000           0.000000000000
           0.000000000000           0.000000000000           0.000000000000
           0.000000000000           0.000000000000           0.000000000000
 
  Mulliken analysis of the total density
  --------------------------------------

    Atom       Charge   Shell Charges
 -----------   ------   -------------------------------------------------------
    1 Au  19    18.00   0.05 -0.52  0.33  1.71  0.42  0.02 -0.01  0.00 -0.00  0.00 -0.00 -0.00  0.03 -0.68  1.34  4.07  1.16  0.09 -0.01  0.00 -0.00  0.00 -0.25  1.86  4.77
  2.97  0.64  0.00  0.00  0.00 -0.00  0.00  0.00  0.00  0.00
 
       Multipole analysis of the density wrt the origin
       ------------------------------------------------
 
     L   x y z        total         open         nuclear
     -   - - -        -----         ----         -------
     0   0 0 0      1.000000      0.000000     19.000000
 
     1   1 0 0      0.000000      0.000000      0.000000
     1   0 1 0      0.000000      0.000000      0.000000
     1   0 0 1     -0.000000      0.000000      0.000000
 
     2   2 0 0    -12.935383      0.000000      0.000000
     2   1 1 0      0.000000      0.000000      0.000000
     2   1 0 1     -0.000000      0.000000      0.000000
     2   0 2 0    -12.935383      0.000000      0.000000
     2   0 1 1     -0.000000      0.000000      0.000000
     2   0 0 2    -12.935383      0.000000      0.000000
 

 Parallel integral file used      92 records with       0 large values

                   NWChem MP2 Semi-direct Energy/Gradient Module
                   ---------------------------------------------
 
 
               Au+, Au(14s,10p,8d,3f,2g,1h) -> [11s,10p,8d,3f,2g,1h]
 
 
  Basis functions       =    131
  Molecular orbitals    =    131
  Frozen core           =      0
  Frozen virtuals       =      0
  Active alpha occupied =      9
  Active beta occupied  =      9
  Active alpha virtual  =    122
  Active beta virtual   =    122
  Use MO symmetry       = T
  Use skeleton AO sym   = T

  AO/Fock/Back tols     =   1.0D-09  1.0D-09  1.0D-09

 GA uses MA = F    GA memory limited = T

 Available: 
  local mem=  2.61D+07
 global mem=  2.62D+07
 local disk=  1.19D+14
  mp2_memr nvloc                      9
  nvloc new                      9
   1 passes of   9:        7646941                     138015                   1701538.
 
 Semi-direct pass number   1 of   1  for RHF alpha+beta  at        5.9s
  vrange nnbf                   8646
Node 0 wrote      5.6 Mb in      0.1 s     Agg I/O rate:   931.4 Mb/s
 Done moints_semi at        7.7s
 Done maket at        8.0s
 Done multipass loop at        8.0s


          -------------------------------------------
          SCF energy                -134.684334043865
          Correlation energy          -0.677993809582
          Singlet pairs               -0.368808470147
          Triplet pairs               -0.309185339435
          Total MP2 energy          -135.362327853447
          -------------------------------------------



          ---------------------------------------------------
                    Spin Component Scaled (SCS) MP2
          Same spin pairs                     -0.206123559623
          Same spin scaling factor             0.333333333333
          Opposite spin pairs                 -0.471870249959
          Opposite spin scaling fact.          1.200000000000
          SCS-MP2 correlation energy          -0.634952153159
          Total SCS-MP2 energy              -135.319286197023
          ---------------------------------------------------

 -----------------------
 Performance information
 -----------------------

 Timer overhead =  3.06D-07 seconds/call

               Nr. of calls         CPU time (s)                 Wall time (s)                GFlops
             ---------------    -------------------     ------------------------------   -------------------
Name         Min   Avg   Max    Min     Avg     Max     Min     Avg     Max   Mx/calls   Min     Max     Sum
mp2: moin     1     1     1    1.3     1.4     1.4      1.7     1.7     1.7     1.7      0.0     0.0     0.0   
mp2: make     1     1     1   0.20    0.30    0.32     0.32    0.32    0.32    0.32      0.0     0.0     0.0   
mp2: tota     1     1     1    2.1     2.2     2.3      3.6     3.6     3.6     3.6      0.0     0.0     0.0   

 The average no. of pstat calls per process was 3.00D+00
 with a timing overhead of 9.17D-07s


 Task  times  cpu:        4.6s     wall:        7.5s
 
 
                                NWChem Input Module
                                -------------------
 
 
                                 NWChem SCF Module
                                 -----------------
 
 
               Au+, Au(14s,10p,8d,3f,2g,1h) -> [11s,10p,8d,3f,2g,1h]
 
 

  ao basis        = "ao basis"
  functions       =   131
  atoms           =     1
  closed shells   =     9
  open shells     =     0
  charge          =   1.00
  wavefunction    = RHF 
  input vectors   = /projects/ccrstaff/general/nikolays/huey/tmp/nwchem.mMfYjJzv0/Au+.movecs
  output vectors  = /projects/ccrstaff/general/nikolays/huey/tmp/nwchem.mMfYjJzv0/Au+.movecs
  use symmetry    = T
  symmetry adapt  = T


 Summary of "ao basis" -> "ao basis" (spherical)
 ------------------------------------------------------------------------------
       Tag                 Description            Shells   Functions and Types
 ---------------- ------------------------------  ------  ---------------------
 Au                      user specified             35      131   11s10p8d3f2g1h


      Symmetry analysis of basis
      --------------------------
 
        ag         33
        au          5
        b1g        12
        b1u        19
        b2g        12
        b2u        19
        b3g        12
        b3u        19
 

  The SCF is already converged 

         Total SCF energy =   -134.684334043865

                          Direct MP2
                          ----------
          Basis functions:                      131
          Shells:                                35
          Block length:                          32
          Active occupied range:           1 -    9
          Active virtual range:           10 -  131
          MO coefficients read from:  /projects/ccrstaff/genera
          Operator matrices in core:             45
          AO passes required:                     1
          Use AO Integral blocking
          Twofold algorithm used

     Pass:    1     Index range:    1  -    9     Time:      1.12


          -------------------------------------------
          SCF energy                -134.684334043865
          Correlation energy          -0.677993809582
          Total MP2 energy          -135.362327853447
          -------------------------------------------


          Total MP2 time:           1.33

 Task  times  cpu:        1.3s     wall:        1.4s
 
 
                                NWChem Input Module
                                -------------------
 
 
                                 NWChem SCF Module
                                 -----------------
 
 
               Au+, Au(14s,10p,8d,3f,2g,1h) -> [11s,10p,8d,3f,2g,1h]
 
 

  ao basis        = "ao basis"
  functions       =   131
  atoms           =     1
  closed shells   =     9
  open shells     =     0
  charge          =   1.00
  wavefunction    = RHF 
  input vectors   = /projects/ccrstaff/general/nikolays/huey/tmp/nwchem.mMfYjJzv0/Au+.movecs
  output vectors  = /projects/ccrstaff/general/nikolays/huey/tmp/nwchem.mMfYjJzv0/Au+.movecs
  use symmetry    = T
  symmetry adapt  = T


 Summary of "ao basis" -> "ao basis" (spherical)
 ------------------------------------------------------------------------------
       Tag                 Description            Shells   Functions and Types
 ---------------- ------------------------------  ------  ---------------------
 Au                      user specified             35      131   11s10p8d3f2g1h


      Symmetry analysis of basis
      --------------------------
 
        ag         33
        au          5
        b1g        12
        b1u        19
        b2g        12
        b2u        19
        b3g        12
        b3u        19
 

  The SCF is already converged 

         Total SCF energy =   -134.684334043865

 
 
                   Four-Index Transformation
                   -------------------------
          Number of basis functions:            131
          Number of shells:                      35
          Number of occupied orbitals:            9
          Number of occ. correlated orbitals:     9
          Block length:                          16
          Superscript MO index range:      1 -    9
          Subscript MO index range:        1 -  131
          MO coefficients read from:  /projects/ccrstaff/genera
          Number of operator matrices in core:   90
          Half-transformed integrals produced
 
     Pass:    1     Index range:    1  -    9     Time:      1.33
 ------------------------------------------
 MP2 Energy (coupled cluster initial guess)
 ------------------------------------------
 Reference energy:           -134.684334043864766
 MP2 Corr. energy:             -0.677993809582498
 Total MP2 energy:           -135.362327853447255


 ****************************************************************************
              the segmented parallel ccsd program:   14 nodes
 ****************************************************************************




 level of theory    ccsd(t)
 number of core         0
 number of occupied     9
 number of virtual    122
 number of deleted      0
 total functions      131
 number of shells      35
 basis label          566



   ***** ccsd parameters *****
   iprt   =     0
   convi  =  0.100E-05
   maxit  =    20
   mxvec  =     5
 memory              26131316
  Using  1 OpenMP thread(s) in CCSD
  IO offset    20.0000000000000     
  IO error message >End of File
  file_read_ga: failing reading from 
 /projects/ccrstaff/general/nikolays/huey/tmp/nwchem.mMfYjJzv0/Au+.t2
  Failed reading restart vector from 
 /projects/ccrstaff/general/nikolays/huey/tmp/nwchem.mMfYjJzv0/Au+.t2
  Using MP2 initial guess vector 


-------------------------------------------------------------------------
 iter     correlation     delta       rms       T2     Non-T2      Main
             energy      energy      error      ampl     ampl      Block
                                                time     time      time
-------------------------------------------------------------------------
   1     -0.6420739924 -6.421D-01  2.902D-01     5.87     0.00     5.21
   2     -0.6552098617 -1.314D-02  1.363D-01     1.56     0.00     0.98
   3     -0.6540423246  1.168D-03  1.853D-03     1.59     0.00     1.01
   4     -0.6542419639 -1.996D-04  1.597D-03     1.56     0.00     0.98
   5     -0.6543760779 -1.341D-04  8.154D-04     1.55     0.00     0.98
   6     -0.6543564878  1.959D-05  4.216D-04     1.59     0.00     0.98
   7     -0.6543542229  2.265D-06  4.689D-05     1.64     0.00     1.00
   8     -0.6543546249 -4.020D-07  3.892D-05     1.58     0.00     0.98
   9     -0.6543546765 -5.168D-08  2.211D-06     1.59     0.00     1.01
  10     -0.6543547190 -4.244D-08  2.341D-06     1.74     0.00     1.04
  11     -0.6543547315 -1.251D-08  8.676D-08     1.54     0.00     0.98
                  *************converged*************
-------------------------------------------------------------------------

 -----------
 CCSD Energy
 -----------
 Reference energy:            -134.684334043864766
 CCSD corr. energy:             -0.654354731481166
 Total CCSD energy:           -135.338688775345929


 --------------------------------
 Spin Component Scaled (SCS) CCSD
 --------------------------------
 Same spin contribution:                 -0.183053878134392
 Same spin scaling factor:                1.130000000000000
 Opposite spin contribution:             -0.471300853346773
 Opposite spin scaling fact.:             1.270000000000000
 SCS-CCSD correlation energy:            -0.805402966042265
 Total SCS-CCSD energy:                -135.489737009907032
 memory              26131316


*********triples calculation*********

nkpass=    1; nvpass=    1; memdrv=         646966; memtrn=        9566310; memavail=       26130196
 memory available/node                       26130196
 total number of virtual orbitals       122
 number of virtuals per integral pass   122
 number of integral evaluations           1
 number of occupied per triples pass      9
 number of triples passes                 1

 commencing integral evaluation        1 at          40.35
  symmetry use  T
 commencing triples evaluation - blocking       1
 ccsd(t): done        1 out of      122 progress:    0.8%
 ccsd(t): done        2 out of      122 progress:    1.6%
 ccsd(t): done        3 out of      122 progress:    2.5%
 ccsd(t): done        4 out of      122 progress:    3.3%
 ccsd(t): done        5 out of      122 progress:    4.1%
 ccsd(t): done        6 out of      122 progress:    4.9%
 ccsd(t): done        7 out of      122 progress:    5.7%
 ccsd(t): done        8 out of      122 progress:    6.6%
 ccsd(t): done        9 out of      122 progress:    7.4%
 ccsd(t): done       10 out of      122 progress:    8.2%
 ccsd(t): done       11 out of      122 progress:    9.0%
 ccsd(t): done       12 out of      122 progress:    9.8%
 ccsd(t): done       13 out of      122 progress:   10.7%
 ccsd(t): done       14 out of      122 progress:   11.5%
 ccsd(t): done       15 out of      122 progress:   12.3%
 ccsd(t): done       16 out of      122 progress:   13.1%
 ccsd(t): done       17 out of      122 progress:   13.9%
 ccsd(t): done       18 out of      122 progress:   14.8%
 ccsd(t): done       19 out of      122 progress:   15.6%
 ccsd(t): done       20 out of      122 progress:   16.4%
 ccsd(t): done       21 out of      122 progress:   17.2%
 ccsd(t): done       22 out of      122 progress:   18.0%
 ccsd(t): done       23 out of      122 progress:   18.9%
 ccsd(t): done       24 out of      122 progress:   19.7%
 ccsd(t): done       25 out of      122 progress:   20.5%
 ccsd(t): done       26 out of      122 progress:   21.3%
 ccsd(t): done       27 out of      122 progress:   22.1%
 ccsd(t): done       28 out of      122 progress:   23.0%
 ccsd(t): done       29 out of      122 progress:   23.8%
 ccsd(t): done       30 out of      122 progress:   24.6%
 ccsd(t): done       31 out of      122 progress:   25.4%
 ccsd(t): done       32 out of      122 progress:   26.2%
 ccsd(t): done       33 out of      122 progress:   27.0%
 ccsd(t): done       34 out of      122 progress:   27.9%
 ccsd(t): done       35 out of      122 progress:   28.7%
 ccsd(t): done       36 out of      122 progress:   29.5%
 ccsd(t): done       37 out of      122 progress:   30.3%
 ccsd(t): done       38 out of      122 progress:   31.1%
 ccsd(t): done       39 out of      122 progress:   32.0%
 ccsd(t): done       40 out of      122 progress:   32.8%
 ccsd(t): done       41 out of      122 progress:   33.6%
 ccsd(t): done       42 out of      122 progress:   34.4%
 ccsd(t): done       43 out of      122 progress:   35.2%
 ccsd(t): done       44 out of      122 progress:   36.1%
 ccsd(t): done       45 out of      122 progress:   36.9%
 ccsd(t): done       46 out of      122 progress:   37.7%
 ccsd(t): done       47 out of      122 progress:   38.5%
 ccsd(t): done       48 out of      122 progress:   39.3%
 ccsd(t): done       49 out of      122 progress:   40.2%
 ccsd(t): done       50 out of      122 progress:   41.0%
 ccsd(t): done       51 out of      122 progress:   41.8%
 ccsd(t): done       52 out of      122 progress:   42.6%
 ccsd(t): done       53 out of      122 progress:   43.4%
 ccsd(t): done       54 out of      122 progress:   44.3%
 ccsd(t): done       55 out of      122 progress:   45.1%
 ccsd(t): done       56 out of      122 progress:   45.9%
 ccsd(t): done       57 out of      122 progress:   46.7%
 ccsd(t): done       58 out of      122 progress:   47.5%
 ccsd(t): done       59 out of      122 progress:   48.4%
 ccsd(t): done       60 out of      122 progress:   49.2%
 ccsd(t): done       61 out of      122 progress:   50.0%
 ccsd(t): done       62 out of      122 progress:   50.8%
 ccsd(t): done       63 out of      122 progress:   51.6%
 ccsd(t): done       64 out of      122 progress:   52.5%
 ccsd(t): done       65 out of      122 progress:   53.3%
 ccsd(t): done       66 out of      122 progress:   54.1%
 ccsd(t): done       67 out of      122 progress:   54.9%
 ccsd(t): done       68 out of      122 progress:   55.7%
 ccsd(t): done       69 out of      122 progress:   56.6%
 ccsd(t): done       70 out of      122 progress:   57.4%
 ccsd(t): done       71 out of      122 progress:   58.2%
 ccsd(t): done       72 out of      122 progress:   59.0%
 ccsd(t): done       73 out of      122 progress:   59.8%
 ccsd(t): done       74 out of      122 progress:   60.7%
 ccsd(t): done       75 out of      122 progress:   61.5%
 ccsd(t): done       76 out of      122 progress:   62.3%
 ccsd(t): done       77 out of      122 progress:   63.1%
 ccsd(t): done       78 out of      122 progress:   63.9%
 ccsd(t): done       79 out of      122 progress:   64.8%
 ccsd(t): done       80 out of      122 progress:   65.6%
 ccsd(t): done       81 out of      122 progress:   66.4%
 ccsd(t): done       82 out of      122 progress:   67.2%
 ccsd(t): done       83 out of      122 progress:   68.0%
 ccsd(t): done       84 out of      122 progress:   68.9%
 ccsd(t): done       85 out of      122 progress:   69.7%
 ccsd(t): done       86 out of      122 progress:   70.5%
 ccsd(t): done       87 out of      122 progress:   71.3%
 ccsd(t): done       88 out of      122 progress:   72.1%
 ccsd(t): done       89 out of      122 progress:   73.0%
 ccsd(t): done       90 out of      122 progress:   73.8%
 ccsd(t): done       91 out of      122 progress:   74.6%
 ccsd(t): done       92 out of      122 progress:   75.4%
 ccsd(t): done       93 out of      122 progress:   76.2%
 ccsd(t): done       94 out of      122 progress:   77.0%
 ccsd(t): done       95 out of      122 progress:   77.9%
 ccsd(t): done       96 out of      122 progress:   78.7%
 ccsd(t): done       97 out of      122 progress:   79.5%
 ccsd(t): done       98 out of      122 progress:   80.3%
 ccsd(t): done       99 out of      122 progress:   81.1%
 ccsd(t): done      100 out of      122 progress:   82.0%
 ccsd(t): done      101 out of      122 progress:   82.8%
 ccsd(t): done      102 out of      122 progress:   83.6%
 ccsd(t): done      103 out of      122 progress:   84.4%
 ccsd(t): done      104 out of      122 progress:   85.2%
 ccsd(t): done      105 out of      122 progress:   86.1%
 ccsd(t): done      106 out of      122 progress:   86.9%
 ccsd(t): done      107 out of      122 progress:   87.7%
 ccsd(t): done      108 out of      122 progress:   88.5%
 ccsd(t): done      109 out of      122 progress:   89.3%
 ccsd(t): done      110 out of      122 progress:   90.2%
 ccsd(t): done      111 out of      122 progress:   91.0%
 ccsd(t): done      112 out of      122 progress:   91.8%
 ccsd(t): done      113 out of      122 progress:   92.6%
 ccsd(t): done      114 out of      122 progress:   93.4%
 ccsd(t): done      115 out of      122 progress:   94.3%
 ccsd(t): done      116 out of      122 progress:   95.1%
 ccsd(t): done      117 out of      122 progress:   95.9%
 ccsd(t): done      118 out of      122 progress:   96.7%
 ccsd(t): done      119 out of      122 progress:   97.5%
 ccsd(t): done      120 out of      122 progress:   98.4%
 ccsd(t): done      121 out of      122 progress:   99.2%
 ccsd(t): done      122 out of      122 progress:  100.0%
 Time for integral evaluation pass     1    11.40
 Time for triples evaluation pass      1    18.58

 pseudo-e(mp4)  -0.20388563014299E-01
 pseudo-e(mp5)   0.23839121501395E-03
        e(t)    -0.20150171799285E-01

 --------------
 CCSD(T) Energy
 --------------
 Reference energy:                    -134.684334043864766

 CCSD corr. energy:                     -0.654354731481166
 T(CCSD) corr. energy:                  -0.020388563014299
 Total CCSD+T(CCSD) energy:           -135.359077338360237

 CCSD corr. energy:                     -0.654354731481166
 (T) corr. energy:                      -0.020150171799285
 Total CCSD(T) energy:                -135.358838947145216
 
 routine      calls  cpu(0)   cpu-min  cpu-ave  cpu-max   i/o 
 aoccsd          1     0.16     0.16     0.16     0.16    0.00
 iterdrv         1     7.25     7.25     7.25     7.25    0.00
 pampt          11     0.77     0.77     0.77     0.77    0.00
 t2pm           11     0.27     0.27     0.27     0.27    0.00
 sxy            11     0.85     0.17     1.59     2.70    0.00
 ints        28350     3.70     3.23     3.59     4.21    0.00
 f_write        90     0.07     0.05     0.06     0.07    0.00
 t2eri         495     8.68     7.48     8.06     8.72    0.00
 idx2          495     1.28     1.23     1.32     1.43    0.00
 idx34          11     0.14     0.11     0.14     0.16    0.00
 ht2pm          11     0.61     0.61     0.61     0.61    0.00
 itm            11     5.02     5.02     5.02     5.02    0.00
 pdiis          11     0.02     0.01     0.02     0.02    0.00
 r_read        450     0.41     0.32     0.37     0.42    0.00
 triples         1     0.04     0.04     0.04     0.04    0.00
 rdtrpo          1     0.07     0.07     0.07     0.07    0.00
 trpmos          1    11.40    11.40    11.40    11.40    0.00
 trpdrv          1     1.21     1.09     1.41     1.66    0.00
 dovvv        7110    13.44    12.99    13.33    13.73    0.00
 doooo        7110     1.64     1.60     1.63     1.67    0.00
 tengy        6399     2.28     2.02     2.20     2.40    0.00
 Total                59.31    59.31    59.31    59.32    0.00

 Task  times  cpu:       52.3s     wall:       60.9s
 
 
                                NWChem Input Module
                                -------------------
 
 
 Summary of allocated global arrays
-----------------------------------
  No active global arrays



                         GA Statistics for process    0
                         ------------------------------

       create   destroy   get      put      acc     scatter   gather  read&inc
calls:  580      580     4.86e+04 3.22e+04 4.44e+05    0        0     5.46e+04 
number of processes/call 1.45e+00 1.44e+00 1.04e+00 0.00e+00 0.00e+00
bytes total:             1.54e+09 2.53e+08 1.06e+09 0.00e+00 0.00e+00 4.37e+05
bytes remote:            9.95e+08 1.05e+08 8.68e+08 0.00e+00 0.00e+00 0.00e+00
Max memory consumed for GA by this process: 28866496 bytes
 
MA_summarize_allocated_blocks: starting scan ...
MA_summarize_allocated_blocks: scan completed: 0 heap blocks, 0 stack blocks
MA usage statistics:

        allocation statistics:
                                              heap           stack
                                              ----           -----
        current number of blocks                 0               0
        maximum number of blocks                40              42
        current total bytes                      0               0
        maximum total bytes                8389344       193464456
        maximum total K-bytes                 8390          193465
        maximum total M-bytes                    9             194
 
 
                                     CITATION
                                     --------
                Please cite the following reference when publishing
                           results obtained with NWChem:
 
                 M. Valiev, E.J. Bylaska, N. Govind, K. Kowalski,
              T.P. Straatsma, H.J.J. van Dam, D. Wang, J. Nieplocha,
                        E. Apra, T.L. Windus, W.A. de Jong
                 "NWChem: a comprehensive and scalable open-source
                  solution for large scale molecular simulations"
                      Comput. Phys. Commun. 181, 1477 (2010)
                           doi:10.1016/j.cpc.2010.04.018
 
                                      AUTHORS
                                      -------
          E. Apra, E. J. Bylaska, W. A. de Jong, N. Govind, K. Kowalski,
       T. P. Straatsma, M. Valiev, H. J. J. van Dam, D. Wang, T. L. Windus,
        J. Hammond, J. Autschbach, K. Bhaskaran-Nair, J. Brabec, K. Lopata,
    S. A. Fischer, S. Krishnamoorthy, M. Jacquelin, W. Ma, M. Klemm, O. Villa,
      Y. Chen, V. Anisimov, F. Aquino, S. Hirata, M. T. Hackler, V. Konjkov,
            D. Mejia-Rodriguez, T. Risthaus, M. Malagoli, A. Marenich,
   A. Otero-de-la-Roza, J. Mullin, P. Nichols, R. Peverati, J. Pittner, Y. Zhao,
        P.-D. Fan, A. Fonari, M. J. Williamson, R. J. Harrison, J. R. Rehr,
      M. Dupuis, D. Silverstein, D. M. A. Smith, J. Nieplocha, V. Tipparaju,
    M. Krishnan, B. E. Van Kuiken, A. Vazquez-Mayagoitia, L. Jensen, M. Swart,
      Q. Wu, T. Van Voorhis, A. A. Auer, M. Nooijen, L. D. Crosby, E. Brown,
      G. Cisneros, G. I. Fann, H. Fruchtl, J. Garza, K. Hirao, R. A. Kendall,
      J. A. Nichols, K. Tsemekhman, K. Wolinski, J. Anchell, D. E. Bernholdt,
      P. Borowski, T. Clark, D. Clerc, H. Dachsel, M. J. O. Deegan, K. Dyall,
    D. Elwood, E. Glendening, M. Gutowski, A. C. Hess, J. Jaffe, B. G. Johnson,
     J. Ju, R. Kobayashi, R. Kutteh, Z. Lin, R. Littlefield, X. Long, B. Meng,
      T. Nakajima, S. Niu, L. Pollack, M. Rosing, K. Glaesemann, G. Sandrone,
      M. Stave, H. Taylor, G. Thomas, J. H. van Lenthe, A. T. Wong, Z. Zhang.

 Total times  cpu:       58.3s     wall:       70.7
```