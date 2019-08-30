import re
import os
import sys
from akrr.parsers.akrrappkeroutputparser import AppKerOutputParser, total_seconds
from akrr.util import get_float_or_int
from akrr.util import log


def process_appker_output(appstdout=None, stdout=None, stderr=None, geninfo=None, resource_appker_vars=None):
    # set App Kernel Description
    parser = AppKerOutputParser(
        name='hpcc',
        version=1,
        description="HPC Challenge Benchmarks",
        url='http://icl.cs.utk.edu/hpcc/',
        measurement_name='xdmod.benchmark.hpcc'
    )
    # set obligatory parameters and statistics
    # set common parameters and statistics
    parser.add_common_must_have_params_and_stats()
    # set app kernel custom sets
    parser.add_must_have_parameter('App:Version')
    parser.add_must_have_parameter('Input:DGEMM Problem Size')
    parser.add_must_have_parameter('Input:High Performance LINPACK Grid Cols')
    parser.add_must_have_parameter('Input:High Performance LINPACK Grid Rows')
    parser.add_must_have_parameter('Input:High Performance LINPACK Problem Size')
    parser.add_must_have_parameter('Input:MPI Ranks')
    parser.add_must_have_parameter('Input:MPIRandom Problem Size')
    parser.add_must_have_parameter('Input:OpenMP Threads')
    parser.add_must_have_parameter('Input:PTRANS Problem Size')
    parser.add_must_have_parameter('Input:STREAM Array Size')
    # parser.add_must_have_parameter('RunEnv:CPU Speed')
    parser.add_must_have_parameter('RunEnv:Nodes')

    parser.add_must_have_statistic(
        'Average Double-Precision General Matrix Multiplication (DGEMM) Floating-Point Performance')
    parser.add_must_have_statistic("Average STREAM 'Add' Memory Bandwidth")
    parser.add_must_have_statistic("Average STREAM 'Copy' Memory Bandwidth")
    parser.add_must_have_statistic("Average STREAM 'Scale' Memory Bandwidth")
    parser.add_must_have_statistic("Average STREAM 'Triad' Memory Bandwidth")
    parser.add_must_have_statistic('Fast Fourier Transform (FFTW) Floating-Point Performance')
    # parser.add_must_have_statistic('High Performance LINPACK Efficiency')
    parser.add_must_have_statistic('High Performance LINPACK Floating-Point Performance')
    parser.add_must_have_statistic('High Performance LINPACK Run Time')
    parser.add_must_have_statistic('MPI Random Access')
    parser.add_must_have_statistic('Parallel Matrix Transpose (PTRANS)')
    parser.add_must_have_statistic('Wall Clock Time')
    # parse common parameters and statistics
    parser.parse_common_params_and_stats(appstdout, stdout, stderr, geninfo, resource_appker_vars)

    if parser.appKerWallClockTime is not None:
        parser.set_statistic("Wall Clock Time", total_seconds(parser.appKerWallClockTime), "Second")

    # Intel MPI benchmark suite contains three classes of benchmarks:
    #
    #  Single-transfer, which needs only 2 processes
    #  Parallel-transfer, which can use as many processes that are available
    #  Collective, which can use as many processes that are available

    # The parameters mapping table
    params = {
        "CommWorldProcs": ["MPI Ranks", "", ""],
        "HPL_N": ["High Performance LINPACK Problem Size", "", ""],
        "HPL_nprow": ["High Performance LINPACK Grid Rows", "", ""],
        "HPL_npcol": ["High Performance LINPACK Grid Cols", "", ""],
        "PTRANS_n": ["PTRANS Problem Size", "", ""],
        "MPIRandomAccess_N": ["MPIRandom Problem Size", "MWord", "val/1024/1024"],
        "STREAM_VectorSize": ["STREAM Array Size", "MWord", ""],
        "DGEMM_N": ["DGEMM Problem Size", "", ""],
        "omp_get_num_threads": ["OpenMP Threads", "", ""],
    }

    # The result mapping table
    metrics = {
        "HPL_Tflops": ["High Performance LINPACK Floating-Point Performance",
                       "MFLOP per Second", "val*1e6"],
        "HPL_time": ["High Performance LINPACK Run Time",
                     "Second", ""],
        "PTRANS_GBs": ["Parallel Matrix Transpose (PTRANS)",
                       "MByte per Second", "val*1024"],
        "MPIRandomAccess_GUPs": ["MPI Random Access",
                                 "MUpdate per Second", "val*1000"],
        "MPIFFT_Gflops": ["Fast Fourier Transform (FFTW) Floating-Point Performance",
                          "MFLOP per Second", "val*1000"],
        "StarDGEMM_Gflops": [
            "Average Double-Precision General Matrix Multiplication (DGEMM) Floating-Point Performance",
            "MFLOP per Second", "val*1000"],
        "StarSTREAM_Copy": ["Average STREAM 'Copy' Memory Bandwidth",
                            "MByte per Second", "val*1024"],
        "StarSTREAM_Scale": ["Average STREAM 'Scale' Memory Bandwidth",
                             "MByte per Second", "val*1024"],
        "StarSTREAM_Add": ["Average STREAM 'Add' Memory Bandwidth",
                           "MByte per Second", "val*1024"],
        "StarSTREAM_Triad": ["Average STREAM 'Triad' Memory Bandwidth",
                             "MByte per Second", "val*1024"]
    }

    # read output
    lines = []
    if os.path.isfile(appstdout):
        fin = open(appstdout, "rt")
        lines = fin.readlines()
        fin.close()

    # process the output
    parser.successfulRun = False
    result_begin = None
    hpl_tflops = None
    num_cores = None

    values = {}
    j = -1
    while j < len(lines) - 1:
        j += 1
        m = re.search(r'End of HPC Challenge tests', lines[j])
        if m:
            parser.successfulRun = True

        m = re.match(r'^Begin of Summary section', lines[j])
        if m:
            result_begin = 1
            continue

        m = re.match(r'^(\w+)=([\w.]+)', lines[j])
        if m and result_begin:
            metric_name = m.group(1).strip()
            values[metric_name] = m.group(2).strip()
            if metric_name == "HPL_Tflops":
                hpl_tflops = float(values[metric_name])
            if metric_name == "CommWorldProcs":
                num_cores = int(values[metric_name])
        m = re.match(r'^Running on ([0-9.]+) processors', lines[j])
        if m:
            num_cores = int(m.group(1).strip())

    if hpl_tflops is None or num_cores is None:
        parser.successfulRun = False

    hpcc_version = None
    mhz = None
    theoretical_gflops = None

    if "VersionMajor" in values and "VersionMinor" in values and "VersionMicro" in values:
        hpcc_version = values["VersionMajor"] + "." + values["VersionMinor"] + "." + values["VersionMicro"]
    if "VersionRelease" in values:
        hpcc_version += values["VersionRelease"]
    if hpcc_version:
        parser.set_parameter("App:Version", hpcc_version)

    for k, v in params.items():
        if k not in values:
            continue
        val = values[k]
        if v[2].find('val') >= 0:
            # if convertion formula is used, then first set val variable and then eval the formula
            val = get_float_or_int(values[k])
            val = eval(v[2])
        units = v[1] if [1] != "" else None
        parser.set_parameter("Input:" + v[0], val, units)

    for k, v in metrics.items():
        if k not in values:
            continue
        val = values[k]
        if v[2].find('val') >= 0:
            # if convertion formula is used, then first set val variable and then eval the formula
            val = get_float_or_int(values[k])
            val = eval(v[2])
        units = v[1] if [1] != "" else None
        parser.set_statistic(v[0], val, units)

    if "cpu_speed" in parser.geninfo:
        ll = parser.geninfo["cpu_speed"].splitlines()
        cpu_speed_max = 0.0
        for l in ll:
            m = re.search(r'([\d.]+)$', l)
            if m:
                v = float(m.group(1).strip())
                if v > cpu_speed_max:
                    cpu_speed_max = v
        if cpu_speed_max > 0.0:
            parser.set_parameter("RunEnv:CPU Speed", cpu_speed_max, "MHz")
            mhz = cpu_speed_max

    if resource_appker_vars is not None:
        if 'resource' in resource_appker_vars and 'app' in resource_appker_vars:
            resname = resource_appker_vars['resource']['name']
            if num_cores is None:
                num_cores = resource_appker_vars['resource']['nnodes']*resource_appker_vars['resource']['ppn']

            theoretical_gflops_per_core = None
            if "appkernel_on_resource" in resource_appker_vars['app'] and \
                    resname in resource_appker_vars['app']["appkernel_on_resource"] and \
                    'theoretical_gflops_per_core' in resource_appker_vars['app']["appkernel_on_resource"][resname]:
                theoretical_gflops_per_core = \
                    resource_appker_vars['app']["appkernel_on_resource"][resname]["theoretical_gflops_per_core"]

            # @todo theoreticalGFlopsPerCore should be deprecated
            if theoretical_gflops_per_core is None and 'theoreticalGFlopsPerCore' in resource_appker_vars['app']:
                resname = resource_appker_vars['resource']['name']
                if resname in resource_appker_vars['app']['theoreticalGFlopsPerCore']:
                    theoretical_gflops_per_core = resource_appker_vars['app']['theoreticalGFlopsPerCore'][resname]
            if theoretical_gflops_per_core is None:
                theoretical_gflops = theoretical_gflops_per_core * num_cores
                log.debug("Theoretical GFLOPS for %s is %f", resname, theoretical_gflops)

    if theoretical_gflops and hpl_tflops:
        # Convert both to GFlops and derive the Efficiency
        percent = (1000.0 * hpl_tflops / theoretical_gflops) * 100.0
        parser.set_statistic("High Performance LINPACK Efficiency", "%.3f" % percent, "Percent")

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
