# Directory with Dockers for nwchem

The nwchem Docker has 2 "versions"

This one is based off of an existing nwchem docker from Dockerhub: nwchemorg/nwchem-qc:latest

The Dockerfile is just adding a few things to work with akrr, namely adding a script that runs the appropriate amount of processes with mpirun.

So you should be able to just build the Docker image right away.

For running the docker, you do need to specify some extra things to ensure that everything runs appropriately

```bash
docker run --shm-size 8g --cap-add=SYS_PTRACE <nwchem docker>

```
The other docker directory has the nwchem version used on ubhpc.



