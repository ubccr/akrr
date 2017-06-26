name = """xdmod.app.md.lammps"""
nickname = """xdmod.app.md.lammps.@ncpus@"""
uri = """file:///home/charngda/Inca-Reporter//xdmod.app.md.lammps"""
context = '''@batchpre@ -nodes=:@ppn@:@ncpus@ -type=@batchFeature@ -walllimit=@walllimit@ -exec="@@"'''
resourceSetName = """defaultGrid"""
action = """add"""
schedule = [
    """? ? */13 * *""",
]
arg_version = """no"""
arg_verbose = 1
arg_help = """no"""
arg_bin_path = """@bin_path@"""
arg_log = 5
walllimit=14 

parser="xdmod.app.md.lammps.py"
#path to run script relative to AppKerDir on particular resource
runScriptPath="lammps/run"
runScriptArgs="input01"