import re
import os
import sys
from akrr.parsers.akrrappkeroutputparser import AppKerOutputParser, total_seconds


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

    if parser.appKerWallClockTime is not None:
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
    def process_subtest(test_name):
        m = re.match(r'\d+/\d+\.\s+'+test_name, lines[j])
        if m:
            print("DSF")

    while j < len(lines):
        # Global parameters
        parser.match_set_parameter("App:Version", r'>>   AI-Benchmark-v\.(.+)$', lines[j])
        parser.match_set_parameter("TF Version", r'\*  TF Version: (.+)$', lines[j])
        parser.match_set_parameter("Platform", r'\*  Platform: (.+)$', lines[j])
        parser.match_set_parameter("CPU", r'\*  CPU: (.+)$', lines[j])
        parser.match_set_parameter("CPU RAM", r'\*  CPU RAM: (.+)$', lines[j])
        parser.match_set_parameter("GPU", r'\*  GPU/0: (.+)$', lines[j])
        parser.match_set_parameter("GPU RAM", r'\*  GPU RAM: (.+)$', lines[j])

        # Summary statistics
        parser.match_set_statistic("Inference Score", r'Device Inference Score: ([0-9.]+)$', lines[j])
        parser.match_set_statistic("Training Score", r'Device Training Score: ([0-9.]+)$', lines[j])
        parser.match_set_statistic("AI Score", r'Device AI Score: ([0-9.]+)$', lines[j])

        m = re.match(r'^For more information and results', lines[j])
        if m:
            successful_run = True

        # detailed metrics
        m_subtest = re.match(r'\d+/\d+[.]\s+(\S+)', lines[j])
        if m_subtest :
            for k in range(2,6):
                if j + k >= len(lines):
                    break
                m_subtest2 = re.match(r'\d+.\d+ - (inference|training)\s+[|] batch=(\d+), (size=\S+): (\d+) ± (\d+) ms', lines[j+k])
                if m_subtest2:
                    parser.set_statistic(f"{m_subtest.group(1)}, {m_subtest2.group(1)}, {m_subtest2.group(3)}",
                                         {'mean': int(m_subtest2.group(4)), 'stdev': int(m_subtest2.group(5)), 'n': int(m_subtest2.group(2))},
                                         units="ms", group="details")
                else:
                    break

        j += 1

    parser.successfulRun = successful_run
    # return
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
