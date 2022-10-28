# Tips and Tricks for AKRR Developers

## Local Developer Setup
Often it is important to be able to interactively debug the code while it is doing meaningful work.
We have a docker container to carry unit and regression tests, but debugging through container might be inconvenient.

### 

### Install AKRR
```bash
# assuming akrr is in ~/xdmod_wsp/akrr
# devel_local is in gitignore and whould not be tracked
mkdir -p ~/xdmod_wsp/akrr/devel_local
ln -s ~/xdmod_wsp/akrr/devel_local ~/akrr

# activate python enviroment, either conda, venv or system
source ~/anaconda3/bin/activate
conda activate py_akrr
export PATH=~/xdmod_wsp/akrr/bin:$PATH
# sometimes localhost socket is not working
akrr -vv setup --akrr-db 127.0.0.1

```

```
