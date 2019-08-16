Docker Container To Test AKRR Upgrade

Building
```bash
docker build -t pseudo_repo/centos-openxdmod-appkernels-update .
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