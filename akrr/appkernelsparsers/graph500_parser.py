import re
import os
import sys
from akrr.appkernelsparsers.akrrappkeroutputparser import AppKerOutputParser, total_seconds


# graph500/run input$numCores
def process_appker_output(appstdout=None, stdout=None, stderr=None, geninfo=None, resource_appker_vars=None):
    # set App Kernel Description
    parser = AppKerOutputParser(
        name='xdmod.benchmark.graph.graph500',
        version=1,
        description="Graph500 Benchmark",
        url='http://www.Graph500.org',
        measurement_name='Graph500'
    )
    # set obligatory parameters and statistics
    # set common parameters and statistics
    parser.add_common_must_have_params_and_stats()
    # set app kernel custom sets
    parser.add_must_have_parameter('App:Version')
    parser.add_must_have_parameter('Edge Factor')
    parser.add_must_have_parameter('Input File')
    parser.add_must_have_parameter('Number of Roots to Check')
    parser.add_must_have_parameter('Number of Edges')
    parser.add_must_have_parameter('Number of Vertices')
    parser.add_must_have_parameter('Scale')

    parser.add_must_have_statistic('Harmonic Mean TEPS')
    parser.add_must_have_statistic('Harmonic Standard Deviation TEPS')
    parser.add_must_have_statistic('Median TEPS')
    parser.add_must_have_statistic('Wall Clock Time')

    # parse common parameters and statistics
    parser.parse_common_params_and_stats(appstdout, stdout, stderr, geninfo, resource_appker_vars)

    if parser.appKerWallClockTime is not None:
        parser.set_statistic("Wall Clock Time", total_seconds(parser.appKerWallClockTime), "Second")
    elif parser.wallClockTime is not None:
        parser.set_statistic("Wall Clock Time", total_seconds(parser.wallClockTime), "Second")

    # read output
    lines = []
    if os.path.isfile(appstdout):
        fin = open(appstdout, "rt")
        lines = fin.readlines()
        fin.close()

    # process the output
    parser.successfulRun = True
    num_of_errors = 0
    j = 0
    while j < len(lines):
        m = re.match(r'^Graph500 version:\s+(.+)', lines[j])
        if m:
            parser.set_parameter("App:Version", m.group(1).strip())

        m = re.match(r'ERROR:\s+(.+)', lines[j])
        if m:
            num_of_errors += 1

        m = re.match(r'^Reading input from\s+(.+)', lines[j])
        if m:
            parser.set_parameter("Input File", m.group(1))

        m = re.match(r'^SCALE:\s+(\d+)', lines[j])
        if m:
            parser.set_parameter("Scale", m.group(1))

        m = re.match(r'^edgefactor:\s+(\d+)', lines[j])
        if m:
            parser.set_parameter("Edge Factor", m.group(1))

        m = re.match(r'^NBFS:\s+(\d+)', lines[j])
        if m:
            parser.set_parameter("Number of Roots to Check", m.group(1))

        m = re.match(r'^median_TEPS:\s+(\d[0-9.e+]+)', lines[j])
        if m:
            parser.set_statistic("Median TEPS", m.group(1), "Traversed Edges Per Second")

        m = re.match(r'^harmonic_mean_TEPS:\s+(\d[0-9.e+]+)', lines[j])
        if m:
            parser.successfulRun = True
            parser.set_statistic("Harmonic Mean TEPS", m.group(1), "Traversed Edges Per Second")

        m = re.match(r'^harmonic_stddev_TEPS:\s+(\d[0-9.e+]+)', lines[j])
        if m:
            parser.set_statistic("Harmonic Standard Deviation TEPS", m.group(1), "Traversed Edges Per Second")

        m = re.match(r'^median_validate:\s+([\d.]+)\s+s', lines[j])
        if m:
            parser.set_statistic("Median Validation Time", m.group(1), "Second")

        m = re.match(r'^mean_validate:\s+([\d.]+)\s+s', lines[j])
        if m:
            parser.set_statistic("Mean Validation Time", m.group(1), "Second")

        m = re.match(r'^stddev_validate:\s+([\d.]+)\s+s', lines[j])
        if m:
            parser.set_statistic("Standard Deviation Validation Time", m.group(1), "Second")

        j += 1

    if num_of_errors > 0:
        parser.successfulRun = False

    if parser.get_parameter('Scale') is not None and parser.get_parameter('Edge Factor') is not None:
        scale = int(parser.get_parameter('Scale'))
        edgefactor = int(parser.get_parameter('Edge Factor'))
        parser.set_parameter("Number of Vertices", 2 ** scale)
        parser.set_parameter("Number of Edges", edgefactor * 2 ** scale)

    if __name__ == "__main__":
        # output for testing purpose
        parser.parsing_complete(True)
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
