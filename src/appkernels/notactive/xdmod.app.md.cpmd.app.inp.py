name = """xdmod.app.md.cpmd"""
nickname = """xdmod.app.md.cpmd.@ncpus@"""
uri = """file:///home/charngda/Inca-Reporter//xdmod.app.md.cpmd"""
context = '''@batchpre@ -nodes=:@ppn@:@ncpus@ -type=@batchFeature@ -walllimit=@walllimit@ -exec="@@"'''
resourceSetName = """defaultGrid"""
action = """add"""
schedule = [
    """? ? */14 * *""",
]
arg_version = """no"""
arg_verbose = 1
arg_help = """no"""
arg_bin_path = """@bin_path@"""
arg_log = 5
walllimit=20

parser="xdmod.app.md.cpmd.py"
#path to run script relative to AppKerDir on particular resource
runScriptPath="cpmd/run"
runScriptArgs="input01"