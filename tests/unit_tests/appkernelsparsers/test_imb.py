def test_parser(datadir):
    from akrr.parsers.imb_parser import process_appker_output
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
    xml_out = ElementTree.fromstring(results.replace("'",""))
    params = xml_out.find(".//parameters")
    stats = xml_out.find(".//statistics")

    assert xml_out.find('./exitStatus/completed').text == "true"

    # Compare parameters to reference
    assert len(parstat_val(params, "App:ExeBinSignature")) > 5
    assert len(parstat_val(params, "RunEnv:Nodes")) > 5
    assert floats_are_close(parstat_val_f(params, "App:MPI Version"), 3.1)
    assert floats_are_close(parstat_val_f(params, "App:Max Message Size"), 4.0)
    assert parstat_val(params, "resource") == "HPC-Cluster"

    # Compare stats to reference
    assert parstat_val_i(stats, "App kernel executable exists") == 1
    assert parstat_val_i(stats, "App kernel input exists") == 1
    assert parstat_val_i(stats, "Task working directory accessible") == 1
    assert parstat_val_i(stats, "Task working directory exists") == 1
    assert parstat_val_i(stats, "local scratch directory accessible") == 1
    assert parstat_val_i(stats, "local scratch directory exists") == 1
    assert parstat_val_i(stats, "Network scratch directory accessible") == 1
    assert parstat_val_i(stats, "Network scratch directory exists") == 1

    assert floats_are_close(parstat_val_f(stats, "Max Exchange Bandwidth"), 18536.14)
    assert floats_are_close(parstat_val_f(stats, "Max MPI-2 Bidirectional Get Bandwidth (aggregate)"), 1619.75)
    assert floats_are_close(parstat_val_f(stats, "Max MPI-2 Bidirectional Get Bandwidth (non-aggregate)"), 3465.83)
    assert floats_are_close(parstat_val_f(stats, "Max MPI-2 Bidirectional Put Bandwidth (aggregate)"), 10857.36)
    assert floats_are_close(parstat_val_f(stats, "Max MPI-2 Bidirectional Put Bandwidth (non-aggregate)"), 11046.2)
    assert floats_are_close(parstat_val_f(stats, "Max MPI-2 Unidirectional Get Bandwidth (aggregate)"), 3664.45)
    assert floats_are_close(parstat_val_f(stats, "Max MPI-2 Unidirectional Get Bandwidth (non-aggregate)"), 3809.56)
    assert floats_are_close(parstat_val_f(stats, "Max MPI-2 Unidirectional Put Bandwidth (aggregate)"), 12090.85)
    assert floats_are_close(parstat_val_f(stats, "Max MPI-2 Unidirectional Put Bandwidth (non-aggregate)"), 11589.06)
    assert floats_are_close(parstat_val_f(stats, "Max PingPing Bandwidth"), 11277.77)
    assert floats_are_close(parstat_val_f(stats, "Max PingPong Bandwidth"), 11833.44)
    assert floats_are_close(parstat_val_f(stats, "Max SendRecv Bandwidth"), 18086.86)
    assert floats_are_close(parstat_val_f(stats, "Min AllGather Latency"), 4.669999999999999e-06)
    assert floats_are_close(parstat_val_f(stats, "Min AllGatherV Latency"), 4.8299999999999995e-06)
    assert floats_are_close(parstat_val_f(stats, "Min AllReduce Latency"), 4.69e-06)
    assert floats_are_close(parstat_val_f(stats, "Min AllToAll Latency"), 4.16e-06)
    assert floats_are_close(parstat_val_f(stats, "Min AllToAllV Latency"), 4.24e-06)
    assert floats_are_close(parstat_val_f(stats, "Min Barrier Latency"), 4.41e-06)
    assert floats_are_close(parstat_val_f(stats, "Min Broadcast Latency"), 1.83e-06)
    assert floats_are_close(parstat_val_f(stats, "Min Gather Latency"), 6.5e-07)
    assert floats_are_close(parstat_val_f(stats, "Min GatherV Latency"), 4.2099999999999995e-06)
    assert floats_are_close(parstat_val_f(stats, "Min MPI-2 Accumulate Latency (aggregate)"), 3.8499999999999996e-06)
    assert floats_are_close(parstat_val_f(stats, "Min MPI-2 Accumulate Latency (non-aggregate)"),
                            1.3539999999999999e-05)
    assert floats_are_close(parstat_val_f(stats, "Min MPI-2 Window Creation Latency"), 5.4189999999999994e-05)
    assert floats_are_close(parstat_val_f(stats, "Min Reduce Latency"), 3.92e-06)
    assert floats_are_close(parstat_val_f(stats, "Min ReduceScatter Latency"), 2.35e-06)
    assert floats_are_close(parstat_val_f(stats, "Min Scatter Latency"), 1.47e-06)
    assert floats_are_close(parstat_val_f(stats, "Min ScatterV Latency"), 1.48e-06)
    assert floats_are_close(parstat_val_f(stats, "Wall Clock Time"), 48.0)
