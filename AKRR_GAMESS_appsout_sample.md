Example of appstdout from NWChem

```text
===ExeBinSignature=== MD5: 0202e1df231e67fe703d707828cb721b /util/academic/gamess/11Nov2017R3/impi/gamess/gamess.01.x
===ExeBinSignature=== MD5: e1940558f29370193cc3079b71372f50 /util/academic/intel/18.0/compilers_and_libraries_2018.1.163/linux/mpi/intel64/lib/libmpi.so.12
===ExeBinSignature=== MD5: 0f65391c22de4d15744ea80ec857419a /util/academic/intel/18.0/compilers_and_libraries_2018.1.163/linux/mpi/intel64/lib/libmpifort.so.12
===ExeBinSignature=== MD5: 5928d7f9554dde0b45bc87ac09598ad0 /lib64/librt.so.1
===ExeBinSignature=== MD5: 23902bbccc0e350c1fdf09d070f3cd48 /lib64/libpthread.so.0
===ExeBinSignature=== MD5: 2705d15430ebce01274ef94967122bcb /lib64/libm.so.6
===ExeBinSignature=== MD5: a2737e5fc2c2059bd357ef6015c99262 /lib64/libc.so.6
===ExeBinSignature=== MD5: c8f2c137eee1a4581bc0be7b63d2c603 /lib64/libgcc_s.so.1
===ExeBinSignature=== MD5: bbb4814755042554781fce1b1da6fdb1 /lib64/libdl.so.2
Attempt to launch GAMESS: 0
----- GAMESS execution script 'rungms' -----
This job is running on host cpn-d15-13.cbls.ccr.buffalo.edu
under operating system Linux at Wed May 1 12:06:31 EDT 2019
 SLURM has assigned the following compute nodes to this run:
cpn-d15-13.cbls.ccr.buffalo.edu
cpn-d15-14.cbls.ccr.buffalo.edu
Available scratch disk space (Kbyte units) at beginning of the job is
Filesystem     1K-blocks  Used Available Use% Mounted on
/dev/md0       224736032 33568 224702464   1% /scratch
GAMESS temporary binary files will be written to /scratch/11369048
GAMESS supplementary output files will be written to /projects/ccrstaff/general/nikolays/huey/tmp/gamess.5esQ3XtNU
Copying input file c8h10-cct-mp2.inp to your run's scratch directory...
cp c8h10-cct-mp2.inp /scratch/11369048/c8h10-cct-mp2.F05
unset echo
Setting  NNODES=2
setenv I_MPI_WAIT_MODE enable
setenv I_MPI_PIN disable
setenv I_MPI_DEBUG 0
setenv I_MPI_STATS 0
setenv I_MPI_SHM_LMT shm
setenv I_MPI_FABRICS tcp
unset echo
MPI kickoff will run GAMESS on 2 cores in 2 nodes.
The binary to be executed is /util/academic/gamess/11Nov2017R3/impi/gamess/gamess.01.x
MPI will run 2 compute processes and 2 data servers,
    placing 8 of each process type onto each node.
The scratch disk space on each node is /scratch/11369048, with free space
Filesystem     1K-blocks  Used Available Use% Mounted on
/dev/md0       224736032 36548 224699484   1% /scratch
RUNGMS  launching GAMESS with srun
NNODES=2
NPROCS=4
srun --overcommit --nodes=2 --ntasks=4 --ntasks-per-core=2 /util/academic/gamess/18Aug2016R1/impi/gamess/gamess.01.x
          ******************************************************
          *         GAMESS VERSION = 18 AUG 2016 (R1)          *
          *             FROM IOWA STATE UNIVERSITY             *
          * M.W.SCHMIDT, K.K.BALDRIDGE, J.A.BOATZ, S.T.ELBERT, *
          *   M.S.GORDON, J.H.JENSEN, S.KOSEKI, N.MATSUNAGA,   *
          *          K.A.NGUYEN, S.J.SU, T.L.WINDUS,           *
          *       TOGETHER WITH M.DUPUIS, J.A.MONTGOMERY       *
          *         J.COMPUT.CHEM.  14, 1347-1363(1993)        *
          **************** 64 BIT INTEL VERSION ****************

  SINCE 1993, STUDENTS AND POSTDOCS WORKING AT IOWA STATE UNIVERSITY
  AND ALSO IN THEIR VARIOUS JOBS AFTER LEAVING ISU HAVE MADE IMPORTANT
  CONTRIBUTIONS TO THE CODE:
     IVANA ADAMOVIC, CHRISTINE AIKENS, YURI ALEXEEV, POOJA ARORA,
     ANDREY ASADCHEV, ROB BELL, PRADIPTA BANDYOPADHYAY, JONATHAN BENTZ,
     BRETT BODE, KURT BRORSEN, CALEB CARLIN, GALINA CHABAN, WEI CHEN,
     CHEOL HO CHOI, PAUL DAY, ALBERT DEFUSCO, NUWAN DESILVA, TIM DUDLEY,
     DMITRI FEDOROV, GRAHAM FLETCHER, MARK FREITAG, KURT GLAESEMANN,
     DAN KEMP, GRANT MERRILL, NORIYUKI MINEZAWA, JONATHAN MULLIN,
     TAKESHI NAGATA, SEAN NEDD, HEATHER NETZLOFF, BOSILJKA NJEGIC, RYAN OLSON,
     MIKE PAK, SPENCER PRUITT, LUKE ROSKOP, JIM SHOEMAKER, LYUDMILA SLIPCHENKO,
     TONY SMITH, SAROM SOK LEANG, JIE SONG, TETSUYA TAKETSUGU, SIMON WEBB,
     PENG XU, SOOHAENG YOO, FEDERICO ZAHARIEV

  ADDITIONAL CODE HAS BEEN PROVIDED BY COLLABORATORS IN OTHER GROUPS:
     IOWA STATE UNIVERSITY:
          JOE IVANIC, AARON WEST, LAIMUTIS BYTAUTAS, KLAUS RUEDENBERG
     UNIVERSITY OF TOKYO: KIMIHIKO HIRAO, TAKAHITO NAKAJIMA,
          TAKAO TSUNEDA, MUNEAKI KAMIYA, SUSUMU YANAGISAWA,
          KIYOSHI YAGI, MAHITO CHIBA, SEIKEN TOKURA, NAOAKI KAWAKAMI
     UNIVERSITY OF AARHUS: FRANK JENSEN
     UNIVERSITY OF IOWA: VISVALDAS KAIRYS, HUI LI
     NATIONAL INST. OF STANDARDS AND TECHNOLOGY: WALT STEVENS, DAVID GARMER
     UNIVERSITY OF PISA: BENEDETTA MENNUCCI, JACOPO TOMASI
     UNIVERSITY OF MEMPHIS: HENRY KURTZ, PRAKASHAN KORAMBATH
     UNIVERSITY OF ALBERTA: TOBY ZENG, MARIUSZ KLOBUKOWSKI
     UNIVERSITY OF NEW ENGLAND: MARK SPACKMAN
     MIE UNIVERSITY: HIROAKI UMEDA
     NAT. INST. OF ADVANCED INDUSTRIAL SCIENCE AND TECHNOLOGY: KAZUO KITAURA
     MICHIGAN STATE UNIVERSITY:
          KAROL KOWALSKI, MARTA WLOCH, JEFFREY GOUR, JESSE LUTZ,
          WEI LI, PIOTR PIECUCH
     UNIVERSITY OF SILESIA: MONIKA MUSIAL, STANISLAW KUCHARSKI
     FACULTES UNIVERSITAIRES NOTRE-DAME DE LA PAIX:
          OLIVIER QUINET, BENOIT CHAMPAGNE
     UNIVERSITY OF CALIFORNIA - SANTA BARBARA: BERNARD KIRTMAN
     INSTITUTE FOR MOLECULAR SCIENCE:
          KAZUYA ISHIMURA, MICHIO KATOUDA, AND SHIGERU NAGASE
     UNIVERSITY OF NOTRE DAME: ANNA POMOGAEVA, DAN CHIPMAN
     KYUSHU UNIVERSITY:
          HARUYUKI NAKANO,
          FENG LONG GU, JACEK KORCHOWIEC, MARCIN MAKOWSKI, AND YURIKO AOKI,
          HIROTOSHI MORI AND EISAKU MIYOSHI
     PENNSYLVANIA STATE UNIVERSITY:
          TZVETELIN IORDANOV, CHET SWALINA, JONATHAN SKONE,
          SHARON HAMMES-SCHIFFER
     WASEDA UNIVERSITY:
          MASATO KOBAYASHI, TOMOKO AKAMA, TSUGUKI TOUMA,
          TAKESHI YOSHIKAWA, YASUHIRO IKABATA, JUNJI SEINO,
          YUYA NAKAJIMA, HIROMI NAKAI
     NANJING UNIVERSITY: SHUHUA LI
     UNIVERSITY OF NEBRASKA:
          PEIFENG SU, DEJUN SI, NANDUN THELLAMUREGE, YALI WANG, HUI LI
     UNIVERSITY OF ZURICH: ROBERTO PEVERATI, KIM BALDRIDGE
     N. COPERNICUS UNIVERSITY AND JACKSON STATE UNIVERSITY:
          MARIA BARYSZ
     UNIVERSITY OF COPENHAGEN: Jimmy Kromann, CASPER STEINMANN
     TOKYO INSTITUTE OF TECHNOLOGY: HIROYA NAKATA
     NAGOYA UNIVERSITY: YOSHIO NISHIMOTO, STEPHAN IRLE
     MOSCOW STATE UNIVERSITY: VLADIMIR MIRONOV


 PARALLEL VERSION RUNNING ON        2 PROCESSORS IN        2 NODES.

 EXECUTION OF GAMESS BEGUN Wed May  1 12:06:33 2019

            ECHO OF THE FIRST FEW INPUT CARDS -
 INPUT CARD> $CONTRL COORD=UNIQUE UNITS=ANGS MAXIT=200 QMTTOL=1.e-5                         
 INPUT CARD>  MPLEVL=2 ICUT=20 ITOL=30 NPRINT=-5 ISPHER=1 $END                              
 INPUT CARD> $SYSTEM MWORDS=100 MEMDDI=100 PARALL=.TRUE. $END                               
 INPUT CARD> $SCF DIRSCF=.TRUE. DAMP=.TRUE. EXTRAP=.TRUE. $END                              
 INPUT CARD> $BASIS GBASIS=CCT $END                                                         
 INPUT CARD> $GUESS GUESS=MOREAD $END                                                       
 INPUT CARD> $DATA                                                                          
 INPUT CARD>C8H10 poly4 appkernel                                                           
 INPUT CARD>C1 1                                                                            
 INPUT CARD>H      1.0     0.00000   0.24400  -1.50072                                      
 INPUT CARD>H      1.0     0.00000  -0.24400   8.90972                                      
 INPUT CARD>C      6.0     0.00000  -0.32417  -0.58578                                      
 INPUT CARD>C      6.0     0.00000   0.32417   0.58578                                      
 INPUT CARD>H      1.0     0.00000  -1.40116  -0.59030                                      
 INPUT CARD>H      1.0     0.00000   1.40116   0.59030                                      
 INPUT CARD>C      6.0     0.00000  -0.32417   1.88388                                      
 INPUT CARD>C      6.0     0.00000   0.32417   3.05545                                      
 INPUT CARD>H      1.0     0.00000  -1.40116   1.87937                                      
 INPUT CARD>H      1.0     0.00000   1.40116   3.05996                                      
 INPUT CARD>C      6.0     0.00000  -0.32417   4.35355                                      
 INPUT CARD>C      6.0     0.00000   0.32417   5.52512                                      
 INPUT CARD>H      1.0     0.00000  -1.40116   4.34903                                      
 INPUT CARD>H      1.0     0.00000   1.40116   5.52963                                      
 INPUT CARD>C      6.0     0.00000  -0.32417   6.82321                                      
 INPUT CARD>C      6.0     0.00000   0.32417   7.99478                                      
 INPUT CARD>H      1.0     0.00000  -1.40116   6.81870                                      
 INPUT CARD>H      1.0     0.00000   1.40116   7.99930                                      
 INPUT CARD> $END                                                                           
 INPUT CARD> $DATA                                                                          
 INPUT CARD>--- CLOSED SHELL ORBITALS --- GENERATED AT Mon Sep 13 11:10:07 2010             
 INPUT CARD>C8H10 poly4 appkernel                                                           
 INPUT CARD>E(RHF)=     -308.8078307750, E(NUC)=  298.6090226575,   11 ITERS                
 INPUT CARD> $VEC                                                                           
 INPUT CARD> 1  1 1.75614928E-05 4.08274012E-04-4.21546037E-05 0.00000000E+00 8.03148234E-06
 INPUT CARD> 1  2-1.06362075E-05 0.00000000E+00-1.22640242E-04 9.47149974E-05 1.98085478E-05
 INPUT CARD> 1  3 1.47755109E-05-6.38869046E-06 0.00000000E+00 0.00000000E+00 1.17026071E-06
 INPUT CARD> 1  4 1.75695298E-05 4.08293599E-04-4.21720415E-05 0.00000000E+00-8.03067712E-06
 INPUT CARD> 1  5 1.06380513E-05 0.00000000E+00 1.22674877E-04-9.46946087E-05 1.98144601E-05
 INPUT CARD> 1  6 1.47818191E-05-6.39683771E-06 0.00000000E+00 0.00000000E+00 1.16750691E-06
 INPUT CARD> 1  7 5.93566861E-03 2.02908544E-04 2.29329414E-04 8.33824094E-04 0.00000000E+00
 INPUT CARD> 1  8-4.44309786E-05 3.55690576E-05 0.00000000E+00 7.23392976E-04 3.14830536E-04
 INPUT CARD> 1  9 0.00000000E+00 3.20795687E-04 2.26794317E-04-2.25744691E-05-2.54842148E-05
 INPUT CARD> 1 10 2.37999280E-05 0.00000000E+00 0.00000000E+00 7.77007628E-06-4.35109911E-05
 INPUT CARD> 1 11-3.96668608E-05-3.99525468E-04 0.00000000E+00 0.00000000E+00 5.04282669E-04
 INPUT CARD> 1 12 0.00000000E+00-1.05746738E-04-1.60600910E-05-3.18447853E-05 2.42020124E-05
 INPUT CARD> 1 13 0.00000000E+00 1.22789471E-05 0.00000000E+00-1.93640992E-05 0.00000000E+00
 INPUT CARD> 1 14 8.65337496E-02 5.26245727E-04 4.20788752E-03-1.26744447E-03 0.00000000E+00
 INPUT CARD> 1 15 8.02965704E-05 1.14116637E-04 0.00000000E+00-6.23951174E-04 5.24786835E-04
 INPUT CARD> 1 16 0.00000000E+00 1.00441038E-04 4.92826997E-04 3.59325681E-05 6.16899161E-05
 INPUT CARD> 1 17 1.71942729E-04 0.00000000E+00 0.00000000E+00 1.01809557E-05 4.37055333E-04
  100000000 WORDS OF MEMORY AVAILABLE

     BASIS OPTIONS
     -------------
     GBASIS=CCT          IGAUSS=       0      POLAR=NONE    
     NDFUNC=       0     NFFUNC=       0     DIFFSP=       F
     NPFUNC=       0      DIFFS=       F     BASNAM=        


     RUN TITLE
     ---------
 C8H10 poly4 appkernel                                                           

 THE POINT GROUP OF THE MOLECULE IS C1      
 THE ORDER OF THE PRINCIPAL AXIS IS     1

 ATOM      ATOMIC                      COORDINATES (BOHR)
           CHARGE         X                   Y                   Z
 H           1.0     0.0000000000        0.4610931410       -2.8359495843
 H           1.0     0.0000000000       -0.4610931410       16.8369294273
 C           6.0     0.0000000000       -0.6125924734       -1.1069636891
 C           6.0     0.0000000000        0.6125924734        1.1069636891
 H           1.0     0.0000000000       -2.6478084650       -1.1155052506
 H           1.0     0.0000000000        2.6478084650        1.1155052506
 C           6.0     0.0000000000       -0.6125924734        3.5600169937
 C           6.0     0.0000000000        0.6125924734        5.7739632692
 H           1.0     0.0000000000       -2.6478084650        3.5514943295
 H           1.0     0.0000000000        2.6478084650        5.7824859334
 C           6.0     0.0000000000       -0.6125924734        8.2270165738
 C           6.0     0.0000000000        0.6125924734       10.4409628493
 H           1.0     0.0000000000       -2.6478084650        8.2184750124
 H           1.0     0.0000000000        2.6478084650       10.4494855135
 C           6.0     0.0000000000       -0.6125924734       12.8939972567
 C           6.0     0.0000000000        0.6125924734       15.1079435321
 H           1.0     0.0000000000       -2.6478084650       12.8854745925
 H           1.0     0.0000000000        2.6478084650       15.1164850936

          INTERNUCLEAR DISTANCES (ANGS.)
          ------------------------------

                1 H          2 H          3 C          4 C          5 H     

   1 H       0.0000000   10.4218715    1.0770016 *  2.0880396 *  1.8802702 *
   2 H      10.4218715    0.0000000    9.4958384    8.3433084    9.5702351  
   3 C       1.0770016 *  9.4958384    0.0000000    1.3389913 *  1.0769995 *
   4 C       2.0880396 *  8.3433084    1.3389913 *  0.0000000    2.0880440 *
   5 H       1.8802702 *  9.5702351    1.0769995 *  2.0880440 *  0.0000000  
   6 H       2.3898502 *  8.4805248    2.0880440 *  1.0769995 *  3.0408574  
   7 C       3.4319578    7.0262974    2.4696600 *  1.4510025 *  2.6984207 *
   8 C       4.5568753    5.8817765    3.6984998    2.4696700 *  4.0333927  
   9 H       3.7591967    7.1249449    2.6901435 *  2.1564180 *  2.4696700 *
  10 H       4.7051909    6.0766968    4.0333837    2.6984207 *  4.6018904  
  11 C       5.8817765    4.5568753    4.9393300    3.8231447    5.0597984  
  12 C       7.0262974    3.4319578    6.1451968    4.9393400    6.3541424  
  13 H       6.0766871    4.7052006    5.0509660    4.1399051    4.9393300  
  14 H       7.1249449    3.7591967    6.3541328    5.0597984    6.7310133  
  15 C       8.3432984    2.0880496 *  7.4089900    6.2710348    7.4913309  
  16 C       9.4958384    1.0770016 *  8.6050192    7.4090000    8.7567324  
  17 H       8.4805248    2.3898502 *  7.4823948    6.4673067    7.4090000  
  18 H       9.5702351    1.8802702 *  8.7567324    7.4913408    9.0351660  

                6 H          7 C          8 C          9 H         10 H     

   1 H       2.3898502 *  3.4319578    4.5568753    3.7591967    4.7051909  
   2 H       8.4805248    7.0262974    5.8817765    7.1249449    6.0766968  
   3 C       2.0880440 *  2.4696600 *  3.6984998    2.6901435 *  4.0333837  
   4 C       1.0769995 *  1.4510025 *  2.4696700 *  2.1564180 *  2.6984207 *
   5 H       3.0408574    2.6984207 *  4.0333927    2.4696700 *  4.6018904  
   6 H       0.0000000    2.1564120 *  2.6901435 *  3.0845905    2.4696600 *
   7 C       2.1564120 *  0.0000000    1.3390000 *  1.0769994 *  2.0880440 *
   8 C       2.6901435 *  1.3390000 *  0.0000000    2.0880440 *  1.0769994 *
   9 H       3.0845905    1.0769994 *  2.0880440 *  0.0000000    3.0408535  
  10 H       2.4696600 *  2.0880440 *  1.0769994 *  3.0408535    0.0000000  
  11 C       4.1399051    2.4696700 *  1.4510025 *  2.6984207 *  2.1564180 *
  12 C       5.0509757    3.6985096    2.4696700 *  4.0333927    2.6901527 *
  13 H       4.6883951    2.6901435 *  2.1564120 *  2.4696600 *  3.0845905  
  14 H       4.9393300    4.0333927    2.6984207 *  4.6018904    2.4696700 *
  15 C       6.4672970    4.9393300    3.8231349    5.0597887    4.1399051  
  16 C       7.4823948    6.1451968    4.9393300    6.3541328    5.0509757  
  17 H       6.8297851    5.0509757    4.1399051    4.9393300    4.6884031  
  18 H       7.4090000    6.3541424    5.0597984    6.7310133    4.9393400  

               11 C         12 C         13 H         14 H         15 C     

   1 H       5.8817765    7.0262974    6.0766871    7.1249449    8.3432984  
   2 H       4.5568753    3.4319578    4.7052006    3.7591967    2.0880496 *
   3 C       4.9393300    6.1451968    5.0509660    6.3541328    7.4089900  
   4 C       3.8231447    4.9393400    4.1399051    5.0597984    6.2710348  
   5 H       5.0597984    6.3541424    4.9393300    6.7310133    7.4913309  
   6 H       4.1399051    5.0509757    4.6883951    4.9393300    6.4672970  
   7 C       2.4696700 *  3.6985096    2.6901435 *  4.0333927    4.9393300  
   8 C       1.4510025 *  2.4696700 *  2.1564120 *  2.6984207 *  3.8231349  
   9 H       2.6984207 *  4.0333927    2.4696600 *  4.6018904    5.0597887  
  10 H       2.1564180 *  2.6901527 *  3.0845905    2.4696700 *  4.1399051  
  11 C       0.0000000    1.3390000 *  1.0769995 *  2.0880440 *  2.4696600 *
  12 C       1.3390000 *  0.0000000    2.0880496 *  1.0769994 *  1.4509936 *
  13 H       1.0769995 *  2.0880496 *  0.0000000    3.0408574    2.6984207 *
  14 H       2.0880440 *  1.0769994 *  3.0408574    0.0000000    2.1564120 *
  15 C       2.4696600 *  1.4509936 *  2.6984207 *  2.1564120 *  0.0000000  
  16 C       3.6984998    2.4696600 *  4.0333927    2.6901435 *  1.3390000 *
  17 H       2.6901435 *  2.1564120 *  2.4696700 *  3.0845905    1.0769994 *
  18 H       4.0333927    2.6984207 *  4.6018984    2.4696700 *  2.0880496 *

               16 C         17 H         18 H     

   1 H       9.4958384    8.4805248    9.5702351  
   2 H       1.0770016 *  2.3898502 *  1.8802702 *
   3 C       8.6050192    7.4823948    8.7567324  
   4 C       7.4090000    6.4673067    7.4913408  
   5 H       8.7567324    7.4090000    9.0351660  
   6 H       7.4823948    6.8297851    7.4090000  
   7 C       6.1451968    5.0509757    6.3541424  
   8 C       4.9393300    4.1399051    5.0597984  
   9 H       6.3541328    4.9393300    6.7310133  
  10 H       5.0509757    4.6884031    4.9393400  
  11 C       3.6984998    2.6901435 *  4.0333927  
  12 C       2.4696600 *  2.1564120 *  2.6984207 *
  13 H       4.0333927    2.4696700 *  4.6018984  
  14 H       2.6901435 *  3.0845905    2.4696700 *
  15 C       1.3390000 *  1.0769994 *  2.0880496 *
  16 C       0.0000000    2.0880440 *  1.0769995 *
  17 H       2.0880440 *  0.0000000    3.0408574  
  18 H       1.0769995 *  3.0408574    0.0000000  

  * ... LESS THAN  3.000


     ATOMIC BASIS SET
     ----------------
 THE CONTRACTED PRIMITIVE FUNCTIONS HAVE BEEN UNNORMALIZED
 THE CONTRACTED BASIS FUNCTIONS ARE NOW NORMALIZED TO UNITY

  SHELL TYPE  PRIMITIVE        EXPONENT          CONTRACTION COEFFICIENT(S)

 H         

      1   S       1            33.8700000    0.025494863235
      1   S       2             5.0950000    0.190362765893
      1   S       3             1.1590000    0.852162022245

      2   S       4             0.3258000    1.000000000000

      3   S       5             0.1027000    1.000000000000

      4   P       6             1.4070000    1.000000000000

      5   P       7             0.3880000    1.000000000000

      6   D       8             1.0570000    1.000000000000

 H         

      7   S       9            33.8700000    0.025494863235
      7   S      10             5.0950000    0.190362765893
      7   S      11             1.1590000    0.852162022245

      8   S      12             0.3258000    1.000000000000

      9   S      13             0.1027000    1.000000000000

     10   P      14             1.4070000    1.000000000000

     11   P      15             0.3880000    1.000000000000

     12   D      16             1.0570000    1.000000000000

 C         

     13   S      17          8236.0000000    0.000542430189
     13   S      18          1235.0000000    0.004196427901
     13   S      19           280.8000000    0.021540914108
     13   S      20            79.2700000    0.083614949614
     13   S      21            25.5900000    0.239871618922
     13   S      22             8.9970000    0.443751820060
     13   S      23             3.3190000    0.353579696469
     13   S      24             0.3643000   -0.009176366076

     14   S      25          8236.0000000   -0.000196392234
     14   S      26          1235.0000000   -0.001525950274
     14   S      27           280.8000000   -0.007890449028
     14   S      28            79.2700000   -0.031514870532
     14   S      29            25.5900000   -0.096910008320
     14   S      30             8.9970000   -0.220541526288
     14   S      31             3.3190000   -0.296069112937
     14   S      32             0.3643000    1.040503432950

     15   S      33             0.9059000    1.000000000000

     16   S      34             0.1285000    1.000000000000

     17   P      35            18.7100000    0.039426387165
     17   P      36             4.1330000    0.244088984924
     17   P      37             1.2000000    0.815492008943

     18   P      38             0.3827000    1.000000000000

     19   P      39             0.1209000    1.000000000000

     20   D      40             1.0970000    1.000000000000

     21   D      41             0.3180000    1.000000000000

     22   F      42             0.7610000    1.000000000000

 C         

     23   S      43          8236.0000000    0.000542430189
     23   S      44          1235.0000000    0.004196427901
     23   S      45           280.8000000    0.021540914108
     23   S      46            79.2700000    0.083614949614
     23   S      47            25.5900000    0.239871618922
     23   S      48             8.9970000    0.443751820060
     23   S      49             3.3190000    0.353579696469
     23   S      50             0.3643000   -0.009176366076

     24   S      51          8236.0000000   -0.000196392234
     24   S      52          1235.0000000   -0.001525950274
     24   S      53           280.8000000   -0.007890449028
     24   S      54            79.2700000   -0.031514870532
     24   S      55            25.5900000   -0.096910008320
     24   S      56             8.9970000   -0.220541526288
     24   S      57             3.3190000   -0.296069112937
     24   S      58             0.3643000    1.040503432950

     25   S      59             0.9059000    1.000000000000

     26   S      60             0.1285000    1.000000000000

     27   P      61            18.7100000    0.039426387165
     27   P      62             4.1330000    0.244088984924
     27   P      63             1.2000000    0.815492008943

     28   P      64             0.3827000    1.000000000000

     29   P      65             0.1209000    1.000000000000

     30   D      66             1.0970000    1.000000000000

     31   D      67             0.3180000    1.000000000000

     32   F      68             0.7610000    1.000000000000

 H         

     33   S      69            33.8700000    0.025494863235
     33   S      70             5.0950000    0.190362765893
     33   S      71             1.1590000    0.852162022245

     34   S      72             0.3258000    1.000000000000

     35   S      73             0.1027000    1.000000000000

     36   P      74             1.4070000    1.000000000000

     37   P      75             0.3880000    1.000000000000

     38   D      76             1.0570000    1.000000000000

 H         

     39   S      77            33.8700000    0.025494863235
     39   S      78             5.0950000    0.190362765893
     39   S      79             1.1590000    0.852162022245

     40   S      80             0.3258000    1.000000000000

     41   S      81             0.1027000    1.000000000000

     42   P      82             1.4070000    1.000000000000

     43   P      83             0.3880000    1.000000000000

     44   D      84             1.0570000    1.000000000000

 C         

     45   S      85          8236.0000000    0.000542430189
     45   S      86          1235.0000000    0.004196427901
     45   S      87           280.8000000    0.021540914108
     45   S      88            79.2700000    0.083614949614
     45   S      89            25.5900000    0.239871618922
     45   S      90             8.9970000    0.443751820060
     45   S      91             3.3190000    0.353579696469
     45   S      92             0.3643000   -0.009176366076

     46   S      93          8236.0000000   -0.000196392234
     46   S      94          1235.0000000   -0.001525950274
     46   S      95           280.8000000   -0.007890449028
     46   S      96            79.2700000   -0.031514870532
     46   S      97            25.5900000   -0.096910008320
     46   S      98             8.9970000   -0.220541526288
     46   S      99             3.3190000   -0.296069112937
     46   S     100             0.3643000    1.040503432950

     47   S     101             0.9059000    1.000000000000

     48   S     102             0.1285000    1.000000000000

     49   P     103            18.7100000    0.039426387165
     49   P     104             4.1330000    0.244088984924
     49   P     105             1.2000000    0.815492008943

     50   P     106             0.3827000    1.000000000000

     51   P     107             0.1209000    1.000000000000

     52   D     108             1.0970000    1.000000000000

     53   D     109             0.3180000    1.000000000000

     54   F     110             0.7610000    1.000000000000

 C         

     55   S     111          8236.0000000    0.000542430189
     55   S     112          1235.0000000    0.004196427901
     55   S     113           280.8000000    0.021540914108
     55   S     114            79.2700000    0.083614949614
     55   S     115            25.5900000    0.239871618922
     55   S     116             8.9970000    0.443751820060
     55   S     117             3.3190000    0.353579696469
     55   S     118             0.3643000   -0.009176366076

     56   S     119          8236.0000000   -0.000196392234
     56   S     120          1235.0000000   -0.001525950274
     56   S     121           280.8000000   -0.007890449028
     56   S     122            79.2700000   -0.031514870532
     56   S     123            25.5900000   -0.096910008320
     56   S     124             8.9970000   -0.220541526288
     56   S     125             3.3190000   -0.296069112937
     56   S     126             0.3643000    1.040503432950

     57   S     127             0.9059000    1.000000000000

     58   S     128             0.1285000    1.000000000000

     59   P     129            18.7100000    0.039426387165
     59   P     130             4.1330000    0.244088984924
     59   P     131             1.2000000    0.815492008943

     60   P     132             0.3827000    1.000000000000

     61   P     133             0.1209000    1.000000000000

     62   D     134             1.0970000    1.000000000000

     63   D     135             0.3180000    1.000000000000

     64   F     136             0.7610000    1.000000000000

 H         

     65   S     137            33.8700000    0.025494863235
     65   S     138             5.0950000    0.190362765893
     65   S     139             1.1590000    0.852162022245

     66   S     140             0.3258000    1.000000000000

     67   S     141             0.1027000    1.000000000000

     68   P     142             1.4070000    1.000000000000

     69   P     143             0.3880000    1.000000000000

     70   D     144             1.0570000    1.000000000000

 H         

     71   S     145            33.8700000    0.025494863235
     71   S     146             5.0950000    0.190362765893
     71   S     147             1.1590000    0.852162022245

     72   S     148             0.3258000    1.000000000000

     73   S     149             0.1027000    1.000000000000

     74   P     150             1.4070000    1.000000000000

     75   P     151             0.3880000    1.000000000000

     76   D     152             1.0570000    1.000000000000

 C         

     77   S     153          8236.0000000    0.000542430189
     77   S     154          1235.0000000    0.004196427901
     77   S     155           280.8000000    0.021540914108
     77   S     156            79.2700000    0.083614949614
     77   S     157            25.5900000    0.239871618922
     77   S     158             8.9970000    0.443751820060
     77   S     159             3.3190000    0.353579696469
     77   S     160             0.3643000   -0.009176366076

     78   S     161          8236.0000000   -0.000196392234
     78   S     162          1235.0000000   -0.001525950274
     78   S     163           280.8000000   -0.007890449028
     78   S     164            79.2700000   -0.031514870532
     78   S     165            25.5900000   -0.096910008320
     78   S     166             8.9970000   -0.220541526288
     78   S     167             3.3190000   -0.296069112937
     78   S     168             0.3643000    1.040503432950

     79   S     169             0.9059000    1.000000000000

     80   S     170             0.1285000    1.000000000000

     81   P     171            18.7100000    0.039426387165
     81   P     172             4.1330000    0.244088984924
     81   P     173             1.2000000    0.815492008943

     82   P     174             0.3827000    1.000000000000

     83   P     175             0.1209000    1.000000000000

     84   D     176             1.0970000    1.000000000000

     85   D     177             0.3180000    1.000000000000

     86   F     178             0.7610000    1.000000000000

 C         

     87   S     179          8236.0000000    0.000542430189
     87   S     180          1235.0000000    0.004196427901
     87   S     181           280.8000000    0.021540914108
     87   S     182            79.2700000    0.083614949614
     87   S     183            25.5900000    0.239871618922
     87   S     184             8.9970000    0.443751820060
     87   S     185             3.3190000    0.353579696469
     87   S     186             0.3643000   -0.009176366076

     88   S     187          8236.0000000   -0.000196392234
     88   S     188          1235.0000000   -0.001525950274
     88   S     189           280.8000000   -0.007890449028
     88   S     190            79.2700000   -0.031514870532
     88   S     191            25.5900000   -0.096910008320
     88   S     192             8.9970000   -0.220541526288
     88   S     193             3.3190000   -0.296069112937
     88   S     194             0.3643000    1.040503432950

     89   S     195             0.9059000    1.000000000000

     90   S     196             0.1285000    1.000000000000

     91   P     197            18.7100000    0.039426387165
     91   P     198             4.1330000    0.244088984924
     91   P     199             1.2000000    0.815492008943

     92   P     200             0.3827000    1.000000000000

     93   P     201             0.1209000    1.000000000000

     94   D     202             1.0970000    1.000000000000

     95   D     203             0.3180000    1.000000000000

     96   F     204             0.7610000    1.000000000000

 H         

     97   S     205            33.8700000    0.025494863235
     97   S     206             5.0950000    0.190362765893
     97   S     207             1.1590000    0.852162022245

     98   S     208             0.3258000    1.000000000000

     99   S     209             0.1027000    1.000000000000

    100   P     210             1.4070000    1.000000000000

    101   P     211             0.3880000    1.000000000000

    102   D     212             1.0570000    1.000000000000

 H         

    103   S     213            33.8700000    0.025494863235
    103   S     214             5.0950000    0.190362765893
    103   S     215             1.1590000    0.852162022245

    104   S     216             0.3258000    1.000000000000

    105   S     217             0.1027000    1.000000000000

    106   P     218             1.4070000    1.000000000000

    107   P     219             0.3880000    1.000000000000

    108   D     220             1.0570000    1.000000000000

 C         

    109   S     221          8236.0000000    0.000542430189
    109   S     222          1235.0000000    0.004196427901
    109   S     223           280.8000000    0.021540914108
    109   S     224            79.2700000    0.083614949614
    109   S     225            25.5900000    0.239871618922
    109   S     226             8.9970000    0.443751820060
    109   S     227             3.3190000    0.353579696469
    109   S     228             0.3643000   -0.009176366076

    110   S     229          8236.0000000   -0.000196392234
    110   S     230          1235.0000000   -0.001525950274
    110   S     231           280.8000000   -0.007890449028
    110   S     232            79.2700000   -0.031514870532
    110   S     233            25.5900000   -0.096910008320
    110   S     234             8.9970000   -0.220541526288
    110   S     235             3.3190000   -0.296069112937
    110   S     236             0.3643000    1.040503432950

    111   S     237             0.9059000    1.000000000000

    112   S     238             0.1285000    1.000000000000

    113   P     239            18.7100000    0.039426387165
    113   P     240             4.1330000    0.244088984924
    113   P     241             1.2000000    0.815492008943

    114   P     242             0.3827000    1.000000000000

    115   P     243             0.1209000    1.000000000000

    116   D     244             1.0970000    1.000000000000

    117   D     245             0.3180000    1.000000000000

    118   F     246             0.7610000    1.000000000000

 C         

    119   S     247          8236.0000000    0.000542430189
    119   S     248          1235.0000000    0.004196427901
    119   S     249           280.8000000    0.021540914108
    119   S     250            79.2700000    0.083614949614
    119   S     251            25.5900000    0.239871618922
    119   S     252             8.9970000    0.443751820060
    119   S     253             3.3190000    0.353579696469
    119   S     254             0.3643000   -0.009176366076

    120   S     255          8236.0000000   -0.000196392234
    120   S     256          1235.0000000   -0.001525950274
    120   S     257           280.8000000   -0.007890449028
    120   S     258            79.2700000   -0.031514870532
    120   S     259            25.5900000   -0.096910008320
    120   S     260             8.9970000   -0.220541526288
    120   S     261             3.3190000   -0.296069112937
    120   S     262             0.3643000    1.040503432950

    121   S     263             0.9059000    1.000000000000

    122   S     264             0.1285000    1.000000000000

    123   P     265            18.7100000    0.039426387165
    123   P     266             4.1330000    0.244088984924
    123   P     267             1.2000000    0.815492008943

    124   P     268             0.3827000    1.000000000000

    125   P     269             0.1209000    1.000000000000

    126   D     270             1.0970000    1.000000000000

    127   D     271             0.3180000    1.000000000000

    128   F     272             0.7610000    1.000000000000

 H         

    129   S     273            33.8700000    0.025494863235
    129   S     274             5.0950000    0.190362765893
    129   S     275             1.1590000    0.852162022245

    130   S     276             0.3258000    1.000000000000

    131   S     277             0.1027000    1.000000000000

    132   P     278             1.4070000    1.000000000000

    133   P     279             0.3880000    1.000000000000

    134   D     280             1.0570000    1.000000000000

 H         

    135   S     281            33.8700000    0.025494863235
    135   S     282             5.0950000    0.190362765893
    135   S     283             1.1590000    0.852162022245

    136   S     284             0.3258000    1.000000000000

    137   S     285             0.1027000    1.000000000000

    138   P     286             1.4070000    1.000000000000

    139   P     287             0.3880000    1.000000000000

    140   D     288             1.0570000    1.000000000000

 TOTAL NUMBER OF BASIS SET SHELLS             =  140
 NUMBER OF CARTESIAN GAUSSIAN BASIS FUNCTIONS =  430
 NOTE: THIS RUN WILL RESTRICT THE MO VARIATION SPACE TO SPHERICAL HARMONICS.
 THE NUMBER OF ORBITALS KEPT IN THE VARIATIONAL SPACE WILL BE PRINTED LATER.
 NUMBER OF ELECTRONS                          =   58
 CHARGE OF MOLECULE                           =    0
 SPIN MULTIPLICITY                            =    1
 NUMBER OF OCCUPIED ORBITALS (ALPHA)          =   29
 NUMBER OF OCCUPIED ORBITALS (BETA )          =   29
 TOTAL NUMBER OF ATOMS                        =   18
 THE NUCLEAR REPULSION ENERGY IS      298.6090226575

     $CONTRL OPTIONS
     ---------------
 SCFTYP=RHF          RUNTYP=ENERGY       EXETYP=RUN     
 MPLEVL=       2     CITYP =NONE         CCTYP =NONE         VBTYP =NONE    
 DFTTYP=NONE         TDDFT =NONE    
 MULT  =       1     ICHARG=       0     NZVAR =       0     COORD =UNIQUE  
 PP    =NONE         RELWFN=NONE         LOCAL =NONE         NUMGRD=       F
 ISPHER=       1     NOSYM =       0     MAXIT =     200     UNITS =ANGS    
 PLTORB=       F     MOLPLT=       F     AIMPAC=       F     FRIEND=        
 NPRINT=      -5     IREST =       0     GEOM  =INPUT   
 NORMF =       0     NORMP =       0     ITOL  =      30     ICUT  =      20
 INTTYP=BEST         GRDTYP=BEST         QMTTOL= 1.0E-05

     $SYSTEM OPTIONS
     ---------------
  REPLICATED MEMORY=   100000000 WORDS (ON EVERY NODE).
 DISTRIBUTED MEMDDI=         100 MILLION WORDS IN AGGREGATE,
 MEMDDI DISTRIBUTED OVER   2 PROCESSORS IS    50000000 WORDS/PROCESSOR.
 TOTAL MEMORY REQUESTED ON EACH PROCESSOR=   150000000 WORDS.
 TIMLIM=      525600.00 MINUTES, OR     365.0 DAYS.
 PARALL= T  BALTYP=  DLB     KDIAG=    0  COREFL= F
 MXSEQ2=     300 MXSEQ3=     150  mem10=         0

          ----------------
          PROPERTIES INPUT
          ----------------

     MOMENTS            FIELD           POTENTIAL          DENSITY
 IEMOM =       1   IEFLD =       0   IEPOT =       0   IEDEN =       0
 WHERE =COMASS     WHERE =NUCLEI     WHERE =NUCLEI     WHERE =NUCLEI  
 OUTPUT=BOTH       OUTPUT=BOTH       OUTPUT=BOTH       OUTPUT=BOTH    
 IEMINT=       0   IEFINT=       0                     IEDINT=       0
                                                       MORB  =       0
          EXTRAPOLATION IN EFFECT
          DAMPING IN EFFECT
          SOSCF IN EFFECT
 ORBITAL PRINTING OPTION: NPREO=     1   430     2     1

     -------------------------------
     INTEGRAL TRANSFORMATION OPTIONS
     -------------------------------
     NWORD  =            0
     CUTOFF = 1.0E-09     MPTRAN =       0
     DIRTRF =       T     AOINTS =DUP     

          ----------------------
          INTEGRAL INPUT OPTIONS
          ----------------------
 NOPK  =       1 NORDER=       0 SCHWRZ=       T

          -----------------------
          MP2 CONTROL INFORMATION
          -----------------------
          NACORE =        8  NBCORE =        8
          LMOMP2 =        F  AOINTS = DUP     
          METHOD =        2  NWORD  =               0
          MP2PRP =        F  OSPT   = NONE    
          CUTOFF = 1.00E-09  CPHFBS = BASISAO 
          CODE   = DDI     

          NUMBER OF CORE -A-  ORBITALS =     8
          NUMBER OF CORE -B-  ORBITALS =     8
          NUMBER OF OCC. -A-  ORBITALS =    29
          NUMBER OF OCC. -B-  ORBITALS =    29
          NUMBER OF MOLECULAR ORBITALS =   430
          NUMBER OF   BASIS  FUNCTIONS =   430


     ------------------------------------------
     THE POINT GROUP IS C1 , NAXIS= 1, ORDER= 1
     ------------------------------------------

 -- VARIATIONAL SPACE WILL BE RESTRICTED TO PURE SPHERICAL HARMONICS ONLY --
 AFTER EXCLUDING CONTAMINANT COMBINATIONS FROM THE CARTESIAN GAUSSIAN BASIS
 SET, THE NUMBER OF SPHERICAL HARMONICS KEPT IN THE VARIATION SPACE IS  380

     DIMENSIONS OF THE SYMMETRY SUBSPACES ARE
 A   =  380

 ..... DONE SETTING UP THE RUN .....
 CPU     0: STEP CPU TIME=     1.13 TOTAL CPU TIME=        1.1 (    0.0 MIN)
 TOTAL WALL CLOCK TIME=        1.7 SECONDS, CPU UTILIZATION IS  65.70%
 ...... END OF ONE-ELECTRON INTEGRALS ......
 CPU     0: STEP CPU TIME=     0.09 TOTAL CPU TIME=        1.2 (    0.0 MIN)
 TOTAL WALL CLOCK TIME=        1.9 SECONDS, CPU UTILIZATION IS  65.95%

          -------------
          GUESS OPTIONS
          -------------
          GUESS =MOREAD            NORB  =       0          NORDER=       0
          MIX   =       F          PRTMO =       F          PUNMO =       F
          TOLZ  = 1.0E-08          TOLE  = 1.0E-05
          SYMDEN=       F          PURIFY=       F

 INITIAL GUESS ORBITALS GENERATED BY MOREAD   ROUTINE.

 SYMMETRIES FOR INITIAL GUESS ORBITALS FOLLOW.   BOTH SET(S).
    29 ORBITALS ARE OCCUPIED (    8 CORE ORBITALS).
     1=A        2=A        3=A        4=A        5=A        6=A        7=A   
     8=A        9=A       10=A       11=A       12=A       13=A       14=A   
    15=A       16=A       17=A       18=A       19=A       20=A       21=A   
    22=A       23=A       24=A       25=A       26=A       27=A       28=A   
    29=A       30=A       31=A       32=A       33=A       34=A       35=A   
    36=A       37=A       38=A       39=A       40=A       41=A       42=A   
    43=A       44=A       45=A       46=A       47=A       48=A       49=A   
    50=A       51=A       52=A       53=A       54=A       55=A       56=A   
    57=A       58=A       59=A       60=A       61=A       62=A       63=A   
    64=A       65=A       66=A       67=A       68=A       69=A       70=A   
    71=A       72=A       73=A       74=A       75=A       76=A       77=A   
    78=A       79=A       80=A       81=A       82=A       83=A       84=A   
    85=A       86=A       87=A       88=A       89=A       90=A       91=A   
    92=A       93=A       94=A       95=A       96=A       97=A       98=A   
    99=A      100=A      101=A      102=A      103=A      104=A      105=A   
   106=A      107=A      108=A      109=A      110=A      111=A      112=A   
   113=A      114=A      115=A      116=A      117=A      118=A      119=A   
   120=A      121=A      122=A      123=A      124=A      125=A      126=A   
   127=A      128=A      129=A      130=A      131=A      132=A      133=A   
   134=A      135=A      136=A      137=A      138=A      139=A      140=A   
   141=A      142=A      143=A      144=A      145=A      146=A      147=A   
   148=A      149=A      150=A      151=A      152=A      153=A      154=A   
   155=A      156=A      157=A      158=A      159=A      160=A      161=A   
   162=A      163=A      164=A      165=A      166=A      167=A      168=A   
   169=A      170=A      171=A      172=A      173=A      174=A      175=A   
   176=A      177=A      178=A      179=A      180=A      181=A      182=A   
   183=A      184=A      185=A      186=A      187=A      188=A      189=A   
   190=A      191=A      192=A      193=A      194=A      195=A      196=A   
   197=A      198=A      199=A      200=A      201=A      202=A      203=A   
   204=A      205=A      206=A      207=A      208=A      209=A      210=A   
   211=A      212=A      213=A      214=A      215=A      216=A      217=A   
   218=A      219=A      220=A      221=A      222=A      223=A      224=A   
   225=A      226=A      227=A      228=A      229=A      230=A      231=A   
   232=A      233=A      234=A      235=A      236=A      237=A      238=A   
   239=A      240=A      241=A      242=A      243=A      244=A      245=A   
   246=A      247=A      248=A      249=A      250=A      251=A      252=A   
   253=A      254=A      255=A      256=A      257=A      258=A      259=A   
   260=A      261=A      262=A      263=A      264=A      265=A      266=A   
   267=A      268=A      269=A      270=A      271=A      272=A      273=A   
   274=A      275=A      276=A      277=A      278=A      279=A      280=A   
   281=A      282=A      283=A      284=A      285=A      286=A      287=A   
   288=A      289=A      290=A      291=A      292=A      293=A      294=A   
   295=A      296=A      297=A      298=A      299=A      300=A      301=A   
   302=A      303=A      304=A      305=A      306=A      307=A      308=A   
   309=A      310=A      311=A      312=A      313=A      314=A      315=A   
   316=A      317=A      318=A      319=A      320=A      321=A      322=A   
   323=A      324=A      325=A      326=A      327=A      328=A      329=A   
   330=A      331=A      332=A      333=A      334=A      335=A      336=A   
   337=A      338=A      339=A      340=A      341=A      342=A      343=A   
   344=A      345=A      346=A      347=A      348=A      349=A      350=A   
   351=A      352=A      353=A      354=A      355=A      356=A      357=A   
   358=A      359=A      360=A      361=A      362=A      363=A      364=A   
   365=A      366=A      367=A      368=A      369=A      370=A      371=A   
   372=A      373=A      374=A      375=A      376=A      377=A      378=A   
   379=A      380=A   
 ...... END OF INITIAL ORBITAL SELECTION ......
 CPU     0: STEP CPU TIME=     0.37 TOTAL CPU TIME=        1.6 (    0.0 MIN)
 TOTAL WALL CLOCK TIME=        2.4 SECONDS, CPU UTILIZATION IS  66.25%

                    ----------------------
                    AO INTEGRAL TECHNOLOGY
                    ----------------------
     S,P,L SHELL ROTATED AXIS INTEGRALS, REPROGRAMMED BY
        KAZUYA ISHIMURA (IMS) AND JOSE SIERRA (SYNSTAR).
     S,P,D,L SHELL ROTATED AXIS INTEGRALS PROGRAMMED BY
        KAZUYA ISHIMURA (INSTITUTE FOR MOLECULAR SCIENCE).
     S,P,D,F,G SHELL TO TOTAL QUARTET ANGULAR MOMENTUM SUM 5,
        ERIC PROGRAM BY GRAHAM FLETCHER (ELORET AND NASA ADVANCED
        SUPERCOMPUTING DIVISION, AMES RESEARCH CENTER).
     S,P,D,F,G,L SHELL GENERAL RYS QUADRATURE PROGRAMMED BY
        MICHEL DUPUIS (PACIFIC NORTHWEST NATIONAL LABORATORY).
  ...... END OF TWO-ELECTRON INTEGRALS .....
 CPU     0: STEP CPU TIME=     0.01 TOTAL CPU TIME=        1.6 (    0.0 MIN)
 TOTAL WALL CLOCK TIME=        2.4 SECONDS, CPU UTILIZATION IS  65.57%

          --------------------------
                 RHF SCF CALCULATION
          --------------------------
     DENSITY MATRIX CONV=  2.00E-06

 DIRECT SCF CALCULATION, SCHWRZ=T   FDIFF=T,  DIRTHR=  0.00E+00 NITDIR=10

                                                                                                                   NONZERO     BLOCKS
 ITER EX DEM     TOTAL ENERGY        E CHANGE  DENSITY CHANGE     ORB. GRAD      VIR. SHIFT       DAMPING        INTEGRALS    SKIPPED
   1  0  0     -308.8061821813  -308.8061821813   0.012045974   0.000000000     0.000000000     1.000000000     1335894340   14867751
          ---------------START SECOND ORDER SCF---------------
   2  1  0     -308.8063187567    -0.0001365753   0.001141016   0.000339563     0.000000000     0.000000000     1330232646   15330603
   3  2  0     -308.8063205553    -0.0000017986   0.000192770   0.000075300     0.000000000     0.000000000     1315781776   16048024
   4  3  0     -308.8063206736    -0.0000001184   0.000030582   0.000015396     0.000000000     0.000000000     1301021462   16611230
   5  4  0     -308.8063206794    -0.0000000058   0.000019378   0.000007263     0.000000000     0.000000000     1272147552   17448015
   6  5  0     -308.8063206805    -0.0000000011   0.000001543   0.000000804     0.000000000     0.000000000     1266679852   17702344
   7  6  0     -308.8063206805    -0.0000000000   0.000000502   0.000000512     0.000000000     0.000000000     1233576180   18586679

          -----------------
          DENSITY CONVERGED
          -----------------
     TIME TO FORM FOCK OPERATORS=     645.0 SECONDS (      92.1 SEC/ITER)
     FOCK TIME ON FIRST ITERATION=      96.2, LAST ITERATION=      87.5
     TIME TO SOLVE SCF EQUATIONS=       0.9 SECONDS (       0.1 SEC/ITER)

 FINAL RHF ENERGY IS     -308.8063206805 AFTER   7 ITERATIONS
 ...... END OF RHF CALCULATION ......
 CPU     0: STEP CPU TIME=   646.34 TOTAL CPU TIME=      647.9 (   10.8 MIN)
 TOTAL WALL CLOCK TIME=      650.1 SECONDS, CPU UTILIZATION IS  99.67%



 ---------------------------     ------------------------------
 DISTRIBUTED DATA MP2 ENERGY     PROGRAM WRITTEN BY G. FLETCHER
 ---------------------------     ------------------------------

    THIS CALCULATION IS RUNNING WITH MWORDS=  100, MEMDDI=     100, AND P=    2
 MEMORY USAGE PER CPU IS 8*(MWORDS + MEMDDI/P)/1024 =    1.2 GBYTES.

 MINIMAL REQUIREMENT FOR THIS RUN IS MWORDS=    4, MEMDDI=      43.
 FOR P=    2, THE MEMORY USAGE PER CPU(CORE) WOULD BE    0.2 GBYTES.

 DDI: Creating Array [0] - 184900 x 231 = 42711900 words.

      DIRECT 4-INDEX TRANSFORMATION 
      SCHWARZ INEQUALITY TEST SKIPPED   28605878 INTEGRAL BLOCKS

 RESULTS OF MOLLER-PLESSET 2ND ORDER CORRECTION ARE
                     E(SCF)=      -308.8063206805
                       E(2)=        -1.2818395009
                     E(MP2)=      -310.0881601814
 SPIN-COMPONENT-SCALED MP2 RESULTS ARE
                      E(2S)=        -0.9795355568
                      E(2T)=        -0.3023039441
                     E(2ST)=        -1.2762106495 = 6/5 * E(2S) + 1/3 * E(2T)
                    SCS-MP2=      -310.0825313300
 ..... DONE WITH MP2 ENERGY .....
 CPU     0: STEP CPU TIME=   492.05 TOTAL CPU TIME=     1140.0 (   19.0 MIN)
 TOTAL WALL CLOCK TIME=     1198.0 SECONDS, CPU UTILIZATION IS  95.16%
               3054902  WORDS OF DYNAMIC MEMORY USED
 EXECUTION OF GAMESS TERMINATED NORMALLY Wed May  1 12:26:31 2019
 DDI: 171850840 bytes (163.9 MB / 20 MWords) used by master data server.

 ----------------------------------------
 CPU timing information for all processes
 ========================================
 0: 1129.796 + 10.279 = 1140.75
 1: 1096.213 + 19.23 = 1115.236
 2: 21.335 + 52.421 = 73.757
 3: 17.836 + 45.311 = 63.148
 ----------------------------------------
unset echo
----- accounting info -----
Files used on the master node cpn-d15-13.cbls.ccr.buffalo.edu were:
-rw------- 1 nikolays ccrstaff  2996714 May  1 12:06 /scratch/11369048/c8h10-cct-mp2.F05
-rw-r--r-- 1 nikolays ccrstaff 16065520 May  1 12:26 /scratch/11369048/c8h10-cct-mp2.F10
-rw-r--r-- 1 nikolays ccrstaff        0 May  1 12:06 /scratch/11369048/c8h10-cct-mp2.nodes.mpd
ls: No match.
ls: No match.
ls: No match.
Wed May  1 12:26:33 EDT 2019
0.363u 0.169s 20:03.28 0.0%     0+0k 232+6336io 0pf+0w
```