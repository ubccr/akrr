import re
import os
import sys

# Set proper path for stand alone test runs
if __name__ == "__main__":
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../..'))


from akrr.appkernelsparsers.akrrappkeroutputparser import AppKerOutputParser


def processAppKerOutput(appstdout=None, stdout=None, stderr=None, geninfo=None, appKerNResVars=None):
    # set App Kernel Description
    parser = AppKerOutputParser(
        name='xdmod.app.md.gromacs.micro',
        version=1,
        description="GROMACS: micro-benchmark for testing purposes",
        url='http://www.gromacs.org/',
        measurement_name='GROMACS-Micro'
    )
    # set obligatory parameters and statistics
    # set common parameters and statistics
    parser.setCommonMustHaveParsAndStats()
    # set app kernel custom sets
    parser.setMustHaveParameter('App:Version')

    parser.setMustHaveStatistic('Simulation Speed')
    parser.setMustHaveStatistic('Wall Clock Time')

    # parse common parameters and statistics
    parser.parseCommonParsAndStats(appstdout, stdout, stderr, geninfo)

    # read output
    lines = []
    if os.path.isfile(appstdout):
        print("HHHH")
        fin = open(appstdout, "rt")
        lines = fin.readlines()
        fin.close()
    print(appstdout)


    # process the output
    successfulRun = False
    j = 0
    while j < len(lines):
        print(lines[j])
        m = re.search(r'^GROMACS:\s+ gmx mdrun, version\s+(\S+)$', lines[j])
        if m:
            parser.setParameter("App:Version",m.group(1))

        m = re.search(r'^Performance:  \s+([0-9.]+)', lines[j])
        if m:
            parser.setStatistic("Simulation Speed", float(m.group(1)), "ns/day")

        m = re.search(r'^ \s+Time:  \s+([0-9.]+) \s+([0-9.]+)', lines[j])
        if m:
            parser.setStatistic("Wall Clock Time", m.group(2), "Second")
            parser.setStatistic("Core Clock Time", m.group(1), "Second")

        m = re.match(r'^GROMACS reminds you', lines[j])
        if m:
            successfulRun = True

        j += 1

    if __name__ == "__main__":
        # output for testing purpose
        print("parsing complete:", parser.parsingComplete())
        parser.printParsNStatsAsMustHave()
        print(parser.getXML())

    # return complete XML overwize return None
    return parser.getXML()


if __name__ == "__main__":
    """stand alone testing"""
    jobdir = sys.argv[1]
    print("Proccessing Output From", jobdir)
    processAppKerOutput(appstdout=os.path.join(jobdir, "appstdout"), geninfo=os.path.join(jobdir, "gen.info"))
