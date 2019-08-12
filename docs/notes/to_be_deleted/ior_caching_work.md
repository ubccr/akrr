## Talking about ior caching and seeing if we can somehow avoid it on openstack

So First thing I'm doing is getting ior set up and running on bare_metal_gen_compute_8core
Just to have a sort of reference.
So, on vortex, I'm doing:


# setting up HDF5 (from IOR Deployment thing)
```bash
export AKRR_APPKER_DIR=/gpfs/scratch/hoffmaps/akrr_project/appker/barere_metal_gen_compute_8core
cd $AKRR_APPKER_DIR/execs

mkdir -p libs
mkdir -p libs\tmp
cd libs\tmp

#obtain parallel-netcdf source code
wget https://support.hdfgroup.org/ftp/HDF5/releases/hdf5-1.8/hdf5-1.8.21/src/hdf5-1.8.21.tar.gz
tar xvzf hdf5-1.8.21.tar.gz
cd hdf5-1.8.21

# might have to module load intel and intel-mpi before this

./configure --prefix=$AKRR_APPKER_DIR/execs/libs/hdf5-1.8.21 --enable-parallel CC=`which mpiicc` CXX=`which mpiicpc`

```
Sample output:
```bash
[hoffmaps@vortex2:/gpfs/scratch/hoffmaps/akrr_project/appker/barere_metal_gen_compute_8core/execs/libstmp/hdf5-1.8.21]$ ./configure --prefix=$AKRR_APPKER_DIR/execs/libs/hdf5-1.8.21 --enable-parallel CC=`which mpiicc` CXX=`which mpiicpc`
checking for a BSD-compatible install... /usr/bin/install -c
checking whether build environment is sane... yes
checking for a thread-safe mkdir -p... /usr/bin/mkdir -p
checking for gawk... gawk
checking whether make sets $(MAKE)... yes
checking whether make supports nested variables... yes
checking whether make supports nested variables... (cached) yes
checking whether to enable maintainer-specific portions of Makefiles... no
checking build system type... x86_64-unknown-linux-gnu
checking host system type... x86_64-unknown-linux-gnu
checking shell variables initial values... done
checking if basename works... yes
checking if xargs works... yes
checking for cached host... none
checking for config x86_64-unknown-linux-gnu... no
checking for config x86_64-unknown-linux-gnu... no
checking for config unknown-linux-gnu... no
checking for config unknown-linux-gnu... no
checking for config x86_64-linux-gnu... no
checking for config x86_64-linux-gnu... no
checking for config x86_64-unknown... no
checking for config linux-gnu... found
compiler '/util/academic/intel/18.3/compilers_and_libraries_2018.3.222/linux/mpi/intel64/bin/mpiicc' is Intel icc-18.0.3.222
No match to get fc_version_info for 
checking for config ./config/site-specific/host-srv-p22-13.cbls.ccr.buffalo.edu... no
checking for config ./config/site-specific/host-cbls.ccr.buffalo.edu... no
checking for config ./config/site-specific/host-ccr.buffalo.edu... no
checking for config ./config/site-specific/host-buffalo.edu... no
checking for config ./config/site-specific/host-edu... no
checking for gcc... /util/academic/intel/18.3/compilers_and_libraries_2018.3.222/linux/mpi/intel64/bin/mpiicc
checking whether the C compiler works... yes
checking for C compiler default output file name... a.out
checking for suffix of executables... 
checking whether we are cross compiling... no
checking for suffix of object files... o
checking whether we are using the GNU C compiler... yes
checking whether /util/academic/intel/18.3/compilers_and_libraries_2018.3.222/linux/mpi/intel64/bin/mpiicc accepts -g... yes
checking for /util/academic/intel/18.3/compilers_and_libraries_2018.3.222/linux/mpi/intel64/bin/mpiicc option to accept ISO C89... none needed
checking whether /util/academic/intel/18.3/compilers_and_libraries_2018.3.222/linux/mpi/intel64/bin/mpiicc understands -c and -o together... yes
checking for style of include used by make... GNU
checking dependency style of /util/academic/intel/18.3/compilers_and_libraries_2018.3.222/linux/mpi/intel64/bin/mpiicc... gcc3
checking if unsupported combinations of configure options are allowed... no
checking if Fortran interface enabled... no
checking if Fortran 2003 interface enabled... no
checking whether we are using the GNU C++ compiler... yes
checking whether /util/academic/intel/18.3/compilers_and_libraries_2018.3.222/linux/mpi/intel64/bin/mpiicpc accepts -g... yes
checking dependency style of /util/academic/intel/18.3/compilers_and_libraries_2018.3.222/linux/mpi/intel64/bin/mpiicpc... gcc3
checking how to run the C++ preprocessor... /util/academic/intel/18.3/compilers_and_libraries_2018.3.222/linux/mpi/intel64/bin/mpiicpc -E
checking if c++ interface enabled... no
checking if high level library is enabled... yes
checking for perl... perl
checking for ar... ar
checking whether make sets $(MAKE)... (cached) yes
checking for tr... /usr/bin/tr
checking if srcdir= and time commands work together... yes
checking how to print strings... printf
checking for a sed that does not truncate output... /usr/bin/sed
checking for grep that handles long lines and -e... /usr/bin/grep
checking for egrep... /usr/bin/grep -E
checking for fgrep... /usr/bin/grep -F
checking for ld used by /util/academic/intel/18.3/compilers_and_libraries_2018.3.222/linux/mpi/intel64/bin/mpiicc... /usr/bin/ld
checking if the linker (/usr/bin/ld) is GNU ld... yes
checking for BSD- or MS-compatible name lister (nm)... /usr/bin/nm -B
checking the name lister (/usr/bin/nm -B) interface... BSD nm
checking whether ln -s works... yes
checking the maximum length of command line arguments... 1572864
checking how to convert x86_64-unknown-linux-gnu file names to x86_64-unknown-linux-gnu format... func_convert_file_noop
checking how to convert x86_64-unknown-linux-gnu file names to toolchain format... func_convert_file_noop
checking for /usr/bin/ld option to reload object files... -r
checking for objdump... objdump
checking how to recognize dependent libraries... pass_all
checking for dlltool... no
checking how to associate runtime and link libraries... printf %s\n
checking for archiver @FILE support... @
checking for strip... strip
checking for ranlib... ranlib
checking command to parse /usr/bin/nm -B output from /util/academic/intel/18.3/compilers_and_libraries_2018.3.222/linux/mpi/intel64/bin/mpiicc object... ok
checking for sysroot... no
checking for a working dd... /usr/bin/dd
checking how to truncate binary pipes... /usr/bin/dd bs=4096 count=1
checking for mt... no
checking if : is a manifest tool... no
checking how to run the C preprocessor... /util/academic/intel/18.3/compilers_and_libraries_2018.3.222/linux/mpi/intel64/bin/mpiicc -E
checking for ANSI C header files... yes
checking for sys/types.h... yes
checking for sys/stat.h... yes
checking for stdlib.h... yes
checking for string.h... yes
checking for memory.h... yes
checking for strings.h... yes
checking for inttypes.h... yes
checking for stdint.h... yes
checking for unistd.h... yes
checking for dlfcn.h... yes
checking for objdir... .libs
checking if /util/academic/intel/18.3/compilers_and_libraries_2018.3.222/linux/mpi/intel64/bin/mpiicc supports -fno-rtti -fno-exceptions... yes
checking for /util/academic/intel/18.3/compilers_and_libraries_2018.3.222/linux/mpi/intel64/bin/mpiicc option to produce PIC... -fPIC -DPIC
checking if /util/academic/intel/18.3/compilers_and_libraries_2018.3.222/linux/mpi/intel64/bin/mpiicc PIC flag -fPIC -DPIC works... yes
checking if /util/academic/intel/18.3/compilers_and_libraries_2018.3.222/linux/mpi/intel64/bin/mpiicc static flag -static works... no
checking if /util/academic/intel/18.3/compilers_and_libraries_2018.3.222/linux/mpi/intel64/bin/mpiicc supports -c -o file.o... yes
checking if /util/academic/intel/18.3/compilers_and_libraries_2018.3.222/linux/mpi/intel64/bin/mpiicc supports -c -o file.o... (cached) yes
checking whether the /util/academic/intel/18.3/compilers_and_libraries_2018.3.222/linux/mpi/intel64/bin/mpiicc linker (/usr/bin/ld -m elf_x86_64) supports shared libraries... yes
checking whether -lc should be explicitly linked in... no
checking dynamic linker characteristics... GNU/Linux ld.so
checking how to hardcode library paths into programs... immediate
checking for shl_load... no
checking for shl_load in -ldld... no
checking for dlopen... yes
checking whether a program can dlopen itself... yes
checking whether a statically linked program can dlopen itself... yes
checking whether stripping libraries is possible... yes
checking if libtool supports shared libraries... yes
checking whether to build shared libraries... yes
checking whether to build static libraries... yes
checking if we should install only statically linked executables... no
checking if -Wl,-rpath should be used to link shared libs in nondefault directories... yes
checking whether make will build with undefined variables... yes
checking for production mode... production
checking for ceil in -lm... yes
checking for dlopen in -ldl... yes
checking for ANSI C header files... (cached) yes
checking whether time.h and sys/time.h may both be included... yes
checking sys/resource.h usability... yes
checking sys/resource.h presence... yes
checking for sys/resource.h... yes
checking sys/time.h usability... yes
checking sys/time.h presence... yes
checking for sys/time.h... yes
checking for unistd.h... (cached) yes
checking sys/ioctl.h usability... yes
checking sys/ioctl.h presence... yes
checking for sys/ioctl.h... yes
checking for sys/stat.h... (cached) yes
checking sys/socket.h usability... yes
checking sys/socket.h presence... yes
checking for sys/socket.h... yes
checking for sys/types.h... (cached) yes
checking stddef.h usability... yes
checking stddef.h presence... yes
checking for stddef.h... yes
checking setjmp.h usability... yes
checking setjmp.h presence... yes
checking for setjmp.h... yes
checking features.h usability... yes
checking features.h presence... yes
checking for features.h... yes
checking dirent.h usability... yes
checking dirent.h presence... yes
checking for dirent.h... yes
checking for stdint.h... (cached) yes
checking mach/mach_time.h usability... no
checking mach/mach_time.h presence... no
checking for mach/mach_time.h... no
checking io.h usability... no
checking io.h presence... no
checking for io.h... no
checking winsock2.h usability... no
checking winsock2.h presence... no
checking for winsock2.h... no
checking sys/timeb.h usability... yes
checking sys/timeb.h presence... yes
checking for sys/timeb.h... yes
checking if libtool needs -no-undefined flag to build shared libraries... no
checking for _FILE_OFFSET_BITS value needed for large files... no
checking for off_t... yes
checking for size_t... yes
checking for ssize_t... yes
checking for ptrdiff_t... yes
checking whether byte ordering is bigendian... no
checking size of char... 1
checking size of short... 2
checking size of int... 4
checking size of unsigned... 4
checking size of long... 8
checking size of long long... 8
checking size of __int64... 8
checking size of float... 4
checking size of double... 8
checking size of long double... 16
checking size of int8_t... 1
checking size of uint8_t... 1
checking size of int_least8_t... 1
checking size of uint_least8_t... 1
checking size of int_fast8_t... 1
checking size of uint_fast8_t... 1
checking size of int16_t... 2
checking size of uint16_t... 2
checking size of int_least16_t... 2
checking size of uint_least16_t... 2
checking size of int_fast16_t... 8
checking size of uint_fast16_t... 8
checking size of int32_t... 4
checking size of uint32_t... 4
checking size of int_least32_t... 4
checking size of uint_least32_t... 4
checking size of int_fast32_t... 8
checking size of uint_fast32_t... 8
checking size of int64_t... 8
checking size of uint64_t... 8
checking size of int_least64_t... 8
checking size of uint_least64_t... 8
checking size of int_fast64_t... 8
checking size of uint_fast64_t... 8
checking size of size_t... 8
checking size of ssize_t... 8
checking size of ptrdiff_t... 8
checking size of off_t... 8
checking if dev_t is scalar... yes
checking for dmalloc library... suppressed
checking zlib.h usability... yes
checking zlib.h presence... yes
checking for zlib.h... yes
checking for compress2 in -lz... yes
checking for compress2... yes
checking for szlib... suppressed
checking for thread safe support... no
checking whether CLOCK_MONOTONIC is declared... yes
checking for tm_gmtoff in struct tm... yes
checking for global timezone variable... yes
checking for st_blocks in struct stat... yes
checking for _getvideoconfig... no
checking for gettextinfo... no
checking for GetConsoleScreenBufferInfo... no
checking for getpwuid... yes
checking for _scrsize... no
checking for ioctl... yes
checking for struct videoconfig... no
checking for struct text_info... no
checking for TIOCGWINSZ... yes
checking for TIOCGETD... yes
checking for library containing clock_gettime... none required
checking for alarm... yes
checking for clock_gettime... yes
checking for difftime... yes
checking for fork... yes
checking for frexpf... yes
checking for frexpl... yes
checking for gethostname... yes
checking for getrusage... yes
checking for gettimeofday... yes
checking for lstat... yes
checking for rand_r... yes
checking for random... yes
checking for setsysinfo... no
checking for signal... yes
checking for longjmp... yes
checking for setjmp... yes
checking for siglongjmp... yes
checking for sigsetjmp... no
checking for sigprocmask... yes
checking for snprintf... yes
checking for srandom... yes
checking for strdup... yes
checking for symlink... yes
checking for system... yes
checking for strtoll... yes
checking for strtoull... yes
checking for tmpfile... yes
checking for asprintf... yes
checking for vasprintf... yes
checking for vsnprintf... yes
checking for waitpid... yes
checking for an ANSI C-conforming const... yes
checking if the compiler understands  __inline__... yes
checking if the compiler understands __inline... yes
checking if the compiler understands inline... yes
checking for __attribute__ extension... yes
checking for __func__ extension... yes
checking for __FUNCTION__ extension... yes
checking for C99 designated initialization support... yes
checking how to print long long... %ld and %lu
checking Threads support system scope... yes
checking for debug flags... none
checking whether function stack tracking is enabled... no
checking whether metadata trace file code is enabled... no
checking for API tracing... no
checking for instrumented library... no
checking whether to clear file buffers... yes
checking whether a memory checking tool will be used... no
checking for parallel support files... provided by compiler
checking whether a simple MPI-IO C program can be linked... yes
checking prefix for running on one processor... 
checking prefix for running in parallel... mpiexec -n $${NPROCS:=6}
checking for MPE... suppressed
checking whether O_DIRECT is declared... yes
checking for posix_memalign... yes
checking if the direct I/O virtual file driver (VFD) is enabled... no
checking for custom plugin default path definition... /usr/local/hdf5/lib/plugin
checking whether exception handling functions is checked during data conversions... yes
checking whether data accuracy is guaranteed during data conversions... yes
checking if the machine has window style path name... no
checking if using special algorithm to convert long double to (unsigned) long values... no
checking if using special algorithm to convert (unsigned) long to long double values... no
checking if correctly converting long double to (unsigned) long long values... yes
checking if correctly converting (unsigned) long long to long double values... yes
checking additional programs should be built... no
checking if deprecated public symbols are available... yes
checking which version of public symbols to use by default... v18
checking whether to perform strict file format checks... no
checking whether to have library information embedded in the executables... yes
checking if alignment restrictions are strictly enforced... no
configure: creating ./config.lt
config.lt: creating libtool
checking that generated files are newer than configure... done
configure: creating ./config.status
config.status: creating src/libhdf5.settings
config.status: creating Makefile
config.status: creating src/Makefile
config.status: creating test/Makefile
config.status: creating test/testcheck_version.sh
config.status: creating test/testerror.sh
config.status: creating test/H5srcdir_str.h
config.status: creating test/testlibinfo.sh
config.status: creating test/testlinks_env.sh
config.status: creating test/test_plugin.sh
config.status: creating testpar/Makefile
config.status: creating tools/Makefile
config.status: creating tools/h5dump/Makefile
config.status: creating tools/h5dump/h5dump_plugin.sh
config.status: creating tools/h5dump/testh5dump.sh
config.status: creating tools/h5dump/testh5dumppbits.sh
config.status: creating tools/h5dump/testh5dumpxml.sh
config.status: creating tools/h5ls/Makefile
config.status: creating tools/h5ls/h5ls_plugin.sh
config.status: creating tools/h5ls/testh5ls.sh
config.status: creating tools/h5import/Makefile
config.status: creating tools/h5import/h5importtestutil.sh
config.status: creating tools/h5diff/Makefile
config.status: creating tools/h5diff/h5diff_plugin.sh
config.status: creating tools/h5diff/testh5diff.sh
config.status: creating tools/h5diff/testph5diff.sh
config.status: creating tools/h5jam/Makefile
config.status: creating tools/h5jam/testh5jam.sh
config.status: creating tools/h5repack/Makefile
config.status: creating tools/h5repack/h5repack.sh
config.status: creating tools/h5repack/h5repack_plugin.sh
config.status: creating tools/h5copy/Makefile
config.status: creating tools/h5copy/testh5copy.sh
config.status: creating tools/lib/Makefile
config.status: creating tools/misc/Makefile
config.status: creating tools/misc/h5cc
config.status: creating tools/misc/testh5mkgrp.sh
config.status: creating tools/misc/testh5repart.sh
config.status: creating tools/h5stat/testh5stat.sh
config.status: creating tools/h5stat/Makefile
config.status: creating tools/perform/Makefile
config.status: creating examples/Makefile
config.status: creating examples/run-c-ex.sh
config.status: creating examples/testh5cc.sh
config.status: creating c++/Makefile
config.status: creating c++/src/Makefile
config.status: creating c++/src/h5c++
config.status: creating c++/test/Makefile
config.status: creating c++/test/H5srcdir_str.h
config.status: creating c++/examples/Makefile
config.status: creating c++/examples/run-c++-ex.sh
config.status: creating c++/examples/testh5c++.sh
config.status: creating fortran/Makefile
config.status: creating fortran/src/h5fc
config.status: creating fortran/src/Makefile
config.status: creating fortran/test/Makefile
config.status: creating fortran/testpar/Makefile
config.status: creating fortran/examples/Makefile
config.status: creating fortran/examples/run-fortran-ex.sh
config.status: creating fortran/examples/testh5fc.sh
config.status: creating hl/Makefile
config.status: creating hl/src/Makefile
config.status: creating hl/test/Makefile
config.status: creating hl/test/H5srcdir_str.h
config.status: creating hl/tools/Makefile
config.status: creating hl/tools/gif2h5/Makefile
config.status: creating hl/tools/gif2h5/h52giftest.sh
config.status: creating hl/examples/Makefile
config.status: creating hl/examples/run-hlc-ex.sh
config.status: creating hl/c++/Makefile
config.status: creating hl/c++/src/Makefile
config.status: creating hl/c++/test/Makefile
config.status: creating hl/c++/examples/Makefile
config.status: creating hl/c++/examples/run-hlc++-ex.sh
config.status: creating hl/fortran/Makefile
config.status: creating hl/fortran/src/Makefile
config.status: creating hl/fortran/test/Makefile
config.status: creating hl/fortran/examples/Makefile
config.status: creating hl/fortran/examples/run-hlfortran-ex.sh
config.status: creating src/H5config.h
config.status: executing pubconf commands
creating src/H5pubconf.h
Post process src/libhdf5.settings
config.status: executing depfiles commands
config.status: executing libtool commands
            SUMMARY OF THE HDF5 CONFIGURATION
            =================================

General Information:
-------------------
                   HDF5 Version: 1.8.21
                  Configured on: Thu Jul 25 13:33:15 EDT 2019
                  Configured by: hoffmaps@srv-p22-13.cbls.ccr.buffalo.edu
                 Configure mode: production
                    Host system: x86_64-unknown-linux-gnu
              Uname information: Linux srv-p22-13.cbls.ccr.buffalo.edu 3.10.0-957.21.3.el7.x86_64 #1 SMP Tue Jun 18 16:35:19 UTC 2019 x86_64 x86_64 x86_64 GNU/Linux
                       Byte sex: little-endian
                      Libraries: static, shared
             Installation point: /gpfs/scratch/hoffmaps/akrr_project/appker/barere_metal_gen_compute_8core/execs/libs/hdf5-1.8.21

Compiling Options:
------------------
               Compilation Mode: production
                     C Compiler: /util/academic/intel/18.3/compilers_and_libraries_2018.3.222/linux/mpi/intel64/bin/mpiicc ( Intel(R) C Intel(R) 64 Compiler Version 18.0.3.222 Build 20180410)
                         CFLAGS: 
                      H5_CFLAGS: -std=c99  -O3
                      AM_CFLAGS: 
                       CPPFLAGS: 
                    H5_CPPFLAGS: -D_GNU_SOURCE -D_POSIX_C_SOURCE=200112L   -DNDEBUG -UH5_DEBUG_API
                    AM_CPPFLAGS: 
               Shared C Library: yes
               Static C Library: yes
  Statically Linked Executables: no
                        LDFLAGS: 
                     H5_LDFLAGS: 
                     AM_LDFLAGS: 
                Extra libraries: -lz -ldl -lm 
                       Archiver: ar
                         Ranlib: ranlib
              Debugged Packages: 
                    API Tracing: no

Languages:
----------
                        Fortran: no

                            C++: no

Features:
---------
                  Parallel HDF5: yes
             High Level library: yes
                   Threadsafety: no
            Default API Mapping: v18
 With Deprecated Public Symbols: yes
         I/O filters (external): deflate(zlib)
                            MPE: 
                     Direct VFD: no
                        dmalloc: no
Clear file buffers before write: yes
           Using memory checker: no
         Function Stack Tracing: no
      Strict File Format Checks: no
   Optimization Instrumentation: no

```
Then we make. In IOR Deployment it has make -j 4, and this website talks a bit about what that actually means: https://www.cmcrossroads.com/article/pitfalls-and-benefits-gnu-make-parallelization
Basically it makes the different recipies execute in parallel so multiple things can get made at once (speeds it up seems like
```bash
# trying it normally (serial)
make
# yeah this takes a lot longer
make install

# so now the hdf5 libriaries are in libs
```

Installing NetCDF
```bash
#get to application kernel executable directory
cd $AKRR_APPKER_DIR/execs

```

yeah yea same more or less as usual

so what I then did is I pulled down the libs
BUT there's symbolic links so what I did is I just copied the files so I didn't need the links and it seems okay





