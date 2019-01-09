import re
import os
import sys
from akrr.parsers.akrrappkeroutputparser import AppKerOutputParser


def process_appker_output(appstdout=None, stdout=None, stderr=None, geninfo=None, resource_appker_vars=None):
    # set App Kernel Description
    parser = AppKerOutputParser(
        name='xdmod.app.md.charmm',
        version=1,
        description="CHARMM: Chemistry at Harvard Macromolecular Mechanics",
        url='http://www.charmm.org',
        measurement_name='CHARMM'
    )
    # set obligatory parameters and statistics
    # set common parameters and statistics
    parser.add_common_must_have_params_and_stats()
    # set app kernel custom sets
    parser.add_must_have_parameter('App:Version')
    parser.add_must_have_parameter('Input:Number of Angles')
    parser.add_must_have_parameter('Input:Number of Atoms')
    parser.add_must_have_parameter('Input:Number of Bonds')
    parser.add_must_have_parameter('Input:Number of Dihedrals')
    parser.add_must_have_parameter('Input:Number of Steps')
    parser.add_must_have_parameter('Input:Timestep')

    parser.add_must_have_statistic('Molecular Dynamics Simulation Performance')
    parser.add_must_have_statistic('Time Spent in External Energy Calculation')
    parser.add_must_have_statistic('Time Spent in Integration')
    parser.add_must_have_statistic('Time Spent in Internal Energy Calculation')
    parser.add_must_have_statistic('Time Spent in Non-Bond List Generation')
    parser.add_must_have_statistic('Time Spent in Waiting (Load Unbalance-ness)')
    parser.add_must_have_statistic('User Time')
    parser.add_must_have_statistic('Wall Clock Time')

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
    wall_clock_time = 0.0
    num_steps = 0
    step_size = 0.0
    time_breakdown_columns = None
    num_atoms = 0
    num_bonds = 0
    num_angles = 0
    num_dihedrals = 0

    j = 0
    while j < len(lines):

        m0 = re.search(r'\s+Chemistry at HARvard Macromolecular Mechanics', lines[j])
        m1 = re.search(r'\sVersion\s+([\da-zA-Z]+)', lines[j + 1])
        if m0 and m1:
            parser.set_parameter("App:Version", m1.group(1).strip())

        if re.search(r'Summary of the structure file counters', lines[j]):
            j += 1
            for k in range(256):
                if re.search(r'CHARMM>', lines[j]):
                    break

                m = re.search(r'Number of atoms\s+=\s+(\d+)', lines[j])
                if m:
                    num_atoms += int(m.group(1).strip())

                m = re.search(r'Number of bonds\s+=\s+(\d+)', lines[j])
                if m:
                    num_bonds += int(m.group(1).strip())

                m = re.search(r'Number of angles\s+=\s+(\d+)', lines[j])
                if m:
                    num_angles += int(m.group(1).strip())

                m = re.search(r'Number of dihedrals\s+=\s+(\d+)', lines[j])
                if m:
                    num_dihedrals += int(m.group(1).strip())

                j += 1

        if re.search(r'<MAKGRP> found', lines[j]):
            j += 1
            for k in range(256):
                if re.search(r'NUMBER OF DEGREES OF FREEDOM', lines[j]):
                    break

                m = re.search(r'NSTEP\s+=\s+(\d+)', lines[j])
                if m:
                    num_steps = int(m.group(1).strip())
                    parser.set_parameter("Input:Number of Steps", num_steps)

                if re.search(r'TIME STEP\s+=', lines[j]):
                    m = re.search(r'([\d\-Ee.]+)\s+PS', lines[j])
                    if m:
                        step_size = 1000.0 * float(m.group(1).strip())
                        parser.set_parameter("Input:Timestep", step_size * 1e-15, "Second per Step")
                j += 1

        if re.search(r'NORMAL TERMINATION BY NORMAL STOP', lines[j]):
            parser.successfulRun = True

        if re.search(r'JOB ACCOUNTING INFORMATION', lines[j]):
            parser.successfulRun = True

            j += 1
            for k in range(256):
                if j > len(lines) - 1:
                    break
                m = re.search(r'ELAPSED TIME:\s*([\d.]+)\s*MINUTES', lines[j])
                if m:
                    wall_clock_time = 60.0 * float(m.group(1).strip())
                    parser.set_statistic("Wall Clock Time", wall_clock_time, "Second")

                m = re.search(r'CPU TIME:\s*([\d.]+)\s*MINUTES', lines[j])
                if m:
                    parser.set_statistic("User Time", 60.0 * float(m.group(1).strip()), "Second")

                m = re.search(r'ELAPSED TIME:\s*([\d.]+)\s*SECONDS', lines[j])
                if m:
                    wall_clock_time = float(m.group(1).strip())
                    parser.set_statistic("Wall Clock Time", wall_clock_time, "Second")

                m = re.search(r'CPU TIME:\s*([\d.]+)\s*SECONDS', lines[j])
                if m:
                    parser.set_statistic("User Time", m.group(1).strip(), "Second")

                j += 1
            if j > len(lines) - 1:
                break

        if re.search(r'Parallel load balance \(sec', lines[j]):
            j += 1
            # grab the column headers from the output, e.g.
            #
            # Parallel load balance (sec.):
            # Node Eext      Eint   Wait    Comm    List   Integ   Total
            #   0   205.5     6.4     1.2    31.2    23.2     2.8   270.4
            #   1   205.2     7.3     1.1    31.2    23.3     3.2   271.2
            #   2   205.2     7.7     0.6    32.3    23.3     3.2   272.3
            #   3   205.2     7.8     0.6    32.1    23.3     3.3   272.3
            # PARALLEL> Average timing for all nodes:
            #   4   205.3     7.3     0.9    31.7    23.3     3.1   271.6
            time_breakdown_columns = lines[j].strip().split()

        if re.search(r'PARALLEL>\s*Average timing for all nodes', lines[j]) and time_breakdown_columns:
            j += 1
            time_breakdown = lines[j].strip().split()
            if len(time_breakdown_columns) == len(time_breakdown):
                for k in range(len(time_breakdown)):
                    if time_breakdown_columns[k] == "Eext":
                        parser.set_statistic("Time Spent in External Energy Calculation", time_breakdown[k], "Second")
                    if time_breakdown_columns[k] == "Eint":
                        parser.set_statistic("Time Spent in Internal Energy Calculation", time_breakdown[k], "Second")
                    if time_breakdown_columns[k] == "Wait":
                        parser.set_statistic("Time Spent in Waiting (Load Unbalance-ness)", time_breakdown[k], "Second")
                    if time_breakdown_columns[k] == "List":
                        parser.set_statistic("Time Spent in Non-Bond List Generation", time_breakdown[k], "Second")
                    if time_breakdown_columns[k] == "Integ":
                        parser.set_statistic("Time Spent in Integration", time_breakdown[k], "Second")

        j += 1
    if num_atoms > 0:
        parser.set_parameter("Input:Number of Atoms", num_atoms)
    if num_bonds > 0:
        parser.set_parameter("Input:Number of Bonds", num_bonds)
    if num_angles > 0:
        parser.set_parameter("Input:Number of Angles", num_angles)
    if num_dihedrals > 0:
        parser.set_parameter("Input:Number of Dihedrals", num_dihedrals)

    if wall_clock_time > 0.0 and num_steps > 0 and step_size > 0.0:
        # $stepSize is in femtoseconds
        # $wallClockTime is in seconds
        parser.set_statistic("Molecular Dynamics Simulation Performance",
                             (1e-6 * step_size * num_steps) / (wall_clock_time / 86400.0) * 1e-9, "Second per Day")

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
    print("Proccessing Output From", jobdir)
    process_appker_output(appstdout=os.path.join(jobdir, "appstdout"), geninfo=os.path.join(jobdir, "gen.info"))
