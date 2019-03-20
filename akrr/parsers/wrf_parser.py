import re
import os
import sys
from akrr.parsers.akrrappkeroutputparser import AppKerOutputParser


def process_appker_output(appstdout=None, stdout=None, stderr=None, geninfo=None, resource_appker_vars=None):
    # set App Kernel Description
    parser = AppKerOutputParser(
        name='wrf',
        version=1,
        description="Weather Research and Forecasting Model",
        url='http://www.wrf-model.org',
        measurement_name='WRF'
    )
    # set obligatory parameters and statistics
    # set common parameters and statistics
    parser.add_common_must_have_params_and_stats()
    # set app kernel custom sets
    parser.add_must_have_parameter('App:Version')
    parser.add_must_have_parameter('Input:Grid Resolution')
    parser.add_must_have_parameter('Input:Simulation Length')
    parser.add_must_have_parameter('Input:Simulation Start Date')
    parser.add_must_have_parameter('Input:Timestep')
    parser.add_must_have_parameter('RunEnv:Nodes')
    parser.add_must_have_parameter('WRF Dynamical Solver')

    # parser.add_must_have_statistic('Average Floating-Point Performance')
    parser.add_must_have_statistic('Average Simulation Speed')
    parser.add_must_have_statistic('Mean Time To Simulate One Timestep')
    parser.add_must_have_statistic('Output Data Size')
    # parser.add_must_have_statistic('Peak Floating-Point Performance')
    parser.add_must_have_statistic('Peak Simulation Speed')
    parser.add_must_have_statistic('Time Spent on I/O')
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
    io_size = None
    wall_clock_time = None
    iteration_wall_clock_time = []
    sim_time_per_iteration = None
    dx = None
    dy = None
    flops_conversion = None

    j = 0
    while j < len(lines):
        m = re.search(r'XDMOD\*\*\*SIZE OF CURRENT DIR BEFORE WRF RUN\s*(\d+)', lines[j])
        if m:
            io_size = int(m.group(1).strip())

        m = re.search(r'XDMOD\*\*\*SIZE OF CURRENT DIR AFTER WRF RUN\s*(\d+)', lines[j])
        if m and io_size:
            parser.set_statistic("Output Data Size", (int(m.group(1).strip()) - io_size) / 1024.0 / 1024.0, "MByte")

        m = re.search(r'XDMOD\*\*\*WRF RUN BEGINS HERE --(.+)', lines[j])
        if m:
            wall_clock_time = parser.get_datetime_local(m.group(1).strip())

        m = re.search(r'XDMOD\*\*\*WRF RUN HAS FINISHED --(.+)', lines[j])
        if m and wall_clock_time:
            wall_clock_time = parser.get_datetime_local(m.group(1).strip()) - wall_clock_time
            parser.set_statistic("Wall Clock Time", wall_clock_time.total_seconds(), "Second")

        if lines[j].find('XDMOD***RESULT OF rsl.out.0000 BEGINS') >= 0:
            # the output from MPI rank #0
            io_time = None
            while j < len(lines):
                if lines[j].find('XDMOD***RESULT OF rsl.out.0000 ENDS') >= 0:
                    break

                m = re.search(r'Timing for processing restart file.+?:\s+(\d\S+)', lines[j], re.I)
                if m:
                    if io_time is None:
                        io_time = 0.0
                    io_time += float(m.group(1).strip())

                m = re.search(r'Timing for Writing.+?:\s+(\d\S+)', lines[j], re.I)
                if m:
                    if io_time is None:
                        io_time = 0.0
                    io_time += float(m.group(1).strip())

                m = re.search(r'Timing for main: time.+?on domain.+?:\s+(\d\S+)', lines[j], re.I)
                if m:
                    iteration_wall_clock_time.append(float(m.group(1).strip()))

                m = re.search(r'WRF NUMBER OF TILES.+?(\d+)', lines[j])
                if m:
                    omp_threads = int(m.group(1).strip())
                    if omp_threads > 1:
                        parser.set_parameter("Number of OpenMP Threads", omp_threads)

                m = re.match(r'^\s+WRF V(\S+) MODEL', lines[j])
                if m:
                    parser.set_parameter("App:Version", m.group(1).strip())
                j += 1
            parser.set_statistic("Time Spent on I/O", io_time, "Second")

        if re.search('XDMOD\*\*\*RESULT OF wrfout.+?BEGINS', lines[j]) is not None:
            # the output file's header (netCDF dump)
            io_time = None
            while j < len(lines):
                if re.search('XDMOD\*\*\*RESULT OF wrfout.+?ENDS', lines[j]) is not None:
                    break

                m = re.search(r':DX = (\d+)', lines[j], re.I)
                if m:
                    dx = float(m.group(1).strip()) * 0.001  # in meters

                m = re.search(r':DY = (\d+)', lines[j], re.I)
                if m:
                    dy = float(m.group(1).strip()) * 0.001  # in meters

                m = re.search(r':DT = (\d+)', lines[j], re.I)
                if m:
                    sim_time_per_iteration = float(m.group(1).strip())  # in seconds
                    parser.set_parameter("Input:Timestep", sim_time_per_iteration, "Second per Step")

                m = re.search(r':SIMULATION_START_DATE = "(.+?)"', lines[j], re.I)
                if m:
                    parser.set_parameter("Input:Simulation Start Date", (m.group(1).strip()))

                m = re.search(r':GRIDTYPE = "(.+?)"', lines[j], re.I)
                if m:
                    solver = m.group(1).strip()
                    if solver == 'C':
                        solver = 'Advanced Research WRF (ARW)'
                    if solver == 'E':
                        solver = 'Nonhydrostatic Mesoscale Model (NMM)'
                    parser.set_parameter("WRF Dynamical Solver", solver)

                m = re.search(r'Timing for Writing.+?:\s+(\d\S+)', lines[j], re.I)
                if m:
                    if io_time is None:
                        io_time = 0.0
                    io_time += float(m.group(1).strip())

                m = re.search(r'Timing for main: time.+?on domain.+?:\s+(\d\S+)', lines[j], re.I)
                if m:
                    iteration_wall_clock_time.append(float(m.group(1).strip()))

                m = re.search(r'WRF NUMBER OF TILES.+?(\d+)', lines[j])
                if m:
                    omp_threads = int(m.group(1).strip())
                    if omp_threads > 1:
                        parser.set_parameter("Number of OpenMP Threads", omp_threads)

                m = re.match(r'^\s+WRF V(\S+) MODEL', lines[j])
                if m:
                    parser.set_parameter("App:Version", m.group(1).strip())
                j += 1
            if dx and dy:
                if (dx - int(dx)) * 1000 < 0.1 and (dy - int(dy)) * 1000 < 0.1:  # back compatibility with output format
                    parser.set_parameter("Input:Grid Resolution", "%.0f x %.0f" % (dx, dy), "km^2")
                else:
                    parser.set_parameter("Input:Grid Resolution", str(dx) + " x " + str(dy), "km^2")

        m = re.search(r'XDMOD\*\*\*FLOATING-POINT PERFORMANCE CONVERSION', lines[j])
        if m:
            flops_conversion = lines[j + 1].strip()
        j += 1

    if wall_clock_time:
        parser.successfulRun = True
    else:
        parser.successfulRun = False

    if len(iteration_wall_clock_time) > 0 and sim_time_per_iteration:
        parser.set_parameter("Input:Simulation Length",
                             (len(iteration_wall_clock_time)) * sim_time_per_iteration / 3600.0, "Hour")
        iteration_wall_clock_time = sorted(iteration_wall_clock_time)
        iteration_wall_clock_time.pop()

        t = 0.0
        min_t = iteration_wall_clock_time[0]
        for tt in iteration_wall_clock_time:
            t += tt
        t = t / len(iteration_wall_clock_time)
        parser.set_statistic("Mean Time To Simulate One Timestep", t, "Second")
        parser.set_statistic("Average Simulation Speed", sim_time_per_iteration / t, "Simulated Second per Second")
        parser.set_statistic("Peak Simulation Speed", sim_time_per_iteration / min_t, "Simulated Second per Second")

        if flops_conversion:
            flops_conversion = flops_conversion.replace("$", "").replace("gflops=", "")
            gflops = eval(flops_conversion, {'T': t})
            parser.set_statistic("Average Floating-Point Performance", 1000.0 * gflops, "MFLOP per Second")
            gflops = eval(flops_conversion, {'T': min_t})
            parser.set_statistic("Peak Floating-Point Performance", 1000.0 * gflops, "MFLOP per Second")

    if __name__ == "__main__":
        # output for testing purpose
        parsing_complete = parser.parsing_complete(True)
        print("parsing complete:", parsing_complete)
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
