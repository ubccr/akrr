def test_parser(datadir):
    from akrr.appkernelsparsers.benchmark_io_ior import process_appker_output
    import xml.etree.ElementTree as ElementTree
    from akrr.util import floats_are_close
    from .xml_comparison import parstat_val, parstat_val_f, parstat_val_i

    results = process_appker_output(
        appstdout=str(datadir / 'appstdout'),
        stdout=str(datadir / 'stdout'),
        stderr=str(datadir / 'stderr'),
        geninfo=str(datadir / 'gen.info'),
        resource_appker_vars={'resource': 'HPC-Cluster'}
    )
    # check resulting xml
    xml_out = ElementTree.fromstring(results)
    params = xml_out.find(".//parameters")
    stats = xml_out.find(".//statistics")

    assert xml_out.find('./exitStatus/completed').text == "true"

    # Compare parameters to reference
    assert len(parstat_val(params, "App:ExeBinSignature")) > 5
    assert len(parstat_val(params, "RunEnv:Nodes")) > 5
    assert parstat_val(params, "App:Version") == "3.0.1"
    assert parstat_val(params, "HDF Version") == "1.8.14 (Parallel)"
    assert parstat_val(params, "HDF5 Collective N-to-1 Test File System") == "gpfs gpfs0 /gpfs"
    assert parstat_val(params, "HDF5 Independent N-to-1 Test File System") == "gpfs gpfs0 /gpfs"
    assert parstat_val(params, "HDF5 N-to-N Test File System") == "gpfs gpfs0 /gpfs"
    assert parstat_val(params, "MPIIO Collective N-to-1 Test File System") == "gpfs gpfs0 /gpfs"
    assert parstat_val(params, "MPIIO Independent N-to-1 Test File System") == "gpfs gpfs0 /gpfs"
    assert parstat_val(params, "MPIIO N-to-N Test File System") == "gpfs gpfs0 /gpfs"
    assert parstat_val(params, "MPIIO Version") == "(version=3, subversion=1)"
    assert parstat_val(params, "POSIX N-to-1 Test File System") == "gpfs gpfs0 /gpfs"
    assert parstat_val(params, "POSIX N-to-N Test File System") == "gpfs gpfs0 /gpfs"
    assert parstat_val(params, "Parallel NetCDF Collective N-to-1 Test File System") == "gpfs gpfs0 /gpfs"
    assert parstat_val(params, "Parallel NetCDF Independent N-to-1 Test File System") == "gpfs gpfs0 /gpfs"
    assert parstat_val(params, "Parallel NetCDF Version") == "(version = 1.3.1 of 24 Sep 2012)"
    assert floats_are_close(parstat_val_f(params, "Per-Process Data Size"), 200.0)
    assert floats_are_close(parstat_val_f(params, "Per-Process I/O Block Size"), 200.0)
    assert floats_are_close(parstat_val_f(params, "Transfer Size Per I/O"), 20.0)
    assert parstat_val(params, "resource") == "HPC-Cluster"

    # Compare stats to reference
    assert parstat_val_i(stats, "App kernel executable exists") == 1
    assert parstat_val_i(stats, "App kernel input exists") == 1
    assert floats_are_close(parstat_val_f(stats, "HDF5 Collective N-to-1  File Close Time (Read)"), 0.078640)
    assert floats_are_close(parstat_val_f(stats, "HDF5 Collective N-to-1  File Close Time (Write)"), 2.12)
    assert floats_are_close(parstat_val_f(stats, "HDF5 Collective N-to-1  File Open Time (Read)"), 0.384665)
    assert floats_are_close(parstat_val_f(stats, "HDF5 Collective N-to-1  File Open Time (Write)"), 0.771071)
    assert floats_are_close(parstat_val_f(stats, "HDF5 Collective N-to-1 Read Aggregate Throughput"), 411.51)
    assert floats_are_close(parstat_val_f(stats, "HDF5 Collective N-to-1 Write Aggregate Throughput"), 189.38)
    assert floats_are_close(parstat_val_f(stats, "HDF5 Independent N-to-1  File Close Time (Read)"), 7.54)
    assert floats_are_close(parstat_val_f(stats, "HDF5 Independent N-to-1  File Close Time (Write)"), 17.24)
    assert floats_are_close(parstat_val_f(stats, "HDF5 Independent N-to-1  File Open Time (Read)"), 0.465735)
    assert floats_are_close(parstat_val_f(stats, "HDF5 Independent N-to-1  File Open Time (Write)"), 0.797255)
    assert floats_are_close(parstat_val_f(stats, "HDF5 Independent N-to-1 Read Aggregate Throughput"), 812.37)
    assert floats_are_close(parstat_val_f(stats, "HDF5 Independent N-to-1 Write Aggregate Throughput"), 544.09)
    assert floats_are_close(parstat_val_f(stats, "HDF5 N-to-N  File Close Time (Read)"), 17.68)
    assert floats_are_close(parstat_val_f(stats, "HDF5 N-to-N  File Close Time (Write)"), 25.30)
    assert floats_are_close(parstat_val_f(stats, "HDF5 N-to-N  File Open Time (Read)"), 10.95)
    assert floats_are_close(parstat_val_f(stats, "HDF5 N-to-N  File Open Time (Write)"), 24.63)
    assert floats_are_close(parstat_val_f(stats, "HDF5 N-to-N Read Aggregate Throughput"), 929.46)
    assert floats_are_close(parstat_val_f(stats, "HDF5 N-to-N Write Aggregate Throughput"), 755.65)
    assert floats_are_close(parstat_val_f(stats, "MPIIO Collective N-to-1  File Close Time (Read)"), 0.174882)
    assert floats_are_close(parstat_val_f(stats, "MPIIO Collective N-to-1  File Close Time (Write)"), 3.86)
    assert floats_are_close(parstat_val_f(stats, "MPIIO Collective N-to-1  File Open Time (Read)"), 0.803321)
    assert floats_are_close(parstat_val_f(stats, "MPIIO Collective N-to-1  File Open Time (Write)"), 0.773575)
    assert floats_are_close(parstat_val_f(stats, "MPIIO Collective N-to-1 Read Aggregate Throughput"), 357.51)
    assert floats_are_close(parstat_val_f(stats, "MPIIO Collective N-to-1 Write Aggregate Throughput"), 468.32)
    assert floats_are_close(parstat_val_f(stats, "MPIIO Independent N-to-1  File Close Time (Read)"), 36.32)
    assert floats_are_close(parstat_val_f(stats, "MPIIO Independent N-to-1  File Close Time (Write)"), 18.75)
    assert floats_are_close(parstat_val_f(stats, "MPIIO Independent N-to-1  File Open Time (Read)"), 0.807227)
    assert floats_are_close(parstat_val_f(stats, "MPIIO Independent N-to-1  File Open Time (Write)"), 0.819208)
    assert floats_are_close(parstat_val_f(stats, "MPIIO Independent N-to-1 Read Aggregate Throughput"), 492.79)
    assert floats_are_close(parstat_val_f(stats, "MPIIO Independent N-to-1 Write Aggregate Throughput"), 517.62)
    assert floats_are_close(parstat_val_f(stats, "MPIIO N-to-N  File Close Time (Read)"), 11.36)
    assert floats_are_close(parstat_val_f(stats, "MPIIO N-to-N  File Close Time (Write)"), 27.27)
    assert floats_are_close(parstat_val_f(stats, "MPIIO N-to-N  File Open Time (Read)"), 0.091708)
    assert floats_are_close(parstat_val_f(stats, "MPIIO N-to-N  File Open Time (Write)"), 26.62)
    assert floats_are_close(parstat_val_f(stats, "MPIIO N-to-N Read Aggregate Throughput"), 927.21)
    assert floats_are_close(parstat_val_f(stats, "MPIIO N-to-N Write Aggregate Throughput"), 701.60)
    assert parstat_val_i(stats, "Network scratch directory accessible") == 1
    assert parstat_val_i(stats, "Network scratch directory exists") == 1
    assert parstat_val_i(stats, "Number of Tests Passed") == 10
    assert parstat_val_i(stats, "Number of Tests Started") == 20
    assert floats_are_close(parstat_val_f(stats, "POSIX N-to-1  File Close Time (Read)"), 22.47)
    assert floats_are_close(parstat_val_f(stats, "POSIX N-to-1  File Close Time (Write)"), 13.50)
    assert floats_are_close(parstat_val_f(stats, "POSIX N-to-1  File Open Time (Read)"), 0.082365)
    assert floats_are_close(parstat_val_f(stats, "POSIX N-to-1  File Open Time (Write)"), 0.161028)
    assert floats_are_close(parstat_val_f(stats, "POSIX N-to-1 Read Aggregate Throughput"), 742.56)
    assert floats_are_close(parstat_val_f(stats, "POSIX N-to-1 Write Aggregate Throughput"), 613.20)
    assert floats_are_close(parstat_val_f(stats, "POSIX N-to-N  File Close Time (Read)"), 15.76)
    assert floats_are_close(parstat_val_f(stats, "POSIX N-to-N  File Close Time (Write)"), 38.33)
    assert floats_are_close(parstat_val_f(stats, "POSIX N-to-N  File Open Time (Read)"), 15.40)
    assert floats_are_close(parstat_val_f(stats, "POSIX N-to-N  File Open Time (Write)"), 38.60)
    assert floats_are_close(parstat_val_f(stats, "POSIX N-to-N Read Aggregate Throughput"), 938.84)
    assert floats_are_close(parstat_val_f(stats, "POSIX N-to-N Write Aggregate Throughput"), 488.70)
    assert floats_are_close(parstat_val_f(stats, "Parallel NetCDF Collective N-to-1  File Close Time (Read)"), 0.626368)
    assert floats_are_close(parstat_val_f(stats, "Parallel NetCDF Collective N-to-1  File Close Time (Write)"),
                            0.032479)
    assert floats_are_close(parstat_val_f(stats, "Parallel NetCDF Collective N-to-1  File Open Time (Read)"), 0.874303)
    assert floats_are_close(parstat_val_f(stats, "Parallel NetCDF Collective N-to-1  File Open Time (Write)"), 0.826898)
    assert floats_are_close(parstat_val_f(stats, "Parallel NetCDF Collective N-to-1 Read Aggregate Throughput"), 803.91)
    assert floats_are_close(parstat_val_f(stats, "Parallel NetCDF Collective N-to-1 Write Aggregate Throughput"),
                            752.14)
    assert floats_are_close(parstat_val_f(stats, "Parallel NetCDF Independent N-to-1  File Close Time (Read)"), 5.90)
    assert floats_are_close(parstat_val_f(stats, "Parallel NetCDF Independent N-to-1  File Close Time (Write)"), 22.18)
    assert floats_are_close(parstat_val_f(stats, "Parallel NetCDF Independent N-to-1  File Open Time (Read)"), 0.910970)
    assert floats_are_close(parstat_val_f(stats, "Parallel NetCDF Independent N-to-1  File Open Time (Write)"),
                            0.793515)
    assert floats_are_close(parstat_val_f(stats, "Parallel NetCDF Independent N-to-1 Read Aggregate Throughput"),
                            861.72)
    assert floats_are_close(parstat_val_f(stats, "Parallel NetCDF Independent N-to-1 Write Aggregate Throughput"),
                            317.39)
    assert parstat_val_i(stats, "Task working directory accessible") == 1
    assert parstat_val_i(stats, "Task working directory exists") == 1
    assert floats_are_close(parstat_val_f(stats, "Wall Clock Time"), 816.0)
    assert parstat_val_i(stats, "local scratch directory accessible") == 1
    assert parstat_val_i(stats, "local scratch directory exists") == 1
