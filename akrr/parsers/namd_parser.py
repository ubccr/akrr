import re
import os
import sys
from akrr.parsers.akrrappkeroutputparser import AppKerOutputParser


def process_appker_output(appstdout=None, stdout=None, stderr=None, geninfo=None, proclog=None, 
                          resource_appker_vars=None):
    # set App Kernel Description
    parser = AppKerOutputParser(
        name='namd',
        version=1,
        description="NAMD: Scalable Molecular Dynamics Package",
        url='http://www.ks.uiuc.edu/Research/namd/',
        measurement_name='NAMD'
    )
    # set obligatory parameters and statistics
    # set common parameters and statistics
    parser.add_common_must_have_params_and_stats()
    # set app kernel custom sets
    parser.add_must_have_parameter('App:Version')
    parser.add_must_have_parameter('Input:Coordinate File')
    parser.add_must_have_parameter('Input:Number of Angles')
    parser.add_must_have_parameter('Input:Number of Atoms')
    parser.add_must_have_parameter('Input:Number of Bonds')
    parser.add_must_have_parameter('Input:Number of Dihedrals')
    parser.add_must_have_parameter('Input:Number of Steps')
    parser.add_must_have_parameter('Input:Structure File')
    parser.add_must_have_parameter('Input:Timestep')

    parser.add_must_have_statistic('Memory')
    parser.add_must_have_statistic('Molecular Dynamics Simulation Performance')
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
    j = 0
    while j < len(lines):

        m = re.match(r'^Info: NAMD ([0-9a-zA-Z.]+)', lines[j])
        if m:
            parser.set_parameter("App:Version", m.group(1))

        m = re.match(r'^Info: TIMESTEP\s+([0-9.]+)', lines[j])
        if m:
            parser.set_parameter("Input:Timestep", m.group(1) + "e-15", "Second per Step")

        m = re.match(r'^Info: NUMBER OF STEPS\s+([0-9.]+)', lines[j])
        if m:
            parser.set_parameter("Input:Number of Steps", m.group(1))

        m = re.match(r'^Info: COORDINATE PDB\s+(.+)', lines[j])
        if m:
            parser.set_parameter("Input:Coordinate File", m.group(1))

        m = re.match(r'^Info: STRUCTURE FILE\s+(.+)', lines[j])
        if m:
            parser.set_parameter("Input:Structure File", m.group(1))

        m = re.match(r'^Info: Running on ([0-9.]+) processors, ([0-9.]+) nodes, ([0-9.]+) physical nodes.', lines[j])
        if m:
            parser.set_parameter("App:NCores", m.group(1).strip())
            parser.set_parameter("App:NNodes", m.group(3).strip())

        if re.match(r'^Info: STRUCTURE SUMMARY', lines[j]):
            j += 1
            for k in range(25):
                if re.match(r'^Info: \*\*\*\*\*', lines[j]):
                    break

                m = re.match(r'^Info:\s+([0-9]+)\s+ATOMS\n', lines[j])
                if m:
                    parser.set_parameter("Input:Number of Atoms", m.group(1))

                m = re.match(r'^Info:\s+([0-9]+)\s+BONDS\n', lines[j])
                if m:
                    parser.set_parameter("Input:Number of Bonds", m.group(1))

                m = re.match(r'^Info:\s+([0-9]+)\s+ANGLES\n', lines[j])
                if m:
                    parser.set_parameter("Input:Number of Angles", m.group(1))

                m = re.match(r'^Info:\s+([0-9]+)\s+DIHEDRALS\n', lines[j])
                if m:
                    parser.set_parameter("Input:Number of Dihedrals", m.group(1))

                j += 1

        if re.search(r'Info: Benchmark time:', lines[j]):
            m = re.search(r' ([0-9.]+) days/ns', lines[j])
            if m:
                parser.set_statistic("Molecular Dynamics Simulation Performance", str(1.0e-9 / float(m.group(1))),
                                     "Second per Day")

        m = re.match(r'^WallClock:\s+([0-9.]+)\s+CPUTime:\s+([0-9.]+)\s+Memory:\s+([0-9.]+)', lines[j])
        if m:
            parser.set_statistic("Wall Clock Time", m.group(1), "Second")
            parser.set_statistic("Memory", m.group(3), "MByte")
            successful_run = True

        m = re.match(r'^End of program', lines[j])
        if m:
            successful_run = True

        j += 1

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
    results_out = None if len(sys.argv)<=2 else sys.argv[2]
    print("Proccessing Output From", jobdir)
    result = process_appker_output(appstdout=os.path.join(jobdir, "appstdout"), geninfo=os.path.join(jobdir, "gen.info"))
    if results_out:
        with open(results_out, "wt") as fout:
            fout.write(str(result))
