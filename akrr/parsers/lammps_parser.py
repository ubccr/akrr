import re
import os
import sys
from akrr.parsers.akrrappkeroutputparser import AppKerOutputParser


def process_appker_output(appstdout=None, stdout=None, stderr=None, geninfo=None, proclog=None, 
                          resource_appker_vars=None):
    # set App Kernel Description
    parser = AppKerOutputParser(
        name='lammps',
        version=1,
        description="LAMMPS: Large-scale Atomic/Molecular Massively Parallel Simulator",
        url='http://lammps.sandia.gov',
        measurement_name='LAMMPS'
    )
    # set obligatory parameters and statistics
    # set common parameters and statistics
    parser.add_common_must_have_params_and_stats()
    # set app kernel custom sets
    parser.add_must_have_parameter('App:Version')
    parser.add_must_have_parameter('Input:Number of Atoms')
    parser.add_must_have_parameter('Input:Number of Steps')
    parser.add_must_have_parameter('Input:Timestep')

    parser.add_must_have_statistic('Molecular Dynamics Simulation Performance')
    parser.add_must_have_statistic('Per-Process Memory')
    parser.add_must_have_statistic('Time Spent in Bond Potential Calculation')
    parser.add_must_have_statistic('Time Spent in Communication')
    parser.add_must_have_statistic('Time Spent in Long-Range Coulomb Potential (K-Space) Calculation')
    parser.add_must_have_statistic('Time Spent in Neighbor List Regeneration')
    parser.add_must_have_statistic('Time Spent in Pairwise Potential Calculation')
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
    wall_clock_time = None
    simulation_units = None
    num_steps = None
    step_size = None
    j = 0
    while j < len(lines):

        m = re.match(r'^LAMMPS\s+\(([\w ]+)\)', lines[j])
        if m:
            parser.set_parameter("App:Version", m.group(1).strip())

        m = re.match(r'^Memory usage per processor = ([\d.]+) Mbyte', lines[j])
        if m:
            parser.set_statistic("Per-Process Memory", m.group(1).strip(), "MByte")

        m = re.match(r'^Loop time of ([\d.]+) on', lines[j])
        if m:
            parser.successfulRun = True
            wall_clock_time = float(m.group(1).strip())
            parser.set_statistic("Wall Clock Time", wall_clock_time, "Second")
            m1 = re.search(r'(\d+) atoms', lines[j])
            if m1:
                parser.set_parameter("Input:Number of Atoms", m1.group(1).strip())

        m = re.match(r'^units\s+(\w+)', lines[j])
        if m:
            simulation_units = m.group(1).strip().lower()

        m = re.match(r'^run\s+(\d+)', lines[j])
        if m:
            num_steps = int(m.group(1).strip())
            parser.set_parameter("Input:Number of Steps", num_steps)

        m = re.match(r'^timestep\s+([\d.]+)', lines[j])
        if m:
            step_size = float(m.group(1).strip())

        m = re.match(r'^Pair\s+time.+= ([\d.]+)', lines[j])
        if parser.successfulRun and m:
            parser.set_statistic("Time Spent in Pairwise Potential Calculation", m.group(1).strip(), "Second")

        m = re.match(r'^Bond\s+time.+= ([\d.]+)', lines[j])
        if parser.successfulRun and m:
            parser.set_statistic("Time Spent in Bond Potential Calculation", m.group(1).strip(), "Second")

        m = re.match(r'^Kspce\s+time.+= ([\d.]+)', lines[j])
        if parser.successfulRun and m:
            parser.set_statistic("Time Spent in Long-Range Coulomb Potential (K-Space) Calculation", m.group(1).strip(),
                                 "Second")

        m = re.match(r'^Neigh\s+time.+= ([\d.]+)', lines[j])
        if parser.successfulRun and m:
            parser.set_statistic("Time Spent in Neighbor List Regeneration", m.group(1).strip(), "Second")

        m = re.match(r'^Comm\s+time.+= ([\d.]+)', lines[j])
        if parser.successfulRun and m:
            parser.set_statistic("Time Spent in Communication", m.group(1).strip(), "Second")

        j += 1

    if parser.successfulRun and num_steps and simulation_units != "lj":
        # The default value for $stepSize is (see http://lammps.sandia.gov/doc/units.html):
        #
        #   0.005 tau for $simulationUnits eq "lj"
        #   1e-15 second for $simulationUnits eq "real" or "metal"
        #   1e-18 second for $simulationUnits eq "electron"
        #   1e-8  second for $simulationUnits eq "si" or "cgs"

        # If $simulationUnits is (see http://lammps.sandia.gov/doc/units.html)
        #
        #  "lj", the unit for $stepSize is tau
        #  "real" or "electron", the unit for $stepSize is 1e-15 second
        #  "metal", the unit for $stepSize is 1e-12 second
        #  "si" or "cgs", the unit for $stepSize is second

        # The default $simulationUnits is "lj"
        #
        # We ignore "lj" since "lj" is unitless.
        if step_size is None:
            if simulation_units == "real":
                step_size = 1.0
            if simulation_units.find("electron") >= 0 or simulation_units.find("metal") >= 0:
                step_size = 0.001
            if simulation_units.find("si") >= 0 or simulation_units.find("cgs") >= 0:
                step_size = 1.0e-8

        step_size_in_sec = step_size
        if step_size:
            if simulation_units.find("electron") >= 0 or simulation_units.find("real") >= 0:
                step_size_in_sec = step_size * 1.0e-15
            if simulation_units == "metal":
                step_size_in_sec = step_size * 1.0e-12
        if step_size_in_sec:
            parser.set_parameter("Input:Timestep", step_size_in_sec, "Second per Step")
            parser.set_statistic("Molecular Dynamics Simulation Performance",
                                 1.0e-9 * (1.0e9 * step_size_in_sec * num_steps) / (wall_clock_time / 86400.0),
                                 "Second per Day")
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
