import re
import os
import sys
from akrr.appkernelsparsers.akrrappkeroutputparser import AppKerOutputParser


def process_appker_output(appstdout=None, stdout=None, stderr=None, geninfo=None, resource_appker_vars=None):
    # set App Kernel Description
    parser = AppKerOutputParser(
        name='xdmod.app.astro.enzo',
        version=1,
        description="Enzo: an Adaptive Mesh Refinement Code for Astrophysics",
        url='http://enzo-project.org',
        measurement_name='Enzo'
    )
    # set obligatory parameters and statistics
    # set common parameters and statistics
    parser.add_common_must_have_params_and_stats()
    # set app kernel custom sets
    parser.add_must_have_parameter('App:Version')
    parser.add_must_have_statistic('Wall Clock Time')

    # parse common parameters and statistics
    parser.parse_common_params_and_stats(appstdout, stdout, stderr, geninfo, resource_appker_vars)

    # read output
    lines = []
    if os.path.isfile(appstdout):
        fin = open(appstdout, "rt")
        lines = fin.readlines()
        fin.close()
    parser.set_parameter("App:Version", "unknown")
    # process the output
    successful_run = False
    j = 0
    while j < len(lines):
        m = re.match(r'^Mercurial Branch\s+(\S+)', lines[j])
        if m:
            branch = m.group(1)
            revision = ""
            if j + 1 < len(lines):
                m = re.match(r'^Mercurial Revision\s+(\S+)', lines[j + 1])
                if m:
                    revision = m.group(1)
            parser.set_parameter("App:Version", "Branch:" + branch + " Revision:" + revision)

        m = re.match(r'^Time\s*=\s*([0-9.]+)\s+CycleNumber\s*=\s*([0-9]+)\s+Wallclock\s*=\s*([0-9.]+)', lines[j])
        if m:
            parser.set_statistic("Final Simulation Time", m.group(1), "Enzo Time Unit")
            parser.set_statistic("Total Cycles", m.group(2))
            parser.set_statistic("Wall Clock Time", m.group(3), "Second")
            successful_run = True

        m = re.match(r'^Successful run, exiting.', lines[j])
        if m:
            successful_run = True

        # performance
        m = re.match(r'^Cycle_Number\s+([0-9]+)', lines[j])
        if m:
            j += 1
            performance_metrics = {}
            while j < len(lines):
                if lines[j].strip() != "":
                    v = lines[j].strip().split()
                    if v[0] not in performance_metrics:
                        performance_metrics[v[0]] = float(v[1])
                    else:
                        performance_metrics[v[0]] += float(v[1])
                else:
                    if j + 1 < len(lines):
                        m = re.match(r'^Cycle_Number\s+([0-9]+)', lines[j + 1])
                        if m:
                            pass
                        else:
                            break
                    else:
                        break
                j += 1

            metric = "CommunicationTranspose"
            if metric in performance_metrics:
                parser.set_statistic("Communication Transpose Time", performance_metrics[metric], "Second")

            metric = "ComputePotentialFieldLevelZero"
            if metric in performance_metrics:
                parser.set_statistic("Gravitational Potential Field Computing Time", performance_metrics[metric],
                                     "Second")

            metric = "EvolvePhotons"
            if metric in performance_metrics:
                parser.set_statistic("Radiative Transfer Calculation Time", performance_metrics[metric], "Second")

            metric = "Group_WriteAllData"
            if metric in performance_metrics:
                parser.set_statistic("All Data Group Write Time", performance_metrics[metric], "Second")

            metric = "Level_00"
            if metric in performance_metrics:
                parser.set_statistic("All Grid Level 00 Calculation Time", performance_metrics[metric], "Second")

            metric = "Level_01"
            if metric in performance_metrics:
                parser.set_statistic("All Grid Level 01 Calculation Time", performance_metrics[metric], "Second")

            metric = "Level_02"
            if metric in performance_metrics:
                parser.set_statistic("All Grid Level 02 Calculation Time", performance_metrics[metric], "Second")

            metric = "RebuildHierarchy"
            if metric in performance_metrics:
                parser.set_statistic("Grid Hierarchy Rebuilding Time", performance_metrics[metric], "Second")

            metric = "SetBoundaryConditions"
            if metric in performance_metrics:
                parser.set_statistic("Boundary Conditions Setting Time", performance_metrics[metric], "Second")

            metric = "SolveForPotential"
            if metric in performance_metrics:
                parser.set_statistic("Poisson Equation Solving Time", performance_metrics[metric], "Second")

            metric = "SolveHydroEquations"
            if metric in performance_metrics:
                parser.set_statistic("Hydro Equations Solving Time", performance_metrics[metric], "Second")

            metric = "Total"
            if metric in performance_metrics:
                parser.set_statistic("Total Time Spent in Cycles", performance_metrics[metric], "Second")

        j += 1
    parser.successfulRun = successful_run

    if __name__ == "__main__":
        # output for testing purpose
        print(("parsing complete:", parser.parsing_complete()))
        parser.print_params_stats_as_must_have()
        print((parser.get_xml()))

    # return complete XML overwize return None
    return parser.get_xml()


if __name__ == "__main__":
    """stand alone testing"""
    jobdir = sys.argv[1]
    print(("Proccessing Output From", jobdir))
    process_appker_output(appstdout=os.path.join(jobdir, "appstdout"), geninfo=os.path.join(jobdir, "gen.info"))
