name = """xdmod.benchmark.osjitter"""
nickname = """xdmod.benchmark.osjitter.@ncpus@"""
uri = """file:///home/charngda/Inca-Reporter//xdmod.benchmark.osjitter"""
context = '''@batchpre@ -nodes=:@ppn@:@ncpus@ -walllimit=@walllimit@ -type=@batchFeature@ -exec="@@"'''
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
walllimit=10