# Generic Parser
import re
import os
import sys
from akrr.appkernelsparsers.akrrappkeroutputparser import AppKerOutputParser


def process_appker_output(appstdout=None, stdout=None, stderr=None, geninfo=None, resource_appker_vars=None):
    # set App Kernel Description
    if resource_appker_vars is not None and 'app' in resource_appker_vars and 'name' in resource_appker_vars['app']:
        akname = resource_appker_vars['app']['name']
    else:
        akname = 'unknown'

    # initiate parser
    parser = AppKerOutputParser(
        name=akname
    )
    # set obligatory parameters and statistics
    # set common parameters and statistics (App:ExeBinSignature and RunEnv:Nodes)
    parser.add_common_must_have_params_and_stats()
    # set app kernel custom sets
    parser.add_must_have_parameter('App:ExeBinSignature')
    parser.add_must_have_parameter('App:Version')
    parser.add_must_have_parameter('Number of Darts Throws')
    parser.add_must_have_parameter('Number of Rounds')
    parser.add_must_have_parameter('RunEnv:Nodes')

    parser.add_must_have_statistic('Darts Throws per Second')
    parser.add_must_have_statistic('Time for PI Calculation')
    parser.add_must_have_statistic('Wall Clock Time')

    # parse common parameters and statistics
    parser.parse_common_params_and_stats(appstdout, stdout, stderr, geninfo)

    if hasattr(parser, 'appKerWallClockTime'):
        parser.set_statistic("Wall Clock Time", parser.appKerWallClockTime.total_seconds(), "Second")

    # Here can be custom output parsing
    # read output
    lines = []
    if os.path.isfile(appstdout):
        fin = open(appstdout, "rt")
        lines = fin.readlines()
        fin.close()

    # process the output
    parser.successfulRun = False
    j = 0
    while j < len(lines):
        m = re.search(r'version:\s+(.+)', lines[j])
        if m:
            parser.set_parameter('App:Version', m.group(1))

        m = re.search(r'number of throws at dartboard:\s+(\d+)', lines[j])
        if m:
            parser.set_parameter('Number of Darts Throws', m.group(1))

        m = re.search(r'number of rounds for dartz throwing\s+(\d+)', lines[j])
        if m:
            parser.set_parameter('Number of Rounds', m.group(1))

        m = re.search(r'Time for PI calculation:\s+([0-9.]+)', lines[j])
        if m:
            parser.set_statistic("Time for PI Calculation", m.group(1), "Seconds")

        m = re.search(r'Giga Darts Throws per Second \(GDaPS\):\s+([0-9.]+)', lines[j])
        if m:
            parser.set_statistic("Darts Throws per Second", m.group(1), "GDaPS")

        m = re.search(r'Giga Darts Throws per Second', lines[j])
        if m:
            parser.successfulRun = True

        j += 1

    if __name__ == "__main__":
        # output for testing purpose
        print(("Parsing complete:", parser.parsing_complete(verbose=True)))
        print("Following statistics and parameter can be set as obligatory:")
        parser.print_params_stats_as_must_have()
        print("\nResulting XML:")
        print((parser.get_xml()))

    # return complete XML otherwise return None
    return parser.get_xml()


if __name__ == "__main__":
    """stand alone testing"""
    jobdir = sys.argv[1]
    print("Proccessing Output From", jobdir)
    process_appker_output(appstdout=os.path.join(jobdir, "appstdout"), geninfo=os.path.join(jobdir, "gen.info"))
