# Making HPCC Appkernel Docker Container

## Building Docker Container

```bash
# build binaries
docker build -f ./docker/hpcg/spack_builder.dockerfile -t spack-ubuntu-builder:hpcg .
# copy binaries to fresh image
docker build -f ./docker/hpcg/spack_installer.dockerfile -t nsimakov/appker:hpcg .

# run tests
docker run -it --rm  --shm-size=4g nsimakov/appker:hpcg
docker run -it --rm  --shm-size=4g nsimakov/appker:hpcg -c gcc_openmpi
docker run -it --rm  --shm-size=4g nsimakov/appker:hpcg -c icc_impi
docker run -it --rm  --shm-size=4g nsimakov/appker:hpcg -c intelver_icc_imkl_impi
docker run -it --rm  --shm-size=4g cnsimakov/appker:hpcg -view hpcg_intelver_icc_imkl_impi_sandybridge

# Convert to singularity container
sudo singularity build hpcg.simg docker-daemon://nsimakov/appker:hpcg
docker push nsimakov/appker:hpcg

# run tests
../hpcg.simg
../hpcg.simg -c icc_impi
../hpcg.simg -c gcc_openmpi
../hpcg.simg -c hpcg_intelver_icc_imkl_impi
../hpcg.simg -view nwchem_icc_mkl_impi_x86_64
```

