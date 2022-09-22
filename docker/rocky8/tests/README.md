# Rocky 8 Based Containers for Tests and Development

## Slurm WLM for Single Host

This docker image to run Slurm Workload Manager on single host

### Creating Image

```
!!!
Docker build should be executed in <akrr_root>/docker/rocky8 directory
(one level up from here)
```

### Making Slurm RPMs

First we need slurm RPMs.
`slurm_rpm_builder.dockerfile` describes simple image for rpm making.
Here is listing on the whole process

```bash
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
```

### Making Single Host Slurm WLM Image

```bash
# make image, in docker/centos7/tests/
docker build -t nsimakov/slurm_single_host_wlm:latest -f ./tests/slurm_single_host_wlm.dockerfile .

# run (to check workability: check sinfo, squeue, salloc -N 1 and so on)
docker run --name tests -h tests \
       --rm -it nsimakov/slurm_single_host_wlm:latest
# in conteiner run something like squeue to check that it is working
# push to docker cloud
docker push nsimakov/slurm_single_host_wlm:latest
```

## Making Test Container Ready for AKRR

```bash
# make image
docker build -t nsimakov/akrr_ready:latest \
       -f ./tests/akrr_ready.dockerfile .

# run (to check workability)
docker run -it --rm \
    -v ~/xmdow_wsp/akrr:/root/src/github.com/ubccr/akrr \
    -e REPO_FULL_NAME=ubccr/akrr \
    nsimakov/akrr_ready:latest bash

# push to docker cloud
docker push nsimakov/akrr_ready:latest
```

## Testing AKRR Image

```bash
# make image in akrr root directory
docker build -t pseudo_repo/akrr_run_tests:latest -f ./docker/rocky8/tests/akrr_run_tests.dockerfile .

# by default after test you'll drop to akrruser bash
# run devel test (i.e. build by setup.py devel)
docker run -it --rm -v $HOME/xdmod_wsp/akrr:/home/akrruser/akrr_src pseudo_repo/akrr_run_tests:latest
# run rpm test
docker run -it --rm -e AKRR_SETUP_WAY=rpm  -v $HOME/xdmod_wsp/akrr:/home/akrruser/akrr_src \
    pseudo_repo/akrr_run_tests:latest
# run in source test
docker run -it --rm -e AKRR_SETUP_WAY=src  -v $HOME/xdmod_wsp/akrr:/home/akrruser/akrr_src \
    pseudo_repo/akrr_run_tests:latest
# run in source test with non default user home
docker run -it --rm -e AKRR_SETUP_WAY=src -e AKRR_SETUP_HOME=/home/akrruser/akrrhome\
    -v $HOMExdmod_wsp/akrr:/home/akrruser/akrr_src \
    pseudo_repo/akrr_run_tests:latest
```

# Other Tips and Tricks for Dev Needs
## Run Copy of Appkernel

```bash
docker run -it --rm --name akrr -h akrr \
    -v /home/nikolays/xdmod_wsp/access_akrr/mysql:/var/lib/mysql \
    -v /home/nikolays/xdmod_wsp/access_akrr/akrr/akrr_home:/home/akrruser/akrr \
    -p 3370:3306 -p 2270:22 \
    nsimakov/akrr_ready_tests:latest bash
```

```bash
docker run -it --rm --name akrr -h akrr \
    -v /home/nikolays/xdmod_wsp/access_akrr/mysql:/var/lib/mysql \
    -v /home/nikolays/xdmod_wsp/access_akrr/akrr/akrr_home:/home/akrruser/akrr \
    -p 3370:3306 -p 2270:22 \
    nsimakov/akrr_ready_tests:latest cmd_start sshd mysqld bash
```
