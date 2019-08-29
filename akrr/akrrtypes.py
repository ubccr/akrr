"""
Various types for AKRR
"""
from enum import Enum


# enum for batch_scheduler
class QueuingSystemType(Enum):
    slurm = "slurm"
    pbs = "pbs"
    shell = "shell"
    openstack = "openstack"
    # synonyms:
    Slurm = "slurm"
    SLURM = "slurm"
    OpenStack = "openstack"

    @staticmethod
    def get_names():
        return [str(v.value) for v in QueuingSystemType]


