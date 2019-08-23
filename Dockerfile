# Run regtest1 in docker
FROM nsimakov/akrr_ready_centos_slurm_single_host_wlm:latest

LABEL description="image to run tests manually"

# copy repo
VOLUME /home/akrruser/src/github.com/ubccr/akrr

ENV REPO_FULL_NAME=ubccr/akrr

ENTRYPOINT ["/usr/local/sbin/cmd_start"]
CMD ["-set-no-exit-on-fail", "self_contained_slurm_wlm", "bash_akrruser"]
