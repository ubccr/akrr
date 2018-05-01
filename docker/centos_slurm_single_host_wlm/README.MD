
# Centos-7 based Slurm WLM for Single Host

This docker image to run Centos-7 based container
with pre-installed Slurm Workload Manager to
Run 

## Creating Image

### Making Slurm RPMs

First we need slurm RPMs.
DockerfileMakeSlurmRPM describes simple image for centos 7 rpm making.
Here is listing on the whole process
  
```bash
#make image, in docker/centos_slurm_single_host_wlm/
docker build -t slurm_rpm_maker:1 -f DockerfileMakeSlurmRPM .

#create directory for RPMS storage
mkdir -p RPMS

#make slurm RPMS
docker run --name slurm_rpm_maker -h slurm_rpm_maker \
           -v `pwd`/RPMS:/RPMS \
           --rm \
           -it slurm_rpm_maker:1 make_slurm_rpms

#delete image and container as they are not needed
#docker container rm slurm_rpm_maker
docker image rm slurm_rpm_maker:1
```

## Making Single Host Slurm WLM Image

```bash
#make image, in docker/centos_slurm_single_host_wlm/
docker build -t nsimakov/centos_slurm_single_host_wlm:1 .

#run
docker run --name centos_slurm_single_host_wlm -h centos_slurm_single_host_wlm \
       --rm
       -it nsimakov/centos_slurm_single_host_wlm:1 

#push to docker cloud
docker push nsimakov/centos_slurm_single_host_wlm:1
```

## Making Single Host Slurm WLM Image with Dependencies Installed for AKRR

```bash
#make image, in docker/centos_slurm_single_host_wlm/
docker build -t nsimakov/akrr_ready_centos_slurm_single_host_wlm:1 -f DockerfileAKRRReady .

#run

#push to docker cloud
docker push nsimakov/akrr_ready_centos_slurm_single_host_wlm:1
```

## Testing AKRR Image

```bash
#make image in akrr root
docker build -t pseudo_repo/akrr_centos_slurm_single_host_wlm:latest .

#run
docker run -it --rm pseudo_repo/akrr_centos_slurm_single_host_wlm:latest bash

```
