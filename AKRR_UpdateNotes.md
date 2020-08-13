# IMB

in new version binaries now in root. Default configuration was updated, thus for older config
executabledir, executable, input_param needed to be reset to old values.

was:
```python
executabledir = "execs/imb/src"
executable = executabledir + "/IMB-MPI1"
# Not really input
input_param = executabledir + "/IMB-EXT"
```
became
```python
executabledir = "execs/imb"
executable = executabledir + "/IMB-MPI1"
# Not really input
input_param = executabledir + "/IMB-EXT"
```