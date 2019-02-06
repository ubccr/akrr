# How to Run Tests

Running all tests with docker image.

Run in AKRR top directory:

```bash
#remove older config and log, clean user ownership
sudo chown -R mikola:mikola ../akrr;rm -rf etc log;\
find . -type f -name '__pycache__' -exec rm -rf {} + ;\
find . -type f -name '*.pyc' -exec rm -rf {} + ;
# build image
sudo docker build -t akrr_test .
#run
sudo docker run -v `pwd`:/root/src/github.com/ubccr/akrr -it --rm akrr_test
```
