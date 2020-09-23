
```bash
cd akrr
# copy intel license
cp /opt/intel/licenses/<license>.lic docker/spack/license.lic
# build
docker build -f ./docker/spack/spack.dockerfile -t spack-ubuntu:20.04 .
# build runner image
docker build -f ./docker/spack/spack_runner.dockerfile -t nsimakov/appker:base .
# check workabilities
docker run -it --rm spack-ubuntu:20.04
docker run -it --rm spack-runner-ubuntu:20.04

docker push nsimakov/appker:base

docker build -f ./docker/spack/spack_runner.dockerfile -t nsimakov/appker:base .
```
