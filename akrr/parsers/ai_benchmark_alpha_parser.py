import re
import os
import sys
from akrr.parsers.akrrappkeroutputparser import AppKerOutputParser


def process_appker_output(appstdout=None, stdout=None, stderr=None, geninfo=None, proclog=None,
                          resource_appker_vars=None):
    # set App Kernel Description
    parser = AppKerOutputParser(
        name='ai_benchmark_alpha',
        version=1,
        description="AI-Benchmark-Alpha",
        url='http://ai-benchmark.com/alpha',
        measurement_name='ai_benchmark_alpha'
    )
    # set obligatory parameters and statistics
    # set common parameters and statistics
    parser.add_common_must_have_params_and_stats()
    # set app kernel custom sets
    parser.add_must_have_parameter('App:Version')
    parser.add_must_have_statistic('Wall Clock Time')
    parser.add_must_have_statistic('AI Score')
    parser.add_must_have_statistic('Inference Score')
    parser.add_must_have_statistic('Training Score')

    # parse common parameters and statistics
    parser.parse_common_params_and_stats(appstdout, stdout, stderr, geninfo, resource_appker_vars)

    # read output
    lines = []
    if os.path.isfile(appstdout):
        fin = open(appstdout, "rt")
        lines = fin.readlines()
        fin.close()

    # process the output
    successful_run = False
    j = 0
    while j < len(lines):

        parser.match_set_parameter("App:Version", r'>>   AI-Benchmark-v\.(.+)$', lines[j])
        parser.match_set_parameter("TF Version", r'\*  TF Version: (.+)$', lines[j])

        parser.match_set_statistic("Inference Score", r'Device Inference Score: ([0-9.]+)$', lines[j])
        parser.match_set_statistic("Training Score", r'Device Training Score: ([0-9.]+)$', lines[j])
        parser.match_set_statistic("AI Score", r'Device AI Score: ([0-9.]+)$', lines[j])

        m = re.match(r'^For more information and results', lines[j])
        if m:
            successful_run = True

        j += 1

    parser.successfulRun = successful_run

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
