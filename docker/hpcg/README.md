# Directory and files needed for HPCG Appkernel

This one is relatively straightforward, since the binaries being used here come when intel mkl is installed in the Docker, so you don't have to worry about getting any binaries or anything.
(Optimized for Intel processors of course then)

If you do want to have your own binaries, you would need to modify the Dockerfile and script a decent bit.

## Setup of this directory
- Dockerfile - used to make the Docker image
- execs/bin - location of akrr help scripts
- inputs/hpcg - location of hpcg input to use
- scripts - location of script that sets up and runs the hpcg benchmark

