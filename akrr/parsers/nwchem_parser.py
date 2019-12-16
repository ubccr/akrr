import re
import os
import sys
from akrr.parsers.akrrappkeroutputparser import AppKerOutputParser


def process_appker_output(appstdout=None, stdout=None, stderr=None, geninfo=None, proclog=None, 
                          resource_appker_vars=None):
    # set App Kernel Description
    parser = AppKerOutputParser(
        name='nwchem',
        version=1,
        description="NWChem: Northwest Computational Chemistry Package",
        url='http://www.emsl.pnl.gov/docs/nwchem',
        measurement_name='NWChem'
    )
    # set obligatory parameters and statistics
    # set common parameters and statistics
    parser.add_common_must_have_params_and_stats()
    # set app kernel custom sets
    parser.add_must_have_parameter('App:Version')
    parser.add_must_have_parameter('App:Branch')
    parser.add_must_have_parameter('Input:File')

    parser.add_must_have_statistic('Wall Clock Time')
    parser.add_must_have_statistic('User Time')
    parser.add_must_have_statistic("Global Arrays 'Create' Calls")
    parser.add_must_have_statistic("Global Arrays 'Destroy' Calls")
    parser.add_must_have_statistic("Global Arrays 'Get' Calls")
    parser.add_must_have_statistic("Global Arrays 'Put' Calls")
    parser.add_must_have_statistic("Global Arrays 'Accumulate' Calls")
    parser.add_must_have_statistic("Global Arrays 'Get' Amount")
    parser.add_must_have_statistic("Global Arrays 'Put' Amount")
    parser.add_must_have_statistic("Global Arrays 'Accumulate' Amount")
    # parse common parameters and statistics
    parser.parse_common_params_and_stats(appstdout, stdout, stderr, geninfo, resource_appker_vars)

    # read output
    lines = []
    if os.path.isfile(appstdout):
        fin = open(appstdout, "rt")
        lines = fin.readlines()
        fin.close()

    # process the output
    j = 0
    while j < len(lines):

        m = re.search(r'Northwest Computational Chemistry Package \(NWChem\) (.+)', lines[j])
        if m:
            parser.set_parameter("App:Version", m.group(1).strip())

        m = re.search(r'nwchem branch *=(.+)', lines[j])
        if m:
            parser.set_parameter("App:Branch", m.group(1).strip())

        m = re.search(r'input\s+= (.+)', lines[j])
        if m:
            parser.set_parameter("Input:File", m.group(1).strip())

        m = re.search(r'Total times\s+cpu:\s+([0-9.]+)s\s+wall:\s+([0-9.]+)s', lines[j])
        if m:
            parser.set_statistic("Wall Clock Time", m.group(2).strip(), "Second")
            parser.set_statistic("User Time", m.group(1).strip(), "Second")

        #                          GA Statistics for process    0
        #                          ------------------------------
        #
        #        create   destroy   get      put      acc     scatter   gather  read&inc
        # calls:  521      521     6.28e+05 6.45e+04 6.78e+05    0        0        0
        # number of processes/call 1.05e+00 1.36e+00 1.03e+00 0.00e+00 0.00e+00
        # bytes total:             7.33e+09 4.35e+08 1.53e+09 0.00e+00 0.00e+00 0.00e+00
        # bytes remote:            5.74e+09 1.31e+08 1.09e+09 0.00e+00 0.00e+00 0.00e+00
        # Max memory consumed for GA by this process: 47428032 bytes
        if re.search(r'GA Statistics for process', lines[j]):
            if re.match(r'^calls', lines[j + 4]):
                v = lines[j + 4].strip().split()
                parser.set_statistic("Global Arrays 'Create' Calls", "%.0f" % float(v[1]), "Number of Calls")
                parser.set_statistic("Global Arrays 'Destroy' Calls", "%.0f" % float(v[2]), "Number of Calls")
                parser.set_statistic("Global Arrays 'Get' Calls", "%.0f" % float(v[3]), "Number of Calls")
                parser.set_statistic("Global Arrays 'Put' Calls", "%.0f" % float(v[4]), "Number of Calls")
                parser.set_statistic("Global Arrays 'Accumulate' Calls", "%.0f" % float(v[5]), "Number of Calls")

                v = lines[j + 6].strip().split()
                parser.set_statistic("Global Arrays 'Get' Amount", (float(v[2])) / 1048576.0, "MByte")
                parser.set_statistic("Global Arrays 'Put' Amount", (float(v[3])) / 1048576.0, "MByte")
                parser.set_statistic("Global Arrays 'Accumulate' Amount", (float(v[4])) / 1048576.0, "MByte")

        # NWChem can be optionally compiled with PAPI, and it will
        # report some GLOPS at the end
        # thus here it is optional 
        m = re.search(r'Aggregate GFLOPS \(Real_time\):\s+([0-9.]+)', lines[j])
        if m:
            parser.set_statistic("Floating-Point Performance (Wall Clock Time)", 1000.0 * float(m.group(1).strip()),
                                 "MFLOP per Second")

        m = re.search(r'Aggregate GFLOPS \(Proc_time\):\s+([0-9.]+)', lines[j])
        if m:
            parser.set_statistic("Floating-Point Performance (User Time)", 1000.0 * float(m.group(1).strip()),
                                 "MFLOP per Second")
        j += 1

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
