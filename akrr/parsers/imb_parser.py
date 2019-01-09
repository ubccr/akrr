# Part of XDMoD=>AKRR
# parser for Intel MPI Benchmarks AK
#
# authors: Nikolay Simakov, Charng-Da Lu
#

import re
import os
import sys
from akrr.parsers.akrrappkeroutputparser import AppKerOutputParser, total_seconds
from akrr.util import get_float_or_int


def process_appker_output(appstdout=None, stdout=None, stderr=None, geninfo=None, resource_appker_vars=None):
    # set App Kernel Description
    parser = AppKerOutputParser(
        name='xdmod.benchmark.mpi.imb',
        version=1,
        description="Intel MPI Benchmarks",
        url='http://www.intel.com/software/imb',
        measurement_name='Intel MPI Benchmarks'
    )
    # set obligatory parameters and statistics
    # set common parameters and statistics
    parser.add_common_must_have_params_and_stats()
    # set app kernel custom sets
    parser.add_must_have_parameter('App:MPI Thread Environment')
    parser.add_must_have_parameter('App:MPI Version')
    parser.add_must_have_parameter('App:Max Message Size')

    parser.add_must_have_statistic('Max Exchange Bandwidth')
    parser.add_must_have_statistic("Max MPI-2 Bidirectional 'Get' Bandwidth (aggregate)")
    parser.add_must_have_statistic("Max MPI-2 Bidirectional 'Get' Bandwidth (non-aggregate)")
    parser.add_must_have_statistic("Max MPI-2 Bidirectional 'Put' Bandwidth (aggregate)")
    parser.add_must_have_statistic("Max MPI-2 Bidirectional 'Put' Bandwidth (non-aggregate)")
    parser.add_must_have_statistic("Max MPI-2 Unidirectional 'Get' Bandwidth (aggregate)")
    parser.add_must_have_statistic("Max MPI-2 Unidirectional 'Get' Bandwidth (non-aggregate)")
    parser.add_must_have_statistic("Max MPI-2 Unidirectional 'Put' Bandwidth (aggregate)")
    parser.add_must_have_statistic("Max MPI-2 Unidirectional 'Put' Bandwidth (non-aggregate)")
    parser.add_must_have_statistic('Max PingPing Bandwidth')
    parser.add_must_have_statistic('Max PingPong Bandwidth')
    parser.add_must_have_statistic('Max SendRecv Bandwidth')
    parser.add_must_have_statistic('Min AllGather Latency')
    parser.add_must_have_statistic('Min AllGatherV Latency')
    parser.add_must_have_statistic('Min AllReduce Latency')
    parser.add_must_have_statistic('Min AllToAll Latency')
    parser.add_must_have_statistic('Min AllToAllV Latency')
    parser.add_must_have_statistic('Min Barrier Latency')
    parser.add_must_have_statistic('Min Broadcast Latency')
    parser.add_must_have_statistic('Min Gather Latency')
    parser.add_must_have_statistic('Min GatherV Latency')
    # parser.add_must_have_statistic("Min MPI-2 'Accumulate' Latency (aggregate)")
    # parser.add_must_have_statistic("Min MPI-2 'Accumulate' Latency (non-aggregate)")
    parser.add_must_have_statistic('Min MPI-2 Window Creation Latency')
    parser.add_must_have_statistic('Min Reduce Latency')
    parser.add_must_have_statistic('Min ReduceScatter Latency')
    parser.add_must_have_statistic('Min Scatter Latency')
    parser.add_must_have_statistic('Min ScatterV Latency')
    parser.add_must_have_statistic('Wall Clock Time')

    # parse common parameters and statistics
    parser.parse_common_params_and_stats(appstdout, stdout, stderr, geninfo, resource_appker_vars)

    if hasattr(parser, 'appKerWallClockTime'):
        parser.set_statistic("Wall Clock Time", total_seconds(parser.appKerWallClockTime), "Second")

    # Intel MPI benchmark suite contains three classes of benchmarks:
    #
    #  Single-transfer, which needs only 2 processes
    #  Parallel-transfer, which can use as many processes that are available
    #  Collective, which can use as many processes that are available

    # The parameters mapping table
    params = {
        "MPI Thread Environment": ["MPI Thread Environment", "", ""],
        "MPI Version": ["MPI Version", "", ""],
        "Maximum message length in bytes": ["Max Message Size", "MByte", "<val>/1024/1024"]
    }

    # The result mapping table
    metrics = {
        "PingPing": ["PingPing Bandwidth", "MByte per Second", "max"],
        "PingPong": ["PingPong Bandwidth", "MByte per Second", "max"],
        "Multi-PingPing": ["PingPing Bandwidth", "MByte per Second", "max"],
        "Multi-PingPong": ["PingPong Bandwidth", "MByte per Second", "max"],
        "Sendrecv": ["SendRecv Bandwidth", "MByte per Second", "max"],
        "Exchange": ["Exchange Bandwidth", "MByte per Second", "max"],
        "Allreduce": ["AllReduce Latency", "us", "min"],
        "Reduce": ["Reduce Latency", "us", "min"],
        "Reduce_scatter": ["ReduceScatter Latency", "us", "min"],
        "Allgather": ["AllGather Latency", "us", "min"],
        "Allgatherv": ["AllGatherV Latency", "us", "min"],
        "Gather": ["Gather Latency", "us", "min"],
        "Gatherv": ["GatherV Latency", "us", "min"],
        "Scatter": ["Scatter Latency", "us", "min"],
        "Scatterv": ["ScatterV Latency", "us", "min"],
        "Alltoall": ["AllToAll Latency", "us", "min"],
        "Alltoallv": ["AllToAllV Latency", "us", "min"],
        "Bcast": ["Broadcast Latency", "us", "min"],
        "Barrier": ["Barrier Latency", "us", "min"],
        "Window": ["MPI-2 Window Creation Latency", "us", "min"],
        "Multi-Unidir_Get": ["MPI-2 Unidirectional 'Get' Bandwidth", "MByte per Second", "max"],
        "Multi-Unidir_Put": ["MPI-2 Unidirectional 'Put' Bandwidth", "MByte per Second", "max"],
        "Multi-Bidir_Get": ["MPI-2 Bidirectional 'Get' Bandwidth", "MByte per Second", "max"],
        "Multi-Bidir_Put": ["MPI-2 Bidirectional 'Put' Bandwidth", "MByte per Second", "max"],
        "Unidir_Get": ["MPI-2 Unidirectional 'Get' Bandwidth", "MByte per Second", "max"],
        "Unidir_Put": ["MPI-2 Unidirectional 'Put' Bandwidth", "MByte per Second", "max"],
        "Bidir_Get": ["MPI-2 Bidirectional 'Get' Bandwidth", "MByte per Second", "max"],
        "Bidir_Put": ["MPI-2 Bidirectional 'Put' Bandwidth", "MByte per Second", "max"],
        "Accumulate": ["MPI-2 'Accumulate' Latency", "us", "min"]
    }

    # read output
    lines = []
    if os.path.isfile(appstdout):
        fin = open(appstdout, "rt")
        lines = fin.readlines()
        fin.close()

    # process the output
    parser.successfulRun = False
    aggregate_mode = None
    metric = None
    j = -1
    while j < len(lines) - 1:
        j += 1
        m = re.search(r'All processes entering MPI_Finalize', lines[j])
        if m:
            parser.successfulRun = True

        m = re.match(r'^# Benchmarking\s+(\S+)', lines[j])
        if m:
            if m.group(1) in metrics:
                metric = m.group(1)
                continue

        m = re.match(r'^#\s+MODE:\s+(\S+)', lines[j])
        if m and metric and aggregate_mode is None:
            aggregate_mode = m.group(1)
            continue

        m = re.match(r'^# (.+): (.+)', lines[j])
        if m:  # benchmark parameters
            param = m.group(1).strip()
            if param in params:
                val = m.group(2).strip()
                v = params[param][2]
                if v.find('<val>') >= 0:
                    val = get_float_or_int(val)
                    val = eval(v.replace('<val>', 'val'))
                parser.set_parameter("App:" + params[param][0], str(val) + " ", params[param][1])
            continue

        m = re.match(r'^\s+([1-9]\d*)\s+\d+', lines[j])
        if m and metric:  # this effectively skips the first line of result, which has #bytes = 0
            results = []

            while m:
                numbers = lines[j].split()
                results.append(float(numbers[-1]))  # tokenize the line, and extract the last column

                j += 1
                if j < len(lines):
                    m = re.match(r'^\s+([1-9]\d*)\s+\d+', lines[j])
                    if lines[j].count('IMB_init_buffers_iter') > 0:
                        break
                else:
                    break
            metric_name = metrics[metric][0]
            if aggregate_mode:
                metric_name += " (" + aggregate_mode.lower() + ")"
            if len(results) > 0:
                if metrics[metric][1] == 'us':
                    statname = metrics[metric][2][0].upper() + metrics[metric][2][1:] + " " + metric_name
                    statval = eval(metrics[metric][2] + "(results)")
                    parser.set_statistic(statname, statval * 1e-6, "Second")
                else:
                    statname = metrics[metric][2][0].upper() + metrics[metric][2][1:] + " " + metric_name
                    statval = eval(metrics[metric][2] + "(results)")
                    parser.set_statistic(statname, statval, metrics[metric][1])

            aggregate_mode = None
            metric = None
    if parser.get_parameter("App:MPI Thread Environment") is None:
        parser.set_parameter("App:MPI Thread Environment", "")

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
