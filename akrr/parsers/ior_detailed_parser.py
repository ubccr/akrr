"""
Parser for Intel MPI Benchmarks output
"""
import re
import os
import sys
from akrr.parsers.akrrappkeroutputparser import AppKerOutputParser, total_seconds
from akrr.util import log


def get_MiB(val, units):
    """
    Calculate MiB from KiB or GiB
    """
    if units == "MiB":
        return val
    if units == "KiB":
        return val / 1024.0
    if units == "GiB":
        return val * 1024


def process_ior_output_v33(parser, lines):
    """
    IOR output processing for version 3.3
    """
    total_number_of_tests = 0
    tests_passed = 0
    i = 0
    input_summary = {}
    filesystem = None
    while i < len(lines) - 1:
        m = re.match(r'^IOR-([3-9]\.[0-9]+\.[0-9]+\S*): MPI Coordinated Test of Parallel I/O', lines[i])
        if m:
            parser.set_parameter("App:Version", m.group(1).strip())

        m = re.match(r'^File System To Test:(.+)', lines[i])
        if m:
            filesystem = m.group(1).strip()

        m = re.match(r'^# Starting Test:', lines[i])
        if m:
            total_number_of_tests += 1

        summary_header = re.match(r'^Summary:$', lines[i].strip()) is not None
        options_header = re.match(r'^Options:$', lines[i].strip()) is not None
        if summary_header or options_header:
            # input summary section
            input_summary = {}
            i += 1
            while i < len(lines):
                if summary_header:
                    m1 = re.match(r'^\t([^=\n\r\f\v]+)=(.+)', lines[i])
                else:
                    m1 = re.match(r'^([^=\n\r\f\v]+):(.+)', lines[i])
                if m1:
                    input_summary[m1.group(1).strip()] = m1.group(2).strip()
                else:
                    break
                i += 1
            # process input_summary
            input_summary['filesystem'] = filesystem
            input_summary['API'] = input_summary['api']
            if input_summary['api'].count("MPIIO") > 0:
                input_summary['API'] = "MPIIO"
                if "apiVersion" in input_summary:
                    input_summary['API_Version'] = input_summary['apiVersion']
                else:
                    input_summary['API_Version'] = input_summary['api'].replace("MPIIO", "").strip()
                parser.set_parameter("MPIIO Version", input_summary['API_Version'])
            if input_summary['api'].count("HDF5") > 0:
                input_summary['API'] = "HDF5"
                if "apiVersion" in input_summary:
                    input_summary['API_Version'] = input_summary['apiVersion']
                else:
                    input_summary['API_Version'] = input_summary['api'].replace("HDF5-", "").replace("HDF5", "").strip()
                parser.set_parameter("HDF Version", input_summary['API_Version'])
            if input_summary['api'].count("NCMPI") > 0:
                input_summary['API'] = "Parallel NetCDF"
                if "apiVersion" in input_summary:
                    input_summary['API_Version'] = input_summary['apiVersion']
                else:
                    input_summary['API_Version'] = input_summary['api'].replace("NCMPI", "").strip()
                parser.set_parameter("Parallel NetCDF Version", input_summary['API_Version'])
            if "nodes" in input_summary and parser.get_parameter("Nodes") is None:
                parser.set_parameter("Nodes", input_summary['nodes'])
            if "tasks" in input_summary and parser.get_parameter("Tasks") is None:
                parser.set_parameter("Tasks", input_summary['tasks'])




            # fileAccessPattern
            input_summary['fileAccessPattern'] = ""
            input_summary['collectiveOrIndependent'] = ""
            if input_summary['access'].count('single-shared-file') > 0:
                input_summary['fileAccessPattern'] = "N-to-1"
            elif input_summary['access'].count('file-per-process') > 0:
                input_summary['fileAccessPattern'] = "N-to-N"
            else:
                log.error("Cannot determine fileAccessPattern")

            # collectiveOrIndependent
            input_summary['collectiveOrIndependent'] = ""
            if "type" in input_summary:
                if input_summary['type'].count('independent') > 0:
                    input_summary['collectiveOrIndependent'] = "Independent"
                elif input_summary['type'].count('collective') > 0:
                    input_summary['collectiveOrIndependent'] = "Collective"
            else:
                if input_summary['access'].count('independent') > 0:
                    input_summary['collectiveOrIndependent'] = "Independent"
                elif input_summary['access'].count('collective') > 0:
                    input_summary['collectiveOrIndependent'] = "Collective"
            if input_summary['collectiveOrIndependent'] == "":
                log.error("Cannot determine collectiveOrIndependent")

            # N-to-N always Independent
            if input_summary['fileAccessPattern'] == "N-to-N" and \
                    input_summary['collectiveOrIndependent'] == "Independent":
                input_summary['collectiveOrIndependent'] = ""
            # POSIX always Independent
            if input_summary['API'] == "POSIX":
                input_summary['collectiveOrIndependent'] = ""

            if input_summary['collectiveOrIndependent'] != "":
                input_summary['method'] = "/".join((input_summary['API'],
                                                    input_summary['collectiveOrIndependent'],
                                                    input_summary['fileAccessPattern']))
            else:
                input_summary['method'] = "//".join((input_summary['API'],
                                                    input_summary['fileAccessPattern']))

            if input_summary['filesystem'] is not None:
                parser.set_parameter(input_summary['method'] + ' Test File System', input_summary['filesystem'])

            if "pattern" in input_summary:
                m1 = re.match(r'^segmented \(([0-9]+) segment', input_summary["pattern"])
                if m1:
                    input_summary["segmentCount"] = int(m1.group(1).strip())
            if "segments" in input_summary:
                input_summary["segmentCount"] = int(input_summary["segments"])

            if "blocksize" in input_summary and "segmentCount" in input_summary:
                val, unit = input_summary["blocksize"].split()
                block_size = get_MiB(float(val), unit)
                segment_count = input_summary["segmentCount"]
                parser.set_parameter("Per-Process Data Size", block_size * segment_count, "MByte")
                parser.set_parameter("Per-Process I/O Block Size", block_size, "MByte")

            if "xfersize" in input_summary:
                val, unit = input_summary["xfersize"].split()
                transfer_size = get_MiB(float(val), unit)
                parser.set_parameter("Transfer Size Per I/O", transfer_size, "MByte")

        m0 = re.match(
            r'^access\s+bw\(MiB/s\)\s+IOPS\s+Latency\(s\)\s+block\(KiB\)\s+xfer\(KiB\)\s+'
            r'open\(s\)\s+wr/rd\(s\)\s+close\(s\)\s+total\(s\)\s+iter',
            lines[i])
        if m0:
            i += 1
            while i < len(lines):
                m1 = re.match(
                    r'^write\s+([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)\s+'
                    r'([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)',
                    lines[i])
                m2 = re.match(
                    r'^read\s+([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)\s+'
                    r'([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)',
                    lines[i])
                if m1 or m2:
                    if m1:
                        access = "Write"
                        bw, iops, latency, block, xfer, open_s, wrrd_s, close_s, total_s, iter_s = m1.groups()
                    else:
                        access = "Read"
                        bw, iops, latency, block, xfer, open_s, wrrd_s, close_s, total_s, iter_s = m2.groups()
                        tests_passed += 1
                        parser.successfulRun = True

                    parser.set_statistic(input_summary['method'] + "/%s/Aggregate Throughput" % access, bw,
                                         "MByte per Second")
                    parser.set_statistic(input_summary['method'] + "/%s/File Open Time" % access, open_s,
                                         "Second")
                    parser.set_statistic(input_summary['method'] + "/%s/File Close Time" % access, close_s,
                                         "Second")
                    parser.set_statistic(input_summary['method'] + "/%s/IOPS" % access, iops,
                                         "IOPS")

                m1 = re.match(r'^Summary of all tests:', lines[i])
                if m1:
                    break
                i += 1
            # reset variables
            input_summary = {}
            # filesystem=None
        i += 1
    return total_number_of_tests, tests_passed


def process_appker_output(appstdout=None, stdout=None, stderr=None, geninfo=None, proclog=None, 
                          resource_appker_vars=None):
    # set App Kernel Description
    parser = AppKerOutputParser(
        name='ior',
        version=1,
        description="IOR (Interleaved-Or-Random) Benchmark",
        url='http://freshmeat.net/projects/ior',
        measurement_name='IOR'
    )
    app_vars = None
    if resource_appker_vars is not None and 'app' in resource_appker_vars:
        app_vars = resource_appker_vars['app']

    # set obligatory parameters and statistics
    # set common parameters and statistics
    parser.add_common_must_have_params_and_stats()
    # set app kernel custom sets
    parser.add_must_have_parameter('App:Version')
    if app_vars is None or (
            app_vars is not None and 'testHDF5' in app_vars and
            app_vars['testHDF5'] is True):
        parser.add_must_have_parameter('HDF Version')
        parser.add_must_have_parameter('HDF5 Collective N-to-1 Test File System')
        parser.add_must_have_parameter('HDF5 Independent N-to-1 Test File System')
        parser.add_must_have_parameter('HDF5 N-to-N Test File System')

    if app_vars is None or (
            app_vars is not None and 'testMPIIO' in app_vars and
            app_vars['testMPIIO'] is True):
        parser.add_must_have_parameter('MPIIO Collective N-to-1 Test File System')
        parser.add_must_have_parameter('MPIIO Independent N-to-1 Test File System')
        parser.add_must_have_parameter('MPIIO N-to-N Test File System')

    if app_vars is None or (
            app_vars is not None and 'testPOSIX' in app_vars and
            app_vars['testPOSIX'] is True):
        parser.add_must_have_parameter('POSIX N-to-1 Test File System')
        parser.add_must_have_parameter('POSIX N-to-N Test File System')

    if app_vars is None or (
            app_vars is not None and 'testNetCDF' in app_vars and
            app_vars['testNetCDF'] is True):
        parser.add_must_have_parameter('Parallel NetCDF Collective N-to-1 Test File System')
        parser.add_must_have_parameter('Parallel NetCDF Independent N-to-1 Test File System')
        parser.add_must_have_parameter('Parallel NetCDF Version')
        parser.add_must_have_parameter('Per-Process Data Size')
        parser.add_must_have_parameter('Per-Process I/O Block Size')
        parser.add_must_have_parameter('RunEnv:Nodes')
        parser.add_must_have_parameter('Transfer Size Per I/O')

    if app_vars is None or (
            app_vars is not None and 'testHDF5' in app_vars and
            app_vars['testHDF5'] is True):
        parser.add_must_have_statistic('HDF5 Collective N-to-1 Read Aggregate Throughput')
        parser.add_must_have_statistic('HDF5 Collective N-to-1 Write Aggregate Throughput')
        parser.add_must_have_statistic('HDF5 Independent N-to-1 Read Aggregate Throughput')
        parser.add_must_have_statistic('HDF5 Independent N-to-1 Write Aggregate Throughput')
        parser.add_must_have_statistic('HDF5 N-to-N Read Aggregate Throughput')
        parser.add_must_have_statistic('HDF5 N-to-N Write Aggregate Throughput')

    if app_vars is None or (
            app_vars is not None and 'testMPIIO' in app_vars and
            app_vars['testMPIIO'] is True):
        parser.add_must_have_statistic('MPIIO Collective N-to-1 Read Aggregate Throughput')
        parser.add_must_have_statistic('MPIIO Collective N-to-1 Write Aggregate Throughput')
        parser.add_must_have_statistic('MPIIO Independent N-to-1 Read Aggregate Throughput')
        parser.add_must_have_statistic('MPIIO Independent N-to-1 Write Aggregate Throughput')
        parser.add_must_have_statistic('MPIIO N-to-N Read Aggregate Throughput')
        parser.add_must_have_statistic('MPIIO N-to-N Write Aggregate Throughput')

    if app_vars is None or (
            app_vars is not None and 'testPOSIX' in app_vars and
            app_vars['testPOSIX'] is True):
        parser.add_must_have_statistic('POSIX N-to-1 Read Aggregate Throughput')
        parser.add_must_have_statistic('POSIX N-to-1 Write Aggregate Throughput')
        parser.add_must_have_statistic('POSIX N-to-N Read Aggregate Throughput')
        parser.add_must_have_statistic('POSIX N-to-N Write Aggregate Throughput')

    if app_vars is None or (
            app_vars is not None and 'testNetCDF' in app_vars and
            app_vars['testNetCDF'] is True):
        parser.add_must_have_statistic('Parallel NetCDF Collective N-to-1 Read Aggregate Throughput')
        parser.add_must_have_statistic('Parallel NetCDF Collective N-to-1 Write Aggregate Throughput')
        parser.add_must_have_statistic('Parallel NetCDF Independent N-to-1 Read Aggregate Throughput')
        parser.add_must_have_statistic('Parallel NetCDF Independent N-to-1 Write Aggregate Throughput')

    parser.add_must_have_statistic('Number of Tests Passed')
    parser.add_must_have_statistic('Number of Tests Started')

    parser.add_must_have_statistic('Wall Clock Time')

    parser.completeOnPartialMustHaveStatistics = True
    # parse common parameters and statistics
    parser.parse_common_params_and_stats(appstdout, stdout, stderr, geninfo, resource_appker_vars)

    if hasattr(parser, 'appKerWallClockTime'):
        parser.set_statistic("Wall Clock Time", total_seconds(parser.appKerWallClockTime), "Second")

    # read output
    lines = []
    if os.path.isfile(appstdout):
        fin = open(appstdout, "rt")
        lines = fin.readlines()
        fin.close()

    # process the output

    # find which version of IOR was used
    ior_output_version = None
    j = 0
    while j < len(lines) - 1:
        # IOR RELEASE: IOR-2.10.3
        m = re.match(r'^#\s+IOR RELEASE:\s(.+)', lines[j])
        if m:
            ior_output_version = 20
        # IOR-3.2.0: MPI Coordinated Test of Parallel I/O
        # IOR-3.3.0+dev: MPI Coordinated Test of Parallel I/O
        m = re.match(r'^IOR-([3-9])\.([0-9])+\.[0-9]\S*: MPI Coordinated Test of Parallel I/O', lines[j])
        if m:
            ior_major = int(m.group(1))
            ior_minor = int(m.group(2))
            if ior_major >=3:
                if ior_minor >= 3:
                    ior_output_version = 33
                elif ior_minor >= 2:
                    ior_output_version = 32
                else:
                    ior_output_version = 30

        j += 1

    if ior_output_version is None:
        print("ERROR: unknown version of IOR output!!!")

    parser.successfulRun = False

    total_number_of_tests, tests_passed = process_ior_output_v33(parser, lines)

    if app_vars is not None and 'doAllWritesFirst' in app_vars:
        if app_vars['doAllWritesFirst']:
            # i.e. separate read and write
            total_number_of_tests = total_number_of_tests // 2
    else:
        # by default separate read and write
        total_number_of_tests = total_number_of_tests // 2

    parser.set_statistic('Number of Tests Passed', tests_passed)
    parser.set_statistic('Number of Tests Started', total_number_of_tests)

    if __name__ == "__main__":
        # output for testing purpose
        print("parsing complete:", parser.parsing_complete(verbose=True))
        parser.print_params_stats_as_must_have()
        parser.print_template_for_pytest()
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
