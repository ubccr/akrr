Docker Container To Test AKRR Upgrade

Building
```bash
# in akrr_src/docker directory (one level up from here)
docker build -t pseudo_repo/centos-openxdmod-appkernels-update -f ./update_test/Dockerfile .
```

Starting container
Building
```bash
docker run --rm -it -h xdmod --name centos-openxdmod-appkernels-update --shm-size 2g \
-v ~/xdmod_wsp/xdmod:/root/xdmod \
-v ~/xdmod_wsp/xdmod-docker:/root/xdmod-docker \
-v ~/xdmod_wsp/akrr:/home/akrruser/akrr-src \
-p 3310:3306 -p 8010:8080 -p 2210:22 \
pseudo_repo/centos-openxdmod-appkernels-update
```

Building
```bash
# in akrr_src directory (one level up from here)
docker build -t nsimakov/centos_akrr_update_test:1_5b -f ./docker/update_test/Dockerfile_UpdateReady .
```


```bash
docker run -it --rm --shm-size 2g --name centos_akrr_update_test_1_5b -h xdmod \
    -v ~/xdmod_wsp:/home/akrruser/xdmod_wsp \
    -v ~/xdmod_wsp/akrr:/home/akrruser/akrr_src \
    -v ~/xdmod_wsp/xdmod:/root/xdmod \
    -v ~/xdmod_wsp/xdmod-appkernels:/root/xdmod-appkernels \
    -v ~/xdmod_wsp/xdmod-docker:/root/xdmod-docker \
    -p 10080:8080 -p 13306:3306 -p 10022:22  -p 19000:9000 \
    nsimakov/centos_akrr_update_test:1_5b

```