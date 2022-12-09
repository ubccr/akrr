import re
import os
import sys

from akrr.parsers.akrrappkeroutputparser import AppKerOutputParser


def process_appker_output(appstdout=None, stdout=None, stderr=None, geninfo=None, proclog=None, 
                          resource_appker_vars=None):
    # set App Kernel Description
    parser = AppKerOutputParser(
        name='gromacs_micro',
        version=1,
        description="GROMACS: micro-benchmark for testing purposes",
        url='http://www.gromacs.org/',
        measurement_name='GROMACS-Micro'
    )
    # set obligatory parameters and statistics
    # set common parameters and statistics
    parser.add_common_must_have_params_and_stats()
    # set app kernel custom sets
    parser.add_must_have_parameter('App:Version')

    parser.add_must_have_statistic('Simulation Speed')
    parser.add_must_have_statistic('Wall Clock Time')

    # parse common parameters and statistics
    parser.parse_common_params_and_stats(appstdout, stdout, stderr, geninfo, resource_appker_vars)

    # read output
    lines = []
    if os.path.isfile(appstdout):
        fin = open(appstdout, "rt")
        lines = fin.readlines()
        fin.close()

    # process the output
    successful_run = False
    gflops = None
    wall_clock = None
    j = 0
    while j < len(lines):
        m = re.search(r'^GROMACS:\s+ gmx mdrun, version\s+(\S+)$', lines[j])
        if m:
            parser.set_parameter("App:Version", m.group(1))

        m = re.search(r'gmx_mpi mdrun -v -nsteps ([0-9]+)$', lines[j])
        if m:
            parser.set_parameter("Input:nsteps", m.group(1))
        m = re.search(r'gmx_mpi mdrun -nsteps ([0-9]+)$', lines[j])
        if m:
            parser.set_parameter("Input:nsteps", m.group(1))

        m = re.search(r'^Performance: \s+([0-9.]+)', lines[j])
        if m:
            parser.set_statistic("Simulation Speed", float(m.group(1)), "ns/day")

        m = re.search(r'^ \s+Time: \s+([0-9.]+) \s+([0-9.]+)', lines[j])
        if m:
            wall_clock = float(m.group(2))
            parser.set_statistic("Wall Clock Time", m.group(2), "Second")
            parser.set_statistic("Core Clock Time", m.group(1), "Second")

        m = re.match(r'^GROMACS reminds you', lines[j])
        if m:
            successful_run = True

        m = re.search(r'M E G A - F L O P S   A C C O U N T I N G', lines[j])
        if m:
            while j < len(lines):
                m = re.search(r'Total\s+([0-9.]+)', lines[j])
                if m:
                    gflops = (float(m.group(1))/1000)
                    break
                j += 1
        m = re.search(r'R E A L   C Y C L E   A N D   T I M E   A C C O U N T I N G', lines[j])
        if m:
            while j < len(lines):
                m = re.search(r'Force\s+[0-9.]+\s+[0-9.]+\s+[0-9.]+\s+[0-9.]+\s+[0-9.]+\s+([0-9.]+)', lines[j])
                if m:
                    parser.set_statistic("Force Calculation Percentage", m.group(1), "%")
                m = re.search(r'PME mesh\s+[0-9.]+\s+[0-9.]+\s+[0-9.]+\s+[0-9.]+\s+[0-9.]+\s+([0-9.]+)', lines[j])
                if m:
                    parser.set_statistic("PME Mesh Calculation Percentage", m.group(1), "%")
                    break
                j += 1
        j += 1

    if gflops is not None and wall_clock is not None:
        parser.set_statistic("Total GFLOP/S", gflops/wall_clock, "GFLOP/S")

    parser.successfulRun = successful_run

    if __name__ == "__main__":
        # output for testing purpose
        print("parsing complete:", parser.parsing_complete())
        parser.print_params_stats_as_must_have()
        print(parser.get_xml())

    # return complete XML overwize return None
    return parser.get_xml()


if __name__ == "__main__":
    """stand alone testing"""
    jobdir = sys.argv[1]
    print("Proccessing Output From", jobdir)
    process_appker_output(appstdout=os.path.join(jobdir, "appstdout"), geninfo=os.path.join(jobdir, "gen.info"))
