# Part of XDMoD=>AKRR
# parser for Intel MPI Benchmarks AK
#
# authors: Nikolay Simakov, Charng-Da Lu
#

import re
import os
import sys
from akrr.appkernelsparsers.akrrappkeroutputparser import AppKerOutputParser, total_seconds


def get_MiB(val, units):
    if units == "MiB":
        return val
    if units == "KiB":
        return val / 1024.0
    if units == "GiB":
        return val * 1024


def process_appker_output(appstdout=None, stdout=None, stderr=None, geninfo=None, resource_appker_vars=None):
    # set App Kernel Description
    parser = AppKerOutputParser(
        name='xdmod.benchmark.io.ior',
        version=1,
        description="IOR (Interleaved-Or-Random) Benchmark",
        url='http://freshmeat.net/projects/ior',
        measurement_name='IOR'
    )
    # set obligatory parameters and statistics
    # set common parameters and statistics
    parser.add_common_must_have_params_and_stats()
    # set app kernel custom sets
    parser.add_must_have_parameter('App:Version')
    if resource_appker_vars is None or (
            resource_appker_vars is not None and 'testHDF5' in resource_appker_vars and
            resource_appker_vars['testHDF5'] is True):
        parser.add_must_have_parameter('HDF Version')
        parser.add_must_have_parameter('HDF5 Collective N-to-1 Test File System')
        parser.add_must_have_parameter('HDF5 Independent N-to-1 Test File System')
        parser.add_must_have_parameter('HDF5 N-to-N Test File System')

    if resource_appker_vars is None or (
            resource_appker_vars is not None and 'testMPIIO' in resource_appker_vars and
            resource_appker_vars['testMPIIO'] is True):
        parser.add_must_have_parameter('MPIIO Collective N-to-1 Test File System')
        parser.add_must_have_parameter('MPIIO Independent N-to-1 Test File System')
        parser.add_must_have_parameter('MPIIO N-to-N Test File System')

    if resource_appker_vars is None or (
            resource_appker_vars is not None and 'testPOSIX' in resource_appker_vars and
            resource_appker_vars['testPOSIX'] is True):
        parser.add_must_have_parameter('POSIX N-to-1 Test File System')
        parser.add_must_have_parameter('POSIX N-to-N Test File System')

    if resource_appker_vars is None or (
            resource_appker_vars is not None and 'testNetCDF' in resource_appker_vars and
            resource_appker_vars['testNetCDF'] is True):
        parser.add_must_have_parameter('Parallel NetCDF Collective N-to-1 Test File System')
        parser.add_must_have_parameter('Parallel NetCDF Independent N-to-1 Test File System')
    parser.add_must_have_parameter('Parallel NetCDF Version')
    parser.add_must_have_parameter('Per-Process Data Size')
    parser.add_must_have_parameter('Per-Process I/O Block Size')
    parser.add_must_have_parameter('RunEnv:Nodes')
    parser.add_must_have_parameter('Transfer Size Per I/O')

    if resource_appker_vars is None or (
            resource_appker_vars is not None and 'testHDF5' in resource_appker_vars and
            resource_appker_vars['testHDF5'] is True):
        parser.add_must_have_statistic('HDF5 Collective N-to-1 Read Aggregate Throughput')
        parser.add_must_have_statistic('HDF5 Collective N-to-1 Write Aggregate Throughput')
        parser.add_must_have_statistic('HDF5 Independent N-to-1 Read Aggregate Throughput')
        parser.add_must_have_statistic('HDF5 Independent N-to-1 Write Aggregate Throughput')
        parser.add_must_have_statistic('HDF5 N-to-N Read Aggregate Throughput')
        parser.add_must_have_statistic('HDF5 N-to-N Write Aggregate Throughput')

    if resource_appker_vars is None or (
            resource_appker_vars is not None and 'testMPIIO' in resource_appker_vars and
            resource_appker_vars['testMPIIO'] is True):
        parser.add_must_have_statistic('MPIIO Collective N-to-1 Read Aggregate Throughput')
        parser.add_must_have_statistic('MPIIO Collective N-to-1 Write Aggregate Throughput')
        parser.add_must_have_statistic('MPIIO Independent N-to-1 Read Aggregate Throughput')
        parser.add_must_have_statistic('MPIIO Independent N-to-1 Write Aggregate Throughput')
        parser.add_must_have_statistic('MPIIO N-to-N Read Aggregate Throughput')
        parser.add_must_have_statistic('MPIIO N-to-N Write Aggregate Throughput')

    if resource_appker_vars is None or (
            resource_appker_vars is not None and 'testPOSIX' in resource_appker_vars and
            resource_appker_vars['testPOSIX'] is True):
        parser.add_must_have_statistic('POSIX N-to-1 Read Aggregate Throughput')
        parser.add_must_have_statistic('POSIX N-to-1 Write Aggregate Throughput')
        parser.add_must_have_statistic('POSIX N-to-N Read Aggregate Throughput')
        parser.add_must_have_statistic('POSIX N-to-N Write Aggregate Throughput')

    if resource_appker_vars is None or (
            resource_appker_vars is not None and 'testNetCDF' in resource_appker_vars and
            resource_appker_vars['testNetCDF'] is True):
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
            ior_output_version = 2

        m = re.match(r'^IOR-[3-9]\.[0-9]+\.[0-9]: MPI Coordinated Test of Parallel I/O', lines[j])
        if m:
            ior_output_version = 3

        j += 1
    if ior_output_version is None:
        print("ERROR: unknown version of IOR output!!!")

    tests_passed = 0
    total_number_of_tests = 0
    parser.successfulRun = False

    write_label = ""

    if ior_output_version == 2:
        metrics = {}
        j = -1
        while j < len(lines) - 1:
            m = re.match(r'^# (.+?):(.+)', lines[j])
            if m:
                metrics[m.group(1).strip()] = m.group(2).strip()
                if m.group(1).strip() == "segmentCount":
                    metrics[m.group(1).strip()] = m.group(2).strip().split()[0]
            m = re.match(r'^# IOR command line used:', lines[j])
            if m:
                total_number_of_tests += 1

            if "IOR RELEASE" in metrics:
                parser.set_parameter("App:Version", metrics["IOR RELEASE"])

            if "Compile-time HDF Version" in metrics:
                parser.set_parameter("HDF Version", metrics["Compile-time HDF Version"])

            if "Compile-time PNETCDF Version" in metrics:
                parser.set_parameter("Parallel NetCDF Version", metrics["Compile-time PNETCDF Version"])

            if "blockSize" in metrics and "segmentCount" in metrics:
                # print METRICS["blockSize"],METRICS["segmentCount"]
                parser.set_parameter("Per-Process Data Size",
                                     (float(metrics["blockSize"]) / 1024.0 / 1024.0) * int(metrics["segmentCount"]),
                                     "MByte")
                parser.set_parameter("Per-Process I/O Block Size", (float(metrics["blockSize"]) / 1024.0 / 1024.0),
                                     "MByte")

            if "reorderTasks" in metrics:
                if int(metrics["reorderTasks"]) != 0:
                    parser.set_parameter("Reorder Tasks for Read-back Tests", "Yes")

            if "repetitions" in metrics:
                if 1 < int(metrics["repetitions"]):
                    parser.set_parameter("Test Repetitions", metrics["repetitions"])

            if "transferSize" in metrics:
                parser.set_parameter("Transfer Size Per I/O", (float(metrics["transferSize"]) / 1024.0 / 1024.0),
                                     "MByte")

            if "mpiio hints passed to MPI_File_open" in metrics:
                parser.set_parameter("MPI-IO Hints", metrics["mpiio hints passed to MPI_File_open"])

            if "Write bandwidth" in metrics and "Read bandwidth" in metrics and \
                    "api" in metrics and "filePerProc" in metrics and "collective" in metrics and \
                    "randomOffset" in metrics and "Run finished" in metrics:

                tests_passed += 1

                label = metrics["api"]

                m = re.search(r'NCMPI', label, re.I)
                if m:
                    label = "Parallel NetCDF"

                m = re.search(r'POSIX', label, re.I)
                if m and "useO_DIRECT" in metrics:
                    if int(metrics["useO_DIRECT"]) != 0:
                        label += ' (O_DIRECT)'
                if m is None:
                    # POSIX doesn't have collective I/O
                    if int(metrics["collective"]) == 0:
                        label += ' Independent'
                    else:
                        label += ' Collective'

                if int(metrics["randomOffset"]) == 0:
                    label += ''
                else:
                    label += ' Random'

                if int(metrics["filePerProc"]) == 0:
                    label += ' N-to-1'
                else:
                    label += ' N-to-N'

                # for N-to-N (each process writes to its own file), it must be
                # Independent, so we can remove the redundant words such as
                # "Independent" and "Collective"
                m = re.search(r' (Independent|Collective).+N-to-N', label, re.I)
                if m:
                    label = label.replace(" Independent", "").replace(" Collective", "")

                # now we have the label, get test-specific parameters
                m = re.search(r'MPIIO', label, re.I)
                if m:
                    if "useFileView" in metrics:
                        if 0 != int(metrics["useFileView"]):
                            parser.set_parameter(label + " Uses MPI_File_set_view", "Yes")
                    if "useSharedFilePointer" in metrics:
                        if 0 != int(metrics["useSharedFilePointer"]):
                            parser.set_parameter(label + " Uses Shared File Pointer", "Yes")

                m = re.search(r'POSIX', label, re.I)
                if m:
                    if "fsyncPerWrite" in metrics:
                        if 0 != int(metrics["fsyncPerWrite"]):
                            parser.set_parameter(label + " Uses fsync per Write", "Yes")

                m = re.search(r'mean=(\S+)', metrics["Write bandwidth"])
                if m:
                    metric = m.group(1).strip()
                    write_label = label

                    # writes are always sequential
                    write_label = write_label.replace(" Random", "")
                    parser.set_statistic(write_label + " Write Aggregate Throughput",
                                         "%.2f" % (float(metric) / 1024.0 / 1024.0,), "MByte per Second")

                    if "fileSystem" in metrics:
                        parser.set_parameter(write_label + " Test File System", metrics["fileSystem"])
                    parser.successfulRun = True

                    if "File Open Time (Write)" in metrics:
                        m2 = re.search(r'mean=(\S+)', metrics["File Open Time (Write)"])
                        if m2:
                            parser.set_statistic(write_label + "  File Open Time (Write)", m2.group(1).strip(),
                                                 "Second")
                    if "File Close Time (Write)" in metrics:
                        m2 = re.search(r'mean=(\S+)', metrics["File Close Time (Write)"])
                        if m2:
                            parser.set_statistic(write_label + "  File Close Time (Write)", m2.group(1).strip(),
                                                 "Second")

                m = re.search(r'mean=(\S+)', metrics["Read bandwidth"])
                if m:
                    parser.set_statistic(label + " Read Aggregate Throughput",
                                         "%.2f" % (float(m.group(1).strip()) / 1024.0 / 1024.0,), "MByte per Second")
                    parser.successfulRun = True

                    if "File Open Time (Read)" in metrics:
                        m2 = re.search(r'mean=(\S+)', metrics["File Open Time (Read)"])
                        if m2:
                            parser.set_statistic(write_label + "  File Open Time (Read)", m2.group(1).strip(), "Second")
                    if "File Close Time (Read)" in metrics:
                        m2 = re.search(r'mean=(\S+)', metrics["File Close Time (Read)"])
                        if m2:
                            parser.set_statistic(write_label + "  File Close Time (Read)", m2.group(1).strip(),
                                                 "Second")

                metrics = {}

            j += 1

    if ior_output_version == 3:
        i = 0
        input_summary = {}
        filesystem = None
        while i < len(lines) - 1:
            m = re.match(r'^IOR-([3-9]\.[0-9]+\.[0-9]+): MPI Coordinated Test of Parallel I/O', lines[i])
            if m:
                parser.set_parameter("App:Version", m.group(1).strip())

            m = re.match(r'^File System To Test:(.+)', lines[i])
            if m:
                filesystem = m.group(1).strip()

            m = re.match(r'^# Starting Test:', lines[i])
            if m:
                total_number_of_tests += 1

            m0 = re.match(r'^Summary:$', lines[i])
            if m0:
                # input summary section
                input_summary = {}
                i += 1
                while i < len(lines):
                    m1 = re.match(r'^\t([^=\n\r\f\v]+)=(.+)', lines[i])
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
                    input_summary['API_Version'] = input_summary['api'].replace("MPIIO", "").strip()
                    parser.set_parameter("MPIIO Version", input_summary['API_Version'])
                if input_summary['api'].count("HDF5") > 0:
                    input_summary['API'] = "HDF5"
                    input_summary['API_Version'] = input_summary['api'].replace("HDF5-", "").replace("HDF5", "").strip()
                    parser.set_parameter("HDF Version", input_summary['API_Version'])
                if input_summary['api'].count("NCMPI") > 0:
                    input_summary['API'] = "Parallel NetCDF"
                    input_summary['API_Version'] = input_summary['api'].replace("NCMPI", "").strip()
                    parser.set_parameter("Parallel NetCDF Version", input_summary['API_Version'])

                input_summary['fileAccessPattern'] = ""
                input_summary['collectiveOrIndependent'] = ""
                if input_summary['access'].count('single-shared-file') > 0:
                    input_summary['fileAccessPattern'] = "N-to-1"
                if input_summary['access'].count('file-per-process') > 0:
                    input_summary['fileAccessPattern'] = "N-to-N"
                if input_summary['access'].count('independent') > 0:
                    input_summary['collectiveOrIndependent'] = "Independent"
                if input_summary['access'].count('collective') > 0:
                    input_summary['collectiveOrIndependent'] = "Collective"
                if input_summary['fileAccessPattern'] == "N-to-N" and \
                        input_summary['collectiveOrIndependent'] == "Independent":
                    input_summary['collectiveOrIndependent'] = ""

                if input_summary['collectiveOrIndependent'] != "":
                    input_summary['method'] = " ".join((input_summary['API'],
                                                        input_summary['collectiveOrIndependent'],
                                                        input_summary['fileAccessPattern']))
                else:
                    input_summary['method'] = " ".join((input_summary['API'],
                                                        input_summary['fileAccessPattern']))

                if input_summary['filesystem'] is not None:
                    parser.set_parameter(input_summary['method'] + ' Test File System', input_summary['filesystem'])

                if "pattern" in input_summary:
                    m1 = re.match(r'^segmented \(([0-9]+) segment', input_summary["pattern"])
                    if m1:
                        input_summary["segmentCount"] = int(m1.group(1).strip())

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
                r'^access\s+bw\(MiB/s\)\s+block\(KiB\)\s+xfer\(KiB\)\s+open\(s\)\s+wr/rd\(s\)\s+close\(s\)\s+total\(s\)\s+iter',
                lines[i])
            if m0:
                i += 1
                while i < len(lines):
                    m1 = re.match(
                        r'^write\s+([0-9.]+)+\s+([0-9.]+)+\s+([0-9.]+)+\s+([0-9.]+)+\s+([0-9.]+)+\s+([0-9.]+)+\s+([0-9.]+)+\s+([0-9.]+)+',
                        lines[i])
                    m2 = re.match(
                        r'^read\s+([0-9.]+)+\s+([0-9.]+)+\s+([0-9.]+)+\s+([0-9.]+)+\s+([0-9.]+)+\s+([0-9.]+)+\s+([0-9.]+)+\s+([0-9.]+)+',
                        lines[i])
                    if m1 or m2:
                        if m1:
                            access = "Write"
                            bw, block, xfer, open_s, wrrd_s, close_s, total_s, iter_s = m1.groups()
                        else:
                            access = "Read"
                            bw, block, xfer, open_s, wrrd_s, close_s, total_s, iter_s = m2.groups()
                            tests_passed += 1
                            parser.successfulRun = True

                        parser.set_statistic(input_summary['method'] + " %s Aggregate Throughput" % access, bw,
                                             "MByte per Second")
                        parser.set_statistic(input_summary['method'] + "  File Open Time (%s)" % access, open_s,
                                             "Second")
                        parser.set_statistic(input_summary['method'] + "  File Close Time (%s)" % access, close_s,
                                             "Second")

                    m1 = re.match(r'^Summary of all tests:', lines[i])
                    if m1:
                        break
                    i += 1
                # reset variables
                input_summary = {}
                # filesystem=None
            i += 1
    parser.set_statistic('Number of Tests Passed', tests_passed)
    parser.set_statistic('Number of Tests Started', total_number_of_tests)

    if __name__ == "__main__":
        # output for testing purpose
        print("parsing complete:", parser.parsing_complete(verbose=True))
        parser.print_params_stats_as_must_have()
        print(parser.get_xml())

    # return complete XML overwize return None
    return parser.get_xml()


if __name__ == "__main__":
    """stand alone testing"""
    jobdir = sys.argv[1]
    print("Proccessing Output From", jobdir)
    process_appker_output(appstdout=os.path.join(jobdir, "appstdout"), geninfo=os.path.join(jobdir, "gen.info"))
