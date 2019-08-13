Notes on errors/things discovered while working with Singularity on dev cluster

Overview of Singularity and Docker interplay: https://www.sylabs.io/guides/3.2/user-guide/singularity_and_docker.html#

Singularity does allow the use of Docker images to run.
Some cases where behavior might not be exactly as expected...

1) ==========

If the Dockerfile for a Docker image uses the command WORKDIR to change the working directory before running an ENTRYPOINT script, most likely the script will not be found, since singularity starts a docker differently.

Example (in Dockerfile):
```bash
WORKDIR /code

ENTRYPOINT [ "entrypoint_script.sh" ]
```

If you try to run this through Singularity like below, you may get an error like the one shown

```bash
$ singularity run awesome_docker_container

/.singularity.d/runscript: line 39: /path/to/where/you/ran/it/from/entrypoint_script.sh: No such file or directory

```
The way to avoid this is to just use absolute paths in the Dockerfile when possible, and then cd where you need to be at the start of the entrypoint script.
This seems to be the simplest workaround if you have access to the Dockerfile. 
If you only have the Docker image, then you may have to try and find out where the entrypoint script is in the image to make Singularity start in that directory. 
The conundrum is discussed more at length here: https://github.com/sylabs/singularity/issues/380

2) ==========

Was getting some issues with getting a Singularity file setup. Something about no space left on device? This happened when I was just on regular huey, not on one of the nodes yet.
Command and output:
```bash
$ singularity pull --docker-login docker://pshoff/akrr_benchmarks:hpcc
WARNING: Authentication token file not found : Only pulls of public images will succeed
Enter Docker Username: pshoff
Enter Docker Password: 
INFO:    Starting build...
Getting image source signatures
Copying blob sha256:8ba884070f611d31cb2c42eddb691319dc9facf5e0ec67672fcfa135181ab3df
 71.91 MiB / 71.91 MiB [====================================================] 7s
Copying blob sha256:bbea64bb0583c7766df6735eb43199da06418bd11754f6b31501602d7cf19824
 163.39 MiB / 163.39 MiB [=================================================] 15s
Copying blob sha256:8829e20024c34823a186d0c50d0577f67093d1a1130d611ad450f4986af777d6
 24.55 MiB / 24.55 MiB [====================================================] 2s
Copying blob sha256:8f23ce40c29f8cc9c9394a417780172af737676111d158f14b52416025603ae4
 2.12 KiB / 2.12 KiB [======================================================] 0s
Copying blob sha256:f31afdf510b46e80d6da41c9720dd6c2deddd1eaf72de3e9634bbc50f622d368
 1.80 KiB / 1.80 KiB [======================================================] 0s
Copying blob sha256:6f10e04b2015f5603c558bc1a0dd98c03e9ccad0ce2ea22dd3444cdb4b85015b
 24.55 MiB / 24.55 MiB [====================================================] 2s
Copying config sha256:09133414c2457349d0ea5997505881b14c30551680160c54caab2903432add6e
 4.25 KiB / 4.25 KiB [======================================================] 0s
Writing manifest to image destination
Storing signatures
FATAL:   Unable to pull docker://pshoff/akrr_benchmarks:hpcc: packer failed to pack: While unpacking tmpfs: unpack: error extracting layer: unable to copy: write /tmp/sbuild-883161459/fs/opt/intel/compilers_and_libraries_2018.3.222/linux/mpi/intel64/lib/debug_mt/libmpi.a: no space left on device
```

And I ran it from my singularity cache directory at /gpfs/scratch/hoffmaps/singularity_cache
Once I got a job allocation and sshed onto a node, it worked fine and made the .sif file okay.

Unsure why the issue is happening.
Perhaps it has to do with the Cache directory? Maybe you have to declare it to be a different location, see https://singularity.lbl.gov/faq#no-space-left-on-device 
But unsure if this was the actual problem.

3) ==========

For the file structure in a Singularity container, (it appears) all files are owned by root, regardless of whether or not the files where chown-ed in the Dockerfile to be owned by another user in the container (at least, from what I could tell). In my case, I was making all the files owned by hpccuser in the Dockerfile, assuming that therefore all permissions would be correct when accessing files. However, in the Singularity container, all files are owned by root despite my chowning them.
You can check this out yourself by doing:
```bash
$ singularity shell singularity_executable.sif
```

This can result in permissions being unexpected, usually meaning you can't access what you thought you could. In most cases this would not cause too much of an issue, since Docker images often make everything available to everyone or don't worry about having another user other than root on their images (this is speaking from a very limited Docker experience)

If you have access to the Dockerfile and all the necessary files being used in the Docker image, the workaround would be either to change the permissions on the files and re-build the docker image, or not to bother at all with other users and just build the image with only the root user. Unsure how much this helps but it would allow more flexible permissions at least.


4) ==========

It appears that there could be some unexpected behavior with environment variables like $HOME and $TMP, since they get mounted on the file system that is running the singularity. So if the Dockerfile or especially the run script is using them, it probably won't work as expected.


5) ==========

After a little while of just pulling singularity down regularly, I got this error:
```bash
FATAL:   Unable to pull docker://pshoff/akrr_benchmarks:hpcc: packer failed to pack: While unpacking tmpfs: unpack: error extracting layer: unable to delete whiteout path: lstat /tmp/sbuild-793549952/fs/usr/local/appker/inputs/hpcc/.wh..opq: permission denied
```
This happened after I chmoded a lot of my files to be 007 in my Dockerfile (testing something out). Changing them back to 7** seems to fix this error, so just pay attention to permissions in the Dockerfile. In most cases you shouldn't even get this error unless you did something like chmoding files to be 007, at least in my case. 

Regardless, its an error dealing with the files in the docker image, not with files in the host system

 


