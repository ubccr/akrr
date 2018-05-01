FROM nsimakov/akrr_ready_centos_slurm_single_host_wlm:1

LABEL description="centos for akrr tests"

# copy repo
COPY . /root/akrr
WORKDIR /root/akrr
