## Making mdtest docker

This directory is largely irrelevant because we're using the ior docker to run mdtest, but these are just some of the files I started working on just in case they might still be useful in the future

NOTE: this is mainly irrelevant since I decided just to use the ior docker to run mdtest, so there's that. But I kept this here in case.

For barebones version it's pretty straightforward, since I'm basically just reusing the ior version, just with calling the mdtest in the script

So just setting it up basically the same as ior, I'm getting this error (or similar) trying to run it
```bash
system msg for write_line failure : Bad file descriptor
PMII_singinit: execv failed: No such file or directory
[unset]:   This singleton init program attempted to access some feature
[unset]:   for which process manager support was required, e.g. spawn or universe_size.
[unset]:   But the necessary mpiexec is not in your path.
Fatal error in MPI_Init: Other MPI error, error stack:
MPIR_Init_thread(805).....: fail failed
MPID_Init(1859)...........: channel initialization failed
MPIDI_CH3_Init(126).......: fail failed
MPID_nem_init_ckpt(857)...: fail failed
MPIDI_CH3I_Seg_commit(427): PMI_KVS_Get returned -1
[unset]: write_line error; fd=-1 buf=:cmd=abort exitcode=69777679
```
If you don't have the LD\_LIBRARY\_PATH it just gives the libgpfs.so error.
srun doesn't work, something weird with mpiexec couldn't find or something. Doing mpirun does appear to work tho... at leas its not giving the same error

Yeah setting the run thing to mpirun, the results seem more or less the same, but it had a bunch of errors of /etc/tmp. something doesn't exist, so I'm not sure what that is.



