# Making HPCC Appkernel Docker Container

## Building Docker Container

```bash
# build binaries
docker build -f ./docker/graph500/spack_builder.dockerfile -t spack-ubuntu-builder:graph500 .
docker run -it --rm  --shm-size=4g spack-ubuntu-builder:graph500

# copy binaries to fresh image
docker build -f ./docker/graph500/spack_installer.dockerfile -t nsimakov/appker:graph500 .

# run tests
docker run -it --rm  --shm-size=4g nsimakov/appker:graph500
docker run -it --rm  --shm-size=4g -e INPUT_PARAM="22 16" nsimakov/appker:graph500
docker run -it --rm  --shm-size=4g nsimakov/appker:graph500 -c gcc_openmpi
docker run -it --rm  --shm-size=4g nsimakov/appker:graph500 -c icc_impi
docker run -it --rm  --shm-size=4g nsimakov/appker:graph500 -c intelver_icc_imkl_impi
docker run -it --rm  --shm-size=4g cnsimakov/appker:graph500 -view graph500_gcc_openmpi_x86_64

# Convert to singularity container
sudo singularity build graph500.simg docker-daemon://nsimakov/appker:graph500
docker push nsimakov/appker:graph500

# run tests
../graph500.simg
../graph500.simg -c icc_impi
../graph500.simg -c gcc_openmpi
../graph500.simg -view graph500_gcc_openmpi_x86_64
```

