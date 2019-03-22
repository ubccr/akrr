def test_parser(datadir):
    from akrr.parsers.mpi_tile_io_parser import process_appker_output
    import xml.etree.ElementTree as ElementTree
    from akrr.util import floats_are_close
    from .xml_comparison import parstat_val, parstat_val_f, parstat_val_i

    results = process_appker_output(
        appstdout=str(datadir / 'appstdout'),
        stdout=str(datadir / 'stdout'),
        stderr=str(datadir / 'stderr'),
        geninfo=str(datadir / 'gen.info'),
        resource_appker_vars={'resource': {'name': 'HPC-Cluster'}}
    )
    # check resulting xml
    xml_out = ElementTree.fromstring(results.replace("'", ""))
    params = xml_out.find(".//parameters")
    stats = xml_out.find(".//statistics")

    assert xml_out.find('./exitStatus/completed').text == "true"

    # Compare parameters to reference
    assert len(parstat_val(params, "App:ExeBinSignature")) > 5
    assert len(parstat_val(params, "RunEnv:Nodes")) > 5
    assert parstat_val(params, "resource") == "HPC-Cluster"
    assert parstat_val(params, "2D Collective Read Test File System") == "panfs (panfs://panfs.ccr.buffalo.edu:global)"
    assert parstat_val(params, "2D Collective Write Test File System") == "panfs (panfs://panfs.ccr.buffalo.edu:global)"
    assert parstat_val(params,
                       "2D HDF5 Collective Read Test File System") == "panfs (panfs://panfs.ccr.buffalo.edu:global)"
    assert parstat_val(params,
                       "2D HDF5 Collective Write Test File System") == "panfs (panfs://panfs.ccr.buffalo.edu:global)"
    assert parstat_val(params, "2D Independent Read Test File System") == "panfs (panfs://panfs.ccr.buffalo.edu:global)"
    assert parstat_val(params,
                       "2D Independent Write Test File System") == "panfs (panfs://panfs.ccr.buffalo.edu:global)"
    assert parstat_val(params, "2D Per-Process Data Topology") == "5120x5120"
    assert parstat_val(params, "2D Per-Process Ghost Zone") == "0x0"
    assert floats_are_close(parstat_val_f(params, "2D Per-Process Memory"), 200.0)
    assert parstat_val(params, "2D Process Topology") == "8x8"
    assert parstat_val(params, "3D Collective Read Test File System") == "panfs (panfs://panfs.ccr.buffalo.edu:global)"
    assert parstat_val(params, "3D Collective Write Test File System") == "panfs (panfs://panfs.ccr.buffalo.edu:global)"
    assert parstat_val(params,
                       "3D HDF5 Collective Read Test File System") == "panfs (panfs://panfs.ccr.buffalo.edu:global)"
    assert parstat_val(params,
                       "3D HDF5 Collective Write Test File System") == "panfs (panfs://panfs.ccr.buffalo.edu:global)"
    assert parstat_val(params, "3D Independent Read Test File System") == "panfs (panfs://panfs.ccr.buffalo.edu:global)"
    assert parstat_val(params,
                       "3D Independent Write Test File System") == "panfs (panfs://panfs.ccr.buffalo.edu:global)"
    assert parstat_val(params, "3D Per-Process Data Topology") == "256x320x320"
    assert parstat_val(params, "3D Per-Process Ghost Zone") == "0x0x0"
    assert floats_are_close(parstat_val_f(params, "3D Per-Process Memory"), 200.0)
    assert parstat_val(params, "3D Process Topology") == "4x4x4"
    assert parstat_val(params, "HDF Version") == "1.8.11 (Parallel)"
    assert parstat_val(params, "MPI-IO Hints") == "panfs_concurrent_write=1;"

    # Compare stats to reference
    assert parstat_val_i(stats, "App kernel executable exists") == 1
    assert parstat_val_i(stats, "App kernel input exists") == 1
    assert parstat_val_i(stats, "Task working directory accessible") == 1
    assert parstat_val_i(stats, "Task working directory exists") == 1
    assert parstat_val_i(stats, "local scratch directory accessible") == 1
    assert parstat_val_i(stats, "local scratch directory exists") == 1
    assert parstat_val_i(stats, "Network scratch directory accessible") == 1
    assert parstat_val_i(stats, "Network scratch directory exists") == 1

    assert floats_are_close(parstat_val_f(stats, "2D Array Collective Read Aggregate Throughput"), 620.45)
    assert floats_are_close(parstat_val_f(stats, "2D Array Collective Write Aggregate Throughput"), 287.00)
    assert floats_are_close(parstat_val_f(stats, "2D Array HDF5 Collective Read Aggregate Throughput"), 653.72)
    assert floats_are_close(parstat_val_f(stats, "2D Array HDF5 Collective Write Aggregate Throughput"), 330.36)
    assert floats_are_close(parstat_val_f(stats, "2D Array Independent Read Aggregate Throughput"), 541.87)
    assert floats_are_close(parstat_val_f(stats, "2D Array Independent Write Aggregate Throughput"), 21.46)
    assert floats_are_close(parstat_val_f(stats, "3D Array Collective Read Aggregate Throughput"), 652.08)
    assert floats_are_close(parstat_val_f(stats, "3D Array Collective Write Aggregate Throughput"), 336.02)
    assert floats_are_close(parstat_val_f(stats, "3D Array HDF5 Collective Read Aggregate Throughput"), 636.77)
    assert floats_are_close(parstat_val_f(stats, "3D Array HDF5 Collective Write Aggregate Throughput"), 317.90)
    assert floats_are_close(parstat_val_f(stats, "3D Array Independent Read Aggregate Throughput"), 331.93)
    assert floats_are_close(parstat_val_f(stats, "3D Array Independent Write Aggregate Throughput"), 27.17)
    assert floats_are_close(parstat_val_f(stats, "File Close Time (2D Data Collective Read)"), 0.000261)
    assert floats_are_close(parstat_val_f(stats, "File Close Time (2D Data Collective Write)"), 0.181099)
    assert floats_are_close(parstat_val_f(stats, "File Close Time (2D Data HDF5 Collective Read)"), 0.000697)
    assert floats_are_close(parstat_val_f(stats, "File Close Time (2D Data HDF5 Collective Write)"), 0.772100)
    assert floats_are_close(parstat_val_f(stats, "File Close Time (2D Data Independent Read)"), 0.000081)
    assert floats_are_close(parstat_val_f(stats, "File Close Time (2D Data Independent Write)"), 0.032696)
    assert floats_are_close(parstat_val_f(stats, "File Close Time (3D Data Collective Read)"), 0.000405)
    assert floats_are_close(parstat_val_f(stats, "File Close Time (3D Data Collective Write)"), 0.191116)
    assert floats_are_close(parstat_val_f(stats, "File Close Time (3D Data HDF5 Collective Read)"), 0.000653)
    assert floats_are_close(parstat_val_f(stats, "File Close Time (3D Data HDF5 Collective Write)"), 0.841222)
    assert floats_are_close(parstat_val_f(stats, "File Close Time (3D Data Independent Read)"), 0.000288)
    assert floats_are_close(parstat_val_f(stats, "File Close Time (3D Data Independent Write)"), 0.032183)
    assert floats_are_close(parstat_val_f(stats, "File Open Time (2D Data Collective Read)"), 0.086550)
    assert floats_are_close(parstat_val_f(stats, "File Open Time (2D Data Collective Write)"), 0.049139)
    assert floats_are_close(parstat_val_f(stats, "File Open Time (2D Data HDF5 Collective Read)"), 0.078241)
    assert floats_are_close(parstat_val_f(stats, "File Open Time (2D Data HDF5 Collective Write)"), 0.037127)
    assert floats_are_close(parstat_val_f(stats, "File Open Time (2D Data Independent Read)"), 0.030526)
    assert floats_are_close(parstat_val_f(stats, "File Open Time (2D Data Independent Write)"), 0.041617)
    assert floats_are_close(parstat_val_f(stats, "File Open Time (3D Data Collective Read)"), 0.071459)
    assert floats_are_close(parstat_val_f(stats, "File Open Time (3D Data Collective Write)"), 0.037431)
    assert floats_are_close(parstat_val_f(stats, "File Open Time (3D Data HDF5 Collective Read)"), 0.061011)
    assert floats_are_close(parstat_val_f(stats, "File Open Time (3D Data HDF5 Collective Write)"), 0.049155)
    assert floats_are_close(parstat_val_f(stats, "File Open Time (3D Data Independent Read)"), 0.054999)
    assert floats_are_close(parstat_val_f(stats, "File Open Time (3D Data Independent Write)"), 0.034026)
    assert floats_are_close(parstat_val_f(stats, "Wall Clock Time"), 864.0)
