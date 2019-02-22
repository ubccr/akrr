# Run regtest1 in docker
FROM nsimakov/akrr_ready_centos_slurm_single_host_wlm:1


LABEL description="image to run tests with git repo location like in shippable"

# copy repo
VOLUME /root/src/github.com/ubccr/akrr

ENV REPO_FULL_NAME=ubccr/akrr

ENTRYPOINT ["/sbin/cmd_start"]
CMD ["-set-no-exit-on-fail", "self_contained_slurm_wlm", "bash"]
