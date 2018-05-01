FROM nsimakov/akrr_ready_centos_slurm_single_host_wlm:1


LABEL description="image to run tests with git repo location like in shippable"

# copy repo
VOLUME /root/src/github.com/nsimakov/akrr

