## Only for additional notes
in case anything in the docs is weird or confusing.

### hpcc

Nothing weird happened

### hpcg

Using xhpcg_skx
Nothing weird happened

### namd

Using namd/2.12b1-multicore to line up with singularity
Gave me a weird error first time round
```bash
Running command: nodelist /util/academic/namd/2.12b1/NAMD_2.12b1_Linux-x86_64-multicore/namd2 ./input.namd +p8 ++nodelist

/util/academic/namd/2.12b1/NAMD_2.12b1_Linux-x86_64-multicore/charmrun: line 32: exec: nodelist: not found
```
I believe it was an error with the fact that it is the multicore build, meaning nodelist doesn't really make sense for it.
So I changed the RUN_APPKERNEL to line up with what I had in my docker
```bash
RUN_APPKERNEL="$charmrun_bin $EXE +p$AKRR_CORES ./input.namd"
```
That then makes it work, so it looks like multicore doesn't use nodelist.
It discusses this a little bit here: https://www.ks.uiuc.edu/Research/namd/2.12/notes.html

###  gamess

Using gamess/11Nov2017R3 to match up with docker
Set EXE=/util/academic/gamess/11Nov2017R3/impi/gamess/gamess.$VERNO.x
in gamess.app.conf
NOTE: it appears if you want to run it in parallel, you switch AKRR_NODES and AKRR_CORESE_PER_NODE
So the RUN_APPKERNEL should look like
```bash
RUN_APPKERNEL="$AKRR_APPKER_DIR/execs/gamess/rungms $INPUT $VERNO $AKRR_CORES_PER_NODE $AKRR_NODES"
```
That appears to make it run fine.

### nwchem
When I created the app, RUN_APPKERNEL looked different from what was in nwchem_deployment
```bash
RUN_APPKERNEL="srun --mpi=pmi2 $EXE $INPUT"
```
I didn't touch it, and it appears to have worked fine, there were no errors that came up







