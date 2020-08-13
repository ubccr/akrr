## Notes on working with singularity on the test/dev cluster

Update: so we went and ran singularity and bare metal on the preprod things
and for hpcc, singualrity was performing WAY better than bare metal, and we didn't really know why
So, after Nikolay and I checked it out, it turns out that when we were requesting "exclusive" for our jobs, it was really allocating the whole node for us. Srun (bare metal) knew that we only requested 8 jobs on the one node, so it was splitting things up normally. However, mpirun just saw all the nodes we had access to, so it split up the 8 processes on the separate nodes and so because now it had more memory to use, it ran faster.
Removing the exclusive tag seems to have fixed the issue we had, and now it should be running the same regardless. 









