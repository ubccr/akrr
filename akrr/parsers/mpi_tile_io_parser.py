# Part of XDMoD=>AKRR
# parser for Intel MPI Benchmarks AK
#
# authors: Nikolay Simakov, Charng-Da Lu
#

import re
import os
import sys
from akrr.parsers.akrrappkeroutputparser import AppKerOutputParser


def process_appker_output(appstdout=None, stdout=None, stderr=None, geninfo=None, proclog=None, 
                          resource_appker_vars=None):
    # set App Kernel Description
    parser = AppKerOutputParser(
        name='mpi-tile-io',
        version=1,
        description="MPI-Tile-IO Benchmark",
        url='http://www.mcs.anl.gov/research/projects/pio-benchmark',
        measurement_name='MPI-Tile-IO'
    )
    # set obligatory parameters and statistics
    # set common parameters and statistics
    parser.add_common_must_have_params_and_stats()
    # set app kernel custom sets
    parser.add_must_have_parameter('2D Collective Read Test File System')
    parser.add_must_have_parameter('2D Collective Write Test File System')
    parser.add_must_have_parameter('2D HDF5 Collective Read Test File System')
    parser.add_must_have_parameter('2D HDF5 Collective Write Test File System')
    parser.add_must_have_parameter('2D Independent Read Test File System')
    parser.add_must_have_parameter('2D Independent Write Test File System')
    parser.add_must_have_parameter('2D Per-Process Data Topology')
    parser.add_must_have_parameter('2D Per-Process Ghost Zone')
    parser.add_must_have_parameter('2D Per-Process Memory')
    parser.add_must_have_parameter('2D Process Topology')
    parser.add_must_have_parameter('3D Collective Read Test File System')
    parser.add_must_have_parameter('3D Collective Write Test File System')
    parser.add_must_have_parameter('3D HDF5 Collective Read Test File System')
    parser.add_must_have_parameter('3D HDF5 Collective Write Test File System')
    parser.add_must_have_parameter('3D Independent Read Test File System')
    parser.add_must_have_parameter('3D Independent Write Test File System')
    parser.add_must_have_parameter('3D Per-Process Data Topology')
    parser.add_must_have_parameter('3D Per-Process Ghost Zone')
    parser.add_must_have_parameter('3D Per-Process Memory')
    parser.add_must_have_parameter('3D Process Topology')
    parser.add_must_have_parameter('App:ExeBinSignature')
    parser.add_must_have_parameter('HDF Version')
    # parser.add_must_have_parameter('MPI-IO Hints')
    parser.add_must_have_parameter('RunEnv:Nodes')

    parser.add_must_have_statistic('2D Array Collective Read Aggregate Throughput')
    parser.add_must_have_statistic('2D Array Collective Write Aggregate Throughput')
    parser.add_must_have_statistic('2D Array HDF5 Collective Read Aggregate Throughput')
    parser.add_must_have_statistic('2D Array HDF5 Collective Write Aggregate Throughput')
    parser.add_must_have_statistic('2D Array Independent Read Aggregate Throughput')
    parser.add_must_have_statistic('2D Array Independent Write Aggregate Throughput')
    parser.add_must_have_statistic('3D Array Collective Read Aggregate Throughput')
    parser.add_must_have_statistic('3D Array Collective Write Aggregate Throughput')
    parser.add_must_have_statistic('3D Array HDF5 Collective Read Aggregate Throughput')
    parser.add_must_have_statistic('3D Array HDF5 Collective Write Aggregate Throughput')
    parser.add_must_have_statistic('3D Array Independent Read Aggregate Throughput')
    parser.add_must_have_statistic('3D Array Independent Write Aggregate Throughput')
    parser.add_must_have_statistic('File Close Time (2D Data Collective Read)')
    parser.add_must_have_statistic('File Close Time (2D Data Collective Write)')
    parser.add_must_have_statistic('File Close Time (2D Data HDF5 Collective Read)')
    parser.add_must_have_statistic('File Close Time (2D Data HDF5 Collective Write)')
    parser.add_must_have_statistic('File Close Time (2D Data Independent Read)')
    parser.add_must_have_statistic('File Close Time (2D Data Independent Write)')
    parser.add_must_have_statistic('File Close Time (3D Data Collective Read)')
    parser.add_must_have_statistic('File Close Time (3D Data Collective Write)')
    parser.add_must_have_statistic('File Close Time (3D Data HDF5 Collective Read)')
    parser.add_must_have_statistic('File Close Time (3D Data HDF5 Collective Write)')
    parser.add_must_have_statistic('File Close Time (3D Data Independent Read)')
    parser.add_must_have_statistic('File Close Time (3D Data Independent Write)')
    parser.add_must_have_statistic('File Open Time (2D Data Collective Read)')
    parser.add_must_have_statistic('File Open Time (2D Data Collective Write)')
    parser.add_must_have_statistic('File Open Time (2D Data HDF5 Collective Read)')
    parser.add_must_have_statistic('File Open Time (2D Data HDF5 Collective Write)')
    parser.add_must_have_statistic('File Open Time (2D Data Independent Read)')
    parser.add_must_have_statistic('File Open Time (2D Data Independent Write)')
    parser.add_must_have_statistic('File Open Time (3D Data Collective Read)')
    parser.add_must_have_statistic('File Open Time (3D Data Collective Write)')
    parser.add_must_have_statistic('File Open Time (3D Data HDF5 Collective Read)')
    parser.add_must_have_statistic('File Open Time (3D Data HDF5 Collective Write)')
    parser.add_must_have_statistic('File Open Time (3D Data Independent Read)')
    parser.add_must_have_statistic('File Open Time (3D Data Independent Write)')
    parser.add_must_have_statistic('Wall Clock Time')

    # parse common parameters and statistics
    parser.parse_common_params_and_stats(appstdout, stdout, stderr, geninfo, resource_appker_vars)

    if hasattr(parser, 'appKerWallClockTime'):
        parser.set_statistic("Wall Clock Time", parser.appKerWallClockTime.total_seconds(), "Second")

    # read output
    lines = []
    if os.path.isfile(appstdout):
        fin = open(appstdout, "rt")
        lines = fin.readlines()
        fin.close()

    # process the output
    # The parameters mapping table
    # The result mapping table
    pm = {
        "processesTopology": {
            're': r"^# processes topology:(.+)",
            'refun': re.match,
            'val': None},
        "localDatasetTopology": {
            're': r"^# local dataset topology:(.+)element",
            'refun': re.match,
            'val': None},
        "localMemoryUsage": {
            're': r"^# local dataset memory usage:(.+)byte",
            'refun': re.match,
            'val': None},
        "datasetGhostZone": {
            're': r"^# local dataset ghost zone:(.+)",
            'refun': re.match,
            'val': None},
        "mpiIOhints": {
            're': r"^# mpiio hints:(.+)",
            'refun': re.match,
            'val': None},
        "maxFileOpenTime": {
            're': r"^# Open:.+?max=(\S+)",
            'refun': re.match,
            'val': None},
        "maxFileCloseTime": {
            're': r"^# Close:.+?max=(\S+)",
            'refun': re.match,
            'val': None},
        "collectiveIO": {
            're': r"^# collective IO:(.+)",
            'refun': re.match,
            'val': None},
        "testFileName": {
            're': r"^# filename:(.+)",
            'refun': re.match,
            'val': None},
        "fileSystem": {
            're': r"^# filesystem:(.+)",
            'refun': re.match,
            'val': None},
        "hdf5Version": {
            're': r"^# HDF5 Version:(.+)",
            'refun': re.match,
            'val': None},
    }

    parser.successfulRun = False
    j = -1
    while j < len(lines) - 1:
        for k, v in pm.items():
            m = v['refun'](v['re'], lines[j])
            if m:
                v['val'] = m.group(1).strip()

        m = re.match(r'^# (.+?)bandwidth:(.+)bytes', lines[j])
        if m:
            read_or_write = m.group(1).strip()
            io_bandwidth = m.group(2).strip()

            # can output data ?
            if pm['processesTopology']['val'] and pm['collectiveIO']['val']:
                # construct the label
                label = ''
                dim = '2D'
                m = re.search(r'\d+x\d+x\d', pm['processesTopology']['val'])
                if m:
                    dim = '3D'

                if pm['hdf5Version']['val']:
                    label += 'HDF5 '
                    parser.set_parameter("HDF Version", pm['hdf5Version']['val'])

                m = re.search(r'yes', pm['collectiveIO']['val'], re.I)
                if m:
                    label += 'Collective '
                else:
                    label += 'Independent '

                m0 = re.search(r'read', read_or_write, re.I)
                m1 = re.search(r'write', read_or_write, re.I)
                if m0:
                    label += 'Read'
                elif m1:
                    label += 'Write'
                else:
                    label += read_or_write[0].upper() + read_or_write[1:]

                parser.set_statistic("%s Array %s Aggregate Throughput" % (dim, label),
                                     "%.2f" % (float(io_bandwidth) / 1024.0 / 1024.0), "MByte per Second")
                if pm["maxFileOpenTime"]['val']:
                    parser.set_statistic("File Open Time (%s Data %s)" % (dim, label), pm["maxFileOpenTime"]['val'],
                                         "Second")
                if pm["maxFileCloseTime"]['val']:
                    parser.set_statistic("File Close Time (%s Data %s)" % (dim, label), pm["maxFileCloseTime"]['val'],
                                         "Second")

                parser.set_parameter("%s Process Topology" % (dim,), pm["processesTopology"]['val'])
                if pm["localMemoryUsage"]['val']:
                    parser.set_parameter("%s Per-Process Memory" % (dim,),
                                         float(pm["localMemoryUsage"]['val']) / 1024.0 / 1024.0, "MByte")
                if pm["localDatasetTopology"]['val']:
                    parser.set_parameter("%s Per-Process Data Topology" % (dim,), pm["localDatasetTopology"]['val'],
                                         "Element")
                if pm["datasetGhostZone"]['val']:
                    parser.set_parameter("%s Per-Process Ghost Zone" % (dim,), pm["datasetGhostZone"]['val'])
                if pm["mpiIOhints"]['val']:
                    parser.set_parameter("MPI-IO Hints", pm["mpiIOhints"]['val'])
                # $benchmark->set_parameter( "${dim} ${label} Test File", $testFileName ) if( defined($testFileName) )
                if pm["fileSystem"]['val']:
                    parser.set_parameter("%s %s Test File System" % (dim, label), pm["fileSystem"]['val'])
                parser.successfulRun = True

                pm["processesTopology"]['val'] = None
                pm["localDatasetTopology"]['val'] = None
                pm["localMemoryUsage"]['val'] = None
                pm["datasetGhostZone"]['val'] = None
                pm["mpiIOhints"]['val'] = None
                # pm["readOrWrite"]['val']=None
                pm["collectiveIO"]['val'] = None
                # pm["IObandwidth"]['val']=None
                pm["maxFileOpenTime"]['val'] = None
                pm["maxFileCloseTime"]['val'] = None
                pm["testFileName"]['val'] = None
                pm["fileSystem"]['val'] = None
                pm["hdf5Version"]['val'] = None
        j += 1

    if __name__ == "__main__":
        # output for testing purpose
        print("parsing complete:", parser.parsing_complete(verbose=True))
        parser.print_params_stats_as_must_have()
        print(parser.get_xml())
    # Print out missing parameters for debug purpose
    parser.parsing_complete(verbose=True)
    # return complete XML overwize return None
    return parser.get_xml()


if __name__ == "__main__":
    """stand alone testing"""
    jobdir = sys.argv[1]
    print("Proccessing Output From", jobdir)
    process_appker_output(appstdout=os.path.join(jobdir, "appstdout"), geninfo=os.path.join(jobdir, "gen.info"))
