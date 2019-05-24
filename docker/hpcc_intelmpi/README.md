## Files for creating HPCC Docker image (uses Intel-mpi)

HPCC - High Performance Compute Competition, a benchmarking technique

Intel-mpi version used: 2018.3

```bash
# building the Dockerfile
docker build -t hpcc_intelmpi_centos7 .

# running it (interactively)
docker run -it hpcc_intelmpi_centos7
```


