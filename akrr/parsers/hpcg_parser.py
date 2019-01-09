# Part of XDMoD=>AKRR
# parser for HPCG Benchmarks AK
#
# authors: Trey Dockendorf
#

import re
import os
import sys
from akrr.parsers.akrrappkeroutputparser import AppKerOutputParser, total_seconds


def process_appker_output(appstdout=None, stdout=None, stderr=None, geninfo=None, resource_appker_vars=None):
    # set App Kernel Description
    parser = AppKerOutputParser(
        name='HPCG',
        version=1,
        description="HPCG Benchmark",
        url='http://www.hpcg-benchmark.org/index.html',
        measurement_name='xdmod.benchmark.hpcg'
    )
    # set obligatory parameters and statistics
    # set common parameters and statistics
    parser.add_common_must_have_params_and_stats()
    # set app kernel custom sets
    parser.add_must_have_parameter('App:Version')
    parser.add_must_have_parameter('Input:HPCG Local Domain Dimensions nx')
    parser.add_must_have_parameter('Input:HPCG Local Domain Dimensions ny')
    parser.add_must_have_parameter('Input:HPCG Local Domain Dimensions nz')
    parser.add_must_have_parameter('Input:Distributed Processes')
    parser.add_must_have_parameter('Input:Threads per processes')
    parser.add_must_have_parameter('RunEnv:CPU Speed')
    parser.add_must_have_parameter('RunEnv:Nodes')
    
    parser.add_must_have_statistic('MFLOPS rating')
    parser.add_must_have_statistic('Wall Clock Time')
    # parse common parameters and statistics
    parser.parse_common_params_and_stats(appstdout, stdout, stderr, geninfo, resource_appker_vars)
    
    if hasattr(parser, 'appKerWallClockTime'):
        parser.set_statistic("Wall Clock Time", total_seconds(parser.appKerWallClockTime), "Second")
    
    # The parameters mapping table
    params = {
        "App:Version": ["^.*version$", "", "", True],
        "Input:HPCG Local Domain Dimensions nx": ['nx', "", "", False],
        "Input:HPCG Local Domain Dimensions ny": ['ny', "", "", False],
        "Input:HPCG Local Domain Dimensions nz": ['nz', "", "", False],
        "Input:Distributed Processes": ["Distributed Processes", "", "", False],
        "Input:Threads per processes": ["Threads per processes", "", "", False],
    }
    
    # The result mapping table
    metrics = {
        "MFLOPS rating": ["HPCG result is VALID with a GFLOP/s rating of", "MFLOP per Second", "val*1e3", False],
    }

    # get path to YAML file
    jobdir = os.path.dirname(appstdout)
    yamlfile = os.path.join(jobdir, "HPCG-Benchmark.yaml")

    # read data
    # Parse YAML lines because YAML is often malformed
    lines = {}
    with open(yamlfile, 'r') as f:
        for line in f.readlines():
            line_stripped = line.strip()
            m = re.search(r'^(\s+)?([^:]+):(\s)?(.*)$', line_stripped)
            key = m.group(2)
            value = m.group(4)
            lines[key] = value
    
    # process the data
    for k, v in params:
        val = lines.get(v[0], None)
        if v[3]:
            for line in lines:
                if re.match(v[0], line):
                    val = lines[line]
                    break
        if v[2].find('val') >= 0:
            val = eval(v[2])
        if v[1] == "":
            v[1] = None
        if val is None:
            continue
        parser.set_parameter(k, val, v[1])
    
    for k, v in metrics:
        val = lines.get(v[0], None)
        if v[3]:
            for line in lines:
                if re.match(v[0], line):
                    val = lines[line]
                    break
        if v[2].find('val') >= 0:
            val = eval(v[2])
        if v[1] == "":
            v[1] = None
        if val is None:
            continue
        parser.set_statistic(k, val, v[1])
    
    if "cpuSpeed" in parser.geninfo:
        ll = parser.geninfo["cpuSpeed"].splitlines()
        cpu_speed_max = 0.0
        for l in ll:
            m = re.search(r'([\d.]+)$', l)
            if m:
                v = float(m.group(1).strip())
                if v > cpu_speed_max:
                    cpu_speed_max = v
        if cpu_speed_max > 0.0:
            parser.set_parameter("RunEnv:CPU Speed", cpu_speed_max, "MHz")
    
    if __name__ == "__main__":
        # output for testing purpose
        print("parsing complete:", parser.parsing_complete(verbose=True))
        parser.print_params_stats_as_must_have()
        print(parser.get_xml())
    
    # return complete XML otherwise return None
    return parser.get_xml()
    
    
if __name__ == "__main__":
    """stand alone testing"""
    job_dir = sys.argv[1]
    print("Processing Output From", job_dir)
    process_appker_output(appstdout=os.path.join(job_dir, "appstdout"), geninfo=os.path.join(job_dir, "gen.info"))
