motorBikeQ is example from OpenFOAM-v2206/tutorials/incompressible/simpleFoam/motorBike.

Few modifications were made (affecting simulation):

1. Quadrupling (thus Q at the end) block sizes: (20 8 8) -> (80 32 32)
2. Using scotch method for decompose.
3. numberOfSubdomains set by AllrunAKRR script

Other modifications:
1. Added timings in AllrunAKRR script, used as final statistics
2. add cat of log.checkMesh
3. add printing last info on simulated timestep from log.simpleFoam

motorBikeQ_v18 same as motorBikeQ but for openfoam of version 18
