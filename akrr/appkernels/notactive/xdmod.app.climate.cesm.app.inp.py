name = """xdmod.app.climate.cesm"""
nickname = """xdmod.app.climate.cesm.@ncpus@"""
uri = """file:///home/charngda/Inca-Reporter//xdmod.app.climate.cesm"""
context = '''@batchpre@ -nodes=:@ppnBigMem@:@ncpus@ -type=@batchFeature@ -walllimit=@walllimit@ -exec="@@"'''
resourceSetName = """defaultGrid"""
action = """add"""
schedule = [
    """? ? */10 * *""",
]
arg_version = """no"""
arg_verbose = 1
arg_help = """no"""
arg_bin_path = """@bin_path@"""
arg_log = 5
walllimit=30