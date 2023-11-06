import re
import os
import sys
from akrr.parsers.akrrappkeroutputparser import AppKerOutputParser, total_seconds


def process_appker_output(appstdout=None, stdout=None, stderr=None, geninfo=None, proclog=None,
                          resource_appker_vars=None):
    # set App Kernel Description
    parser = AppKerOutputParser(
        name='openfoam',
        version=1,
        description="OpenFOAM",
        url='https://www.openfoam.com/',
        measurement_name='openfoam'
    )
    # set obligatory parameters and statistics
    # set common parameters and statistics
    parser.add_common_must_have_params_and_stats()
    # set app kernel custom sets
    parser.add_must_have_parameter('App:ExeBinSignature')
    parser.add_must_have_parameter('App:Version')
    parser.add_must_have_parameter('Input')
    parser.add_must_have_parameter('Mesh stats: cells')
    parser.add_must_have_parameter('Mesh stats: faces')
    parser.add_must_have_parameter('Mesh stats: points')
    parser.add_must_have_parameter('RunEnv:Nodes')

    parser.add_must_have_statistic('Snappy run-time')
    parser.add_must_have_statistic('Solver run-time')
    parser.add_must_have_statistic('Wall Clock Time')

    # parse common parameters and statistics
    parser.parse_common_params_and_stats(appstdout, stdout, stderr, geninfo, resource_appker_vars)

    if parser.appKerWallClockTime is not None:
        parser.set_statistic("Wall Clock Time", total_seconds(parser.appKerWallClockTime), "Second")

    if "input_param" in parser.geninfo:
        input_param = parser.geninfo['input_param']
        if re.match("inputs/openfoam/", input_param):
            input_param = input_param.replace("inputs/openfoam/", "", 1)
            parser.set_parameter("Input", input_param.strip())

    # read output
    lines = []
    if os.path.isfile(appstdout):
        fin = open(appstdout, "rt")
        lines = fin.readlines()
        fin.close()



    # process the output
    time_more_than_zero = False
    reach_end_allrun = 0
    j = 0

    while j < len(lines):
        # Global parameters
        parser.match_set_parameter("App:Version", r'Build\s+:\s+(.+)$', lines[j])
        m = re.match(r'^Mesh stats', lines[j])
        if m:
            j += 1
            while j < len(lines) and lines[j].strip() != "":
                parser.match_set_parameter("Mesh stats: points", r'\s*points:\s*(\d+)$', lines[j])
                parser.match_set_parameter("Mesh stats: faces", r'\s*faces:\s*(\d+)$', lines[j])
                parser.match_set_parameter("Mesh stats: cells", r'\s*cells:\s*(\d+)$', lines[j])
                j += 1

        # Summary statistics
        parser.match_set_statistic("Snappy run-time", r'Snappy run-time: ([0-9.]+)$', lines[j], units="Seconds")
        parser.match_set_statistic("Solver run-time", r'Solver run-time: ([0-9.]+)$', lines[j], units="Seconds")
        parser.match_set_statistic("Wall Clock Time", r'Total run-time: ([0-9.]+)$', lines[j], units="Second")

        # This for determining is it a good run

        m = re.match(r'^# log.simpleFoam #', lines[j])
        if m:
            j += 1
            while j < len(lines):
                m = re.match(r'^Time = (\d+)', lines[j])
                if m and int(m.group(1)) > 0:
                    time_more_than_zero = True
                if lines[j].strip()=="Finalising parallel run" or \
                        lines[j].strip()=="End Allrun":
                    reach_end_allrun += 1
                j += 1
        j += 1

    parser.successfulRun = (reach_end_allrun == 2) and time_more_than_zero

    # return
    if __name__ == "__main__":
        # output for testing purpose
        print("parsing complete:", parser.parsing_complete())
        parser.print_params_stats_as_must_have()
        print("XML:")
        print(parser.get_xml())
        print("json:")
        print(parser.get_json())

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
