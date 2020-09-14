# Making HPCC Appkernel Docker Container

## Building Docker Container

```bash
# build binaries
docker build -f ./docker/hpcg/spack_builder.dockerfile -t spack-ubuntu-builder:hpcg .
# copy binaries to fresh image
docker build -f ./docker/hpcg/spack_installer.dockerfile -t containers:hpcg .

# run tests
docker run -it --rm  --shm-size=4g containers:hpcg
docker run -it --rm  --shm-size=4g containers:hpcg -c gcc_openmpi_openblas
docker run -it --rm  --shm-size=4g containers:hpcg -v nwchem_icc_mkl_impi_x86_64

# Convert to singularity container
sudo singularity build hpcg.simg docker-daemon://containers:hpcg

# run tests
./hpcg.simg
./hpcg.simg -c gcc_openmpi_openblas
./hpcg.simg -view nwchem_icc_mkl_impi_x86_64
```

