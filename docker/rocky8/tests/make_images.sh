#!/bin/bash

#exit on any error
set -e

###################
## Making Slurm RPMs

#make image, in docker/centos7/centos_slurm_single_host_wlm/
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

###################
## Making Single Host Slurm WLM Image

#make image, in docker/centos7/centos_slurm_single_host_wlm/
docker build -t nsimakov/centos_slurm_single_host_wlm:1 .

#push to docker cloud
docker push nsimakov/centos_slurm_single_host_wlm:1

#rm RPMs we don't need them any more
rm -rf RPMS

###################
## Making Single Host Slurm WLM Image with Dependencies Installed for AKRR

#make image, in docker/centos7/centos_slurm_single_host_wlm/
docker build -t nsimakov/akrr_ready_centos_slurm_single_host_wlm:1 -f DockerfileAKRRReady .

#push to docker cloud
docker push nsimakov/akrr_ready_centos_slurm_single_host_wlm:1
