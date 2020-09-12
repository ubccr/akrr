
```bash
cd akrr
# copy intel license
cp /opt/intel/licenses/<license>.lic docker/spack/license.lic
# build
docker build -f ./docker/spack/spack.dockerfile -t spack-ubuntu:20.04 .
# check workabilities
docker run -it --rm spack-ubuntu:20.04
```
