# Centos-7 based Slurm WLM for Single Host

This docker image to run Centos-7 based container
with pre-installed Slurm Workload Manager to
Run 

## Creating Image

```
!!!
Docker build should be executed in akrr_src/docker directory
(one level up from here)
```

### Making Slurm RPMs

First we need slurm RPMs.
DockerfileMakeSlurmRPM describes simple image for centos 7 rpm making.
Here is listing on the whole process

```bash
[[ -d "./centos_slurm_single_host_wlm/RPMS" ]] && rm -rf "./centos_slurm_single_host_wlm/RPMS" 
#make image, in docker/centos_slurm_single_host_wlm/
docker build -t slurm_rpm_maker:latest -f ./centos_slurm_single_host_wlm/DockerfileMakeSlurmRPM .

#create directory for RPMS storage
[[ ! -d "./centos_slurm_single_host_wlm/RPMS" ]] && mkdir -p centos_slurm_single_host_wlm/RPMS

#make slurm RPMS
docker run --name slurm_rpm_maker -h slurm_rpm_maker \
           -v `pwd`/centos_slurm_single_host_wlm/RPMS:/RPMS \
           --rm \
           -it slurm_rpm_maker:latest make_slurm_rpms
```docker/centos_slurm_single_host_wlm/README.MD:35

## Making Single Host Slurm WLM Image

```bash
#make image, in docker/centos_slurm_single_host_wlm/
docker build -t nsimakov/centos_slurm_single_host_wlm:latest -f ./centos_slurm_single_host_wlm/Dockerfile .

#run (to check workability)
docker run --name centos_slurm_single_host_wlm -h centos_slurm_single_host_wlm \
       --rm -it nsimakov/centos_slurm_single_host_wlm:latest
#in conteiner run something like squeue to check that it is working
#push to docker cloud
docker push nsimakov/centos_slurm_single_host_wlm:latest
```

## Making Single Host Slurm WLM Image with Dependencies Installed for AKRR

```bash
#make image, in docker/centos_slurm_single_host_wlm/
docker build -t nsimakov/akrr_ready_centos_slurm_single_host_wlm:latest \
       -f ./centos_slurm_single_host_wlm/DockerfileAKRRReady .

#run (to check workability)
docker run -it --rm \
    -v ~/xmdow_wsp/akrr:/root/src/github.com/ubccr/akrr \
    -e REPO_FULL_NAME=ubccr/akrr \
    nsimakov/akrr_ready_centos_slurm_single_host_wlm:latest bash

#push to docker cloud
docker push nsimakov/akrr_ready_centos_slurm_single_host_wlm:latest
```

## Testing AKRR Image

```bash
# make image in akrr root directory
docker build -t pseudo_repo/akrr_runtest:latest -f Dockerfile_run_tests .

# by default after test you'll drop to akrruser bash
# run devel test (i.e. build by setup.py devel)
docker run -it --rm -v $HOME/xdmod_wsp/akrr:/home/akrruser/akrr_src pseudo_repo/akrr_runtest:latest
# run rpm test
docker run -it --rm -e AKRR_SETUP_WAY=rpm  -v $HOME/xdmod_wsp/akrr:/home/akrruser/akrr_src \
    pseudo_repo/akrr_runtest:latest
# run in source test
docker run -it --rm -e AKRR_SETUP_WAY=src  -v $HOME/xdmod_wsp/akrr:/home/akrruser/akrr_src \
    pseudo_repo/akrr_runtest:latest
# run in source test with non default user home
docker run -it --rm -e AKRR_SETUP_WAY=src -e AKRR_SETUP_HOME=/home/akrruser/akrrhome\
    -v $HOMExdmod_wsp/akrr:/home/akrruser/akrr_src \
    pseudo_repo/akrr_runtest:latest
```
