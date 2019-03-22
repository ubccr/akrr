def test_parser(datadir):
    from akrr.parsers.wrf_parser import process_appker_output
    import xml.etree.ElementTree as ElementTree
    from akrr.util import floats_are_close
    from .xml_comparison import parstat_val, parstat_val_f, parstat_val_i, print_params_or_stats_for_comparisons

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
    assert floats_are_close(parstat_val_f(params, "App:Version"), 3.3)
    assert parstat_val(params, "Input:Grid Resolution") == "12 x 12"
    assert floats_are_close(parstat_val_f(params, "Input:Simulation Length"), 3.0)
    assert parstat_val(params, "Input:Simulation Start Date") == "2001-10-24_00:00:00"
    assert floats_are_close(parstat_val_f(params, "Input:Timestep"), 72.0)
    assert parstat_val(params, "WRF Dynamical Solver") == "Advanced Research WRF (ARW)"

    # Compare stats to reference
    assert parstat_val_i(stats, "App kernel executable exists") == 1
    assert parstat_val_i(stats, "App kernel input exists") == 1
    assert parstat_val_i(stats, "Task working directory accessible") == 1
    assert parstat_val_i(stats, "Task working directory exists") == 1
    assert parstat_val_i(stats, "local scratch directory accessible") == 1
    assert parstat_val_i(stats, "local scratch directory exists") == 1
    assert parstat_val_i(stats, "Network scratch directory accessible") == 1
    assert parstat_val_i(stats, "Network scratch directory exists") == 1

    assert floats_are_close(parstat_val_f(stats, "Average Floating-Point Performance"), 45428.61484535666)
    assert floats_are_close(parstat_val_f(stats, "Average Simulation Speed"), 108.68089675922646)
    assert floats_are_close(parstat_val_f(stats, "Mean Time To Simulate One Timestep"), 0.6624899328859059)
    assert floats_are_close(parstat_val_f(stats, "Output Data Size"), 625.2359209060669)
    assert floats_are_close(parstat_val_f(stats, "Peak Floating-Point Performance"), 50479.70479704797)
    assert floats_are_close(parstat_val_f(stats, "Peak Simulation Speed"), 120.7648440120765)
    assert floats_are_close(parstat_val_f(stats, "Time Spent on I/O"), 40.9111)
    assert floats_are_close(parstat_val_f(stats, "Wall Clock Time"), 144.0)
