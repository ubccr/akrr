# Directory for Namd Docker

Because I was working with docker and on OpenStack, the docker is meant to only be used on one node.
Accordingly, I used the namd multicore binary.

To get this binary, you can either go to this site: https://www.ks.uiuc.edu/Development/Download/download.cgi?PackageName=NAMD

And pick out the multicore binary that works best.

To try and guarantee that I was running the same namd in singularity and bare metal, I got my namd binary from UB-HPC.

It's as easy as this:
```bash
module avail namd
```

```text
---------------------------------- /util/academic/modulefiles/Core -----------------------------------
   namd/2.8-MPI-CUDA             namd/2.10-ibverbs          (D)    namd/2.12b1-multicore      (L)
   namd/2.9b2-IBVERBS            namd/2.10-multicore-CUDA          namd/2.12-ibverbs-smp-CUDA
   namd/2.9-IBVERBS-SRC          namd/2.10-multicore-MIC           namd/2.12-ibverbs-smp
   namd/2.9-IBVERBS              namd/2.10-multicore               namd/2.12-ibverbs
   namd/2.9-MPI-CUDA             namd/2.11-ibverbs-smp-CUDA        namd/2.12-multicore-CUDA
   namd/2.9-MPI                  namd/2.11-MPI                     namd/2.12-multicore
   namd/2.10-ibverbs-smp-CUDA    namd/2.11-multicore-CUDA
   namd/2.10-ibverbs-smp         namd/2.12b1-ibverbs

```
```bash
module load namd/2.12b1-multicore

echo `which namd2`

/util/academic/namd/2.12b1/NAMD_2.12b1_Linux-x86_64-multicore/namd2

```
So you just want to get the directory that the binary is in (in this case NAMD\_2.12b1\_Linux-x86\_64-multicore) and put it in your execs directory.
Then from there you just have to modify the Dockerfile slightly to have the correct namd name.

Once you have that binary all set up you can build the Docker image

### Flags to use

