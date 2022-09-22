FROM nsimakov/slurm_single_host_wlm:latest

LABEL description="container for akrr tests"

# install dependencies
# Needed for shippable:
#    git sudo
# Needed to build RPM:
#    rpm-build
# Needed to run:
#    python36 python36-libs python36-bottle python36-requests python36-mysql python36-typing
#    python3-prettytable
#    openssl openssh-clients crontabs
# Needed for tests:
#     with yum: python34-PyYAML python34-pip gromacs
#     with pip: pylint coverage pytest pytest-cov pytest-dependency
#
RUN dnf -y update && \
    dnf config-manager --set-enabled powertools && \
    dnf -y install epel-release && crb enable && \
    dnf -y update && \
    dnf -y install --setopt=tsflags=nodocs \
        git sudo \
        python3 python3-libs python3-bottle python3-requests python3-mysqlclient python3-typing-extensions \
        python3-prettytable python3-PyYAML python3-pip \
        python3-dateutil python3-psutil \
        python3-sqlalchemy \
        openssl  openssh-clients crontabs gromacs \
        rpm-build && \
    dnf clean all && \
    pip3 install --upgrade pip && \
    pip3 install bottle && \
    pip3 install pylint coverage pytest pytest-cov pytest-dependency

COPY ./utils/cmd_setup ./utils/cmd_start ./utils/cmd_stop /usr/local/sbin/

# reset entry point
ENTRYPOINT []
CMD []
