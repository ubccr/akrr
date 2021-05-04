import re
import os
import sys
import json
from akrr.parsers.akrrappkeroutputparser import AppKerOutputParser, total_seconds


def process_appker_output(appstdout=None, stdout=None, stderr=None, geninfo=None, proclog=None, 
                          resource_appker_vars=None):
    # set App Kernel Description
    parser = AppKerOutputParser(
        name='akrr network check',
        version=1,
        description="network benchmarking",
        url='http://www.xdmod.org',
        measurement_name='akrr network check'
    )
    # set obligatory parameters and statistics
    # set common parameters and statistics
    parser.add_must_have_parameter('App:ExeBinSignature')
    parser.add_must_have_statistic('Ping, Mean')
    parser.add_must_have_statistic('Secure Copy Bandwidth (in), Mean')
    parser.add_must_have_statistic('Secure Copy Bandwidth (out), Mean')
    parser.add_must_have_statistic('WGet Bandwidth, Mean')
    parser.add_must_have_statistic('Wall Clock Time')

    # set app kernel custom sets
    parser.add_must_have_statistic('Wall Clock Time')

    # parse common parameters and statistics
    parser.parse_common_params_and_stats(appstdout, stdout, stderr, geninfo, resource_appker_vars)

    if hasattr(parser, 'wallClockTime') and parser.wallClockTime is not None:
        parser.set_statistic("Wall Clock Time", total_seconds(parser.wallClockTime), "Second")
    if hasattr(parser, 'appKerWallClockTime') and parser.appKerWallClockTime is not None:
        parser.set_statistic("Wall Clock Time", total_seconds(parser.appKerWallClockTime), "Second")

    # read output
    lines = []
    if os.path.isfile(appstdout):
        fin = open(appstdout, "rt")
        lines = fin.readlines()
        fin.close()

    # process the output
    successful_run = False
    j = 0

    start = None
    while j < len(lines):
        if lines[j].strip() == "AKRR Network Check Results:":
            start = j
        if lines[j].strip() == "Done":
            end = j
        j += 1

    if start is not None and end is not None:
        r = json.loads(" ".join(lines[(start+1):end]))
        successful_run = True
        if 'ping' in r:
            count = 0
            ping = 0.0
            for k,v in r['ping'].items():
                if v is None:
                    successful_run = False
                else:
                    ping += float(v['rtt_avg'])
                    count +=1
            parser.set_statistic("Ping, Mean", ping/count, "ms")
        if 'wget' in r:
            count = 0
            val = 0.0
            for k,v in r['wget'].items():
                if v is None:
                    successful_run = False
                else:
                    val += float(v['bandwidth'])
                    count +=1
            parser.set_statistic("WGet Bandwidth, Mean", val/count, "MB/s")
        if 'scp' in r:
            count = 0
            val_in = 0.0
            val_out = 0.0
            for k,v in r['scp'].items():
                if v is None:
                    successful_run = False
                else:
                    val_in += float(v['bandwidth_ingress'])
                    val_out += float(v['bandwidth_egress'])
                    count +=1
            parser.set_statistic("Secure Copy Bandwidth (in), Mean", val_in / count, "MB/s")
            parser.set_statistic("Secure Copy Bandwidth (out), Mean", val_out / count, "MB/s")


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
