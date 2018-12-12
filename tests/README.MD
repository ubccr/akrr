# How to Run Tests

Running all tests with docker image.

Run in AKRR top directory:

```bash
#remove older config and log, clean user ownership
sudo chown -R mikola:mikola ../akrr;rm -rf etc log
# build image
sudo docker build -t akrr_test .
#run
docker run -v `pwd`:/root/src/github.com/ubccr/akrr -it --rm akrr_test
```