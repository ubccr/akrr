#!/bin/bash
echo "NOT UP TO DATE!!!! COPY FROM README"
#exit on any error
set -e

###################
## Making Slurm RPMs

# make slurm rpm making image
[[ -d "./tests/RPMS" ]] && rm -rf "./tests/RPMS"
# make image, in docker/
docker build -t slurm_rpm_builder:latest -f ./tests/slurm_rpm_builder.dockerfile .

# create directory for RPMS storage
[[ ! -d "./tests/RPMS" ]] && mkdir -p tests/RPMS

# make slurm RPMS
docker run --name slurm_rpm_builder -h slurm_rpm_builder \
           -v `pwd`/tests/RPMS:/RPMS \
           --rm \
           -it slurm_rpm_builder:latest make_slurm_rpms

# change owner on RPMS
sudo chown -R $USER:$USER ./tests/RPMS

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
