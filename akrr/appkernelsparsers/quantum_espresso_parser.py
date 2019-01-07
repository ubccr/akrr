import re
import os
import sys
from akrr.appkernelsparsers.akrrappkeroutputparser import AppKerOutputParser


def process_appker_output(appstdout=None, stdout=None, stderr=None, geninfo=None, resource_appker_vars=None):
    # set App Kernel Description
    parser = AppKerOutputParser(
        name='xdmod.app.phys.quantum_espresso',
        version=1,
        description="Quantum ESPRESSO (PWSCF)",
        url='http://www.quantum-espresso.org',
        measurement_name='Quantum_ESPRESSO'
    )
    # set obligatory parameters and statistics
    # set common parameters and statistics
    parser.add_common_must_have_params_and_stats()
    # set app kernel custom sets
    parser.add_must_have_parameter('App:Version')
    parser.add_must_have_parameter('Input:Number of Atoms per Cell')
    parser.add_must_have_parameter('Input:Number of Atomic Types')
    parser.add_must_have_parameter('Input:Number of Electrons')

    parser.add_must_have_statistic('Wall Clock Time')
    parser.add_must_have_statistic('User Time')
    parser.add_must_have_statistic("Per-Process Dynamical Memory")
    parser.add_must_have_statistic("Time Spent in Program Initialization")
    parser.add_must_have_statistic("Time Spent in Electron Energy Calculation")
    parser.add_must_have_statistic("Time Spent in Force Calculation")
    # This statistic probably was working for a different set of inputs, optional now
    # parser.add_must_have_statistic("Time Spent in Stress Calculation")
    # This statistic probably was working for a different set of inputs, optional now
    # parser.add_must_have_statistic("Time Spent in Potential Updates "\
    # "(Charge Density and Wavefunctions Extrapolations)")

    # parse common parameters and statistics
    parser.parse_common_params_and_stats(appstdout, stdout, stderr, geninfo, resource_appker_vars)

    # read output
    lines = []
    if os.path.isfile(appstdout):
        fin = open(appstdout, "rt")
        lines = fin.readlines()
        fin.close()

    # process the output
    parser.successfulRun = False
    j = 0
    while j < len(lines):

        m = re.match(r'^\s+Program PWSCF\s+([\w.]+)\s+starts', lines[j])
        if m:
            parser.set_parameter("App:Version", m.group(1).strip())

        m = re.match(r'^\s+number of atoms/cell\s*=\s*([\d.]+)', lines[j])
        if m:
            parser.set_parameter("Input:Number of Atoms per Cell", m.group(1).strip())

        m = re.match(r'^\s+number of atomic types\s*=\s*([\d.]+)', lines[j])
        if m:
            parser.set_parameter("Input:Number of Atomic Types", m.group(1).strip())

        m = re.match(r'^\s+number of electrons\s*=\s*([\d.]+)', lines[j])
        if m:
            parser.set_parameter("Input:Number of Electrons", m.group(1).strip())

        m = re.match(r'^\s+per-process dynamical memory:\s*([\d.]+)\s*Mb', lines[j])
        if m:
            parser.set_statistic("Per-Process Dynamical Memory", (m.group(1).strip()), "MByte")

        m = re.match(r'^\s+init_run\s+:\s*([\d.]+)s CPU', lines[j])
        if m:
            parser.set_statistic("Time Spent in Program Initialization", (m.group(1).strip()), "Second")

        m = re.match(r'^\s+electrons\s+:\s*([\d.]+)s CPU', lines[j])
        if m:
            parser.set_statistic("Time Spent in Electron Energy Calculation", (m.group(1).strip()), "Second")

        m = re.match(r'^\s+forces\s+:\s*([\d.]+)s CPU', lines[j])
        if m:
            parser.set_statistic("Time Spent in Force Calculation", (m.group(1).strip()), "Second")

        m = re.match(r'^\s+stress\s+:\s*([\d.]+)s CPU', lines[j])
        if m:
            parser.set_statistic("Time Spent in Stress Calculation", (m.group(1).strip()), "Second")

        m = re.match(r'^\s+update_pot\s+:\s*([\d.]+)s CPU', lines[j])
        if m:
            parser.set_statistic("Time Spent in Potential Updates (Charge Density and Wavefunctions Extrapolations)",
                                 float(m.group(1).strip()), "Second")

        m = re.match(r'^\s+PWSCF\s+:(.+CPU.+)', lines[j])
        if m:
            run_times = m.group(1).strip().split(',')
            for run_time in run_times:
                v = run_time.split()
                if len(v) > 1:
                    if v[0].lower().find("m") >= 0:
                        m = re.match(r'^([0-9]+)m([0-9.]+)s', v[0])
                        sec = float(m.group(1)) * 60.0 + float(m.group(2))
                    else:
                        m = re.match(r'^([0-9.]+)s', v[0])
                        sec = float(m.group(1))
                    if v[1].upper().find("CPU") >= 0:
                        parser.set_statistic("User Time", sec, "Second")
                    if v[1].upper().find("WALL") >= 0:
                        parser.set_statistic("Wall Clock Time", sec, "Second")

        if re.match(r'^\s+JOB DONE', lines[j]):
            parser.successfulRun = True
        j += 1
    if __name__ == "__main__":
        # output for testing purpose
        print("parsing complete:", parser.parsing_complete(True))
        if hasattr(parser, 'successfulRun'):
            print("successfulRun", parser.successfulRun)
        parser.print_params_stats_as_must_have()
        print(parser.get_xml())

    # return complete XML overwize return None
    return parser.get_xml()


if __name__ == "__main__":
    """stand alone testing"""
    jobdir = sys.argv[1]
    print("Proccessing Output From", jobdir)
    process_appker_output(appstdout=os.path.join(jobdir, "appstdout"), geninfo=os.path.join(jobdir, "gen.info"))
