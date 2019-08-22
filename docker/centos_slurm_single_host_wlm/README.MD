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

#delete image and container as they are not needed
#docker container rm slurm_rpm_maker
docker image rm slurm_rpm_maker:latest
```

## Making Single Host Slurm WLM Image

```bash
#make image, in docker/centos_slurm_single_host_wlm/
docker build -t nsimakov/centos_slurm_single_host_wlm:latest -f ./centos_slurm_single_host_wlm/Dockerfile .

#run
docker run --name centos_slurm_single_host_wlm -h centos_slurm_single_host_wlm \
       --rm -it nsimakov/centos_slurm_single_host_wlm:latest

#push to docker cloud
docker push nsimakov/centos_slurm_single_host_wlm:latest
```

## Making Single Host Slurm WLM Image with Dependencies Installed for AKRR

```bash
#make image, in docker/centos_slurm_single_host_wlm/
docker build -t nsimakov/akrr_ready_centos_slurm_single_host_wlm:latest \
       -f ./centos_slurm_single_host_wlm/DockerfileAKRRReady .

#run

#push to docker cloud
docker push nsimakov/akrr_ready_centos_slurm_single_host_wlm:latest
```

## Testing AKRR Image

```bash
#make image in akrr root directory
docker build -t pseudo_repo/akrr_centos_slurm_single_host_wlm:latest .

#run
docker run -it --rm pseudo_repo/akrr_centos_slurm_single_host_wlm:latest bash

```
