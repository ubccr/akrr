# Tests for CI through Shippable

shippable clone repository:
```bash
git clone https://github.com/nsimakov/akrr.git /root/src/github.com/nsimakov/akrr
```

## Debugging Shippable

Here is notes for debugging Shippable CI

### Start conteiner with source code at shippable location
#### Using akrr_ready_centos_slurm_single_host_wlm and git clone

```bash

# Start container
docker run -it --rm nsimakov/akrr_ready_centos_slurm_single_host_wlm:1 bash

# Get source code
git clone https://github.com/nsimakov/akrr.git /root/src/github.com/nsimakov/akrr
```

#### Connect source code through volume

Good side code can be modified on host and can be run on uncommitted code.
Bad side root user can affect files.

```bash
docker build -t pseudo_repo/akrr_centos_slurm_single_host_wlm:latest .
docker run -v `pwd`:/root/src/github.com/nsimakov/akrr -it --rm \
       pseudo_repo/akrr_centos_slurm_single_host_wlm:latest bash
```

### Start tests
```bash
# Here is tests, which is in ci portion of shippable.yml
# Start all daemons
cmd_start self_contained_slurm_wlm
# Run tests
export PATH=/root/src/github.com/nsimakov/akrr/bin:/root/src/github.com/nsimakov/akrr/test/bin:$PATH
/root/src/github.com/nsimakov/akrr/tests/regtest1/run_test.sh setup

```
