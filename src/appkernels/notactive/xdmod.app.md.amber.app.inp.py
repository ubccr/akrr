name = """xdmod.app.md.amber"""
nickname = """xdmod.app.md.amber.@ncpus@"""
uri = """file:///home/charngda/Inca-Reporter//xdmod.app.md.amber"""
context = '''@batchpre@ -nodes=:@ppn@:@ncpus@ -type=@batchFeature@ -walllimit=@walllimit@ -exec="@@"'''
resourceSetName = """defaultGrid"""
action = """add"""
schedule = [
    """? ? 0-31/13 * *""",
]
arg_version = """no"""
arg_verbose = 1
arg_help = """no"""
arg_bin_path = """@bin_path@"""
arg_log = 5
walllimit=12

parser="xdmod.app.md.amber.py"
#path to run script relative to AppKerDir on particular resource
runScriptPath="amber/run"
runScriptArgs="input01"
