# initial image for XDMoD CI
FROM tas-tools-ext-01.ccr.xdmod.org/centos7_6-open8.1.2:latest

# copy setup script and daemons starters
COPY ./cmd_setup ./cmd_start ./cmd_stop /usr/local/sbin/

# add akrruser user
ENV DOCKER_USER=akrruser \
    DOCKER_PASSWORD=akrruser \
    DOCKER_UID=1000 \
    DOCKER_GID=1000 \
    DOCKER_SHELL=/bin/bash
ENV DOCKER_GROUP=$DOCKER_USER \
    DOCKER_HOME=/home/$DOCKER_USER \
    AKRRUSER=$DOCKER_USER \
    AKRRUSER_HOME=/home/$DOCKER_USER


RUN groupadd -g $DOCKER_GID $DOCKER_GROUP && \
    useradd -m -u $DOCKER_UID -g $DOCKER_GID -s $DOCKER_SHELL -G wheel $DOCKER_USER && \
    echo "$DOCKER_USER ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers && \
    echo "$DOCKER_USER:$DOCKER_PASSWORD" |chpasswd && \
    echo 'root:root' |chpasswd

RUN cmd_setup sshd xdebug
RUN cmd_setup xdmod_install_xdmod_appkernels akrr-1.0_1month xdmod_appkernels

USER root
ENTRYPOINT ["/usr/local/sbin/cmd_start", "-set-no-exit-on-fail", "sshd", "~/bin/services start", "akrr_v1"]
CMD ["bash"]
