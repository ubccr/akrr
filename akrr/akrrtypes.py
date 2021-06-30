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
    googlecloud = "googlecloud"
    # synonyms:
    Slurm = "slurm"
    SLURM = "slurm"
    OpenStack = "openstack"
    GoogleCloud = "googlecloud"
    gcloud = "googlecloud"
    @staticmethod
    def get_names():
        return [str(v.value) for v in QueuingSystemType]
