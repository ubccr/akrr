# resource processes per node look up dictionary

resource_ppn_lookup = {
    'edge': 8,  # edge.ccr.buffalo.edu, None
    'u2': 2,  # _bono.ccr.buffalo.edu_, 1024 total cores Xeon (Family 15, Model 4) @ 3.0/3.2GHz (2 cores, 2/4/8 GB per node)
    'india': 8,  # india.futuregrid.org, Nehalem-EP/Gainestown X5570 @ 2.93GHz (8 cores, 24 GB per node)
    'sierra': 8,  # sierra.futuregrid.org, None
    'hotel': 8,  # hotel.futuregrid.org, None
    'alamo': 8,  # alamo.futuregrid.org, None
    'xray': 8,  # xray.futuregrid.org, None
    'trestles': 32,  # trestles.sdsc.edu, 32
    'edge12core': 12,  # bono.ccr.buffalo.edu, None
    'gordon': 16,  # gordon.sdsc.edu, None
    'ranger': 16,  # ranger.tacc.utexas.edu, 16
    'lonestar4': 12,  # lonestar.tacc.utexas.edu, 12
    'kraken': 12,  # kraken.nics.utk.edu, 12
    'blacklight': 16,  # blacklight.psc.edu, 8
    'forge': 16,  # forge.ncsa.illinois.edu, None
    'stampede': 16,  # stampede.tacc.utexas.edu, 16
    'SuperMIC': 20,  # SuperMIC, 20
    'comet': 24,  # comet.sdsc.edu, 24
    'rush1on12': 1,  # rush1on12, 1
    'rush6on12': 6,  # rush6on12, 6
    'rush1on12shared': 1,  # rush1on12shared, 1
    'rush6on12shared': 6,  # rush6on12shared, 6
    'edge12core_ifs': 12,  # edge12core_ifs, 12
    'stampede2-knl': 68,  # stampede2-knl, 68
    'bridges': 28,  # bridges, 28
    'huey': 8,  # huey, 8
    'huey_local': 8,  # huey_local, 8
    'UBHPC': 32,  # UBHPC, 32
    'stampede2-skx': 48,  # stampede2-skx, 48
    'jetstream-iu-xlarge': 8,  # jetstream-iu-xlarge, 8
    'Bridges-2': 128,  # Bridges-2, 128
    'Expanse': 128,  # Expanse, 128
    'anvil': 128,  # anvil, 128
}
