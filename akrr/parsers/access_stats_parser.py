import os
import sys
import re
import datetime
from akrr.parsers.akrrappkeroutputparser import AppKerOutputParser, total_seconds


def process_appker_output(appstdout=None, stdout=None, stderr=None, geninfo=None, proclog=None,
                          resource_appker_vars=None):
    """
    Process test appkernel output.
    """
    # set App Kernel Description
    parser = AppKerOutputParser(
        name='test',
        version=1,
        description="Test the resource deployment",
        url='http://xdmod.buffalo.edu',
        measurement_name='test'
    )
    # set obligatory parameters and statistics
    # set common parameters and statistics
    parser.add_common_must_have_params_and_stats()
    # set app kernel custom sets
    # parser.add_must_have_statistic('Wall Clock Time')
    # parser.add_must_have_statistic('Shell is BASH')

    # parse common parameters and statistics
    parser.parse_common_params_and_stats(appstdout, stdout, stderr, geninfo, resource_appker_vars)

    # set statistics
    if parser.wallClockTime is not None:
        parser.set_statistic("Wall Clock Time", total_seconds(parser.wallClockTime), "Second")

    # read output
    lines = []
    if os.path.isfile(stdout):
        fin = open(stdout, "rt")
        lines = fin.readlines()
        fin.close()

    # process the output
    parser.set_statistic('Shell is BASH', 0)
    j = 0
    while j < len(lines):
        if lines[j].count("Checking that the shell is BASH") > 0 and lines[j + 1].count("bash") > 0:
            parser.set_statistic('Shell is BASH', 1)
        j += 1

    # process proc log
    if proclog is not None:
        os_start = None
        os_first_login = None
        os_start_shutdown = None
        os_terminated = None
        with open(proclog, "rt") as fin:
            for line in fin:
                m = re.search("Starting OpenStack instance \(([0-9]+)-([0-9]+)-([0-9]+) ([0-9]+):([0-9]+):([0-9]+)\)",
                              line)
                if m:
                    os_start = datetime.datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)),
                                                 int(m.group(4)), int(m.group(5)), int(m.group(6)))
                m = re.search("OpenStack Instance should be up and running \(([0-9]+)-([0-9]+)-([0-9]+) ([0-9]+):([0-9]+):([0-9]+)\)",
                              line)
                if m:
                    os_first_login = datetime.datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)),
                                                 int(m.group(4)), int(m.group(5)), int(m.group(6)))
                m = re.search("Shutting down OpenStack instance \(([0-9]+)-([0-9]+)-([0-9]+) ([0-9]+):([0-9]+):([0-9]+)\)",
                              line)
                if m:
                    os_start_shutdown = datetime.datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)),
                                                 int(m.group(4)), int(m.group(5)), int(m.group(6)))
                m = re.search("OpenStack Instance should be down and terminated \(([0-9]+)-([0-9]+)-([0-9]+) ([0-9]+):([0-9]+):([0-9]+)\)",
                              line)
                if m:
                    os_terminated = datetime.datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)),
                                                 int(m.group(4)), int(m.group(5)), int(m.group(6)))
        if os_start is not None and os_first_login is not None:
            parser.set_statistic('Cloud Instance, Start Time to Login', total_seconds(os_first_login-os_start))
        if os_start_shutdown is not None and os_terminated is not None:
            parser.set_statistic('Cloud Instance, Shut Down Time', total_seconds(os_terminated-os_start_shutdown))
        # log.info("OpenStack Instance should be up and running  (%s)"
        # log.info("Shutting down OpenStack instance (%s)" % datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S"))
        # log.info("OpenStack Instance should be down and terminated (%s)"

    if __name__ == "__main__":
        # output for testing purpose
        print(("parsing complete:", parser.parsing_complete()))
        parser.print_params_stats_as_must_have()
        print((parser.get_xml()))

    # return complete XML otherwise return None
    return parser.get_xml()


if __name__ == "__main__":
    """stand alone testing"""
    jobdir = sys.argv[1]
    print(("Processing Output From", jobdir))
    process_appker_output(appstdout=os.path.join(jobdir, "appstdout"),
                          stdout=os.path.join(jobdir, "stdout"),
                          stderr=os.path.join(jobdir, "stderr"),
                          geninfo=os.path.join(jobdir, "gen.info"),
                          proclog=os.path.join(os.path.dirname(jobdir), 'proc', "log"))
