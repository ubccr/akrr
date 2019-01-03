def test_parser(datadir):
    from akrr.appkernelsparsers.test_parser import process_appker_output
    import xml.etree.ElementTree as ElementTree
    from akrr.util import floats_are_close
    from .xml_comparison import parstat_val, parstat_val_f, parstat_val_i, print_params_or_stats_for_comparisons

    results = process_appker_output(
        appstdout=str(datadir / 'appstdout'),
        stdout=str(datadir / 'stdout'),
        stderr=str(datadir / 'stderr'),
        geninfo=str(datadir / 'gen.info'),
        resource_appker_vars={'resource': 'HPC-Cluster'}
    )
    # check resulting xml
    xml_out = ElementTree.fromstring(results.replace("'",""))
    params = xml_out.find(".//parameters")
    stats = xml_out.find(".//statistics")

    assert xml_out.find('./exitStatus/completed').text == "true"

    # Compare parameters to reference
    assert len(parstat_val(params, "App:ExeBinSignature")) > 5
    assert len(parstat_val(params, "RunEnv:Nodes")) > 5
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

    assert parstat_val_i(stats, "App kernel executable exists") == 1
    assert parstat_val_i(stats, "App kernel input exists") == 1
    assert parstat_val_i(stats, "Network scratch directory accessible") == 1
    assert parstat_val_i(stats, "Network scratch directory exists") == 1
    assert parstat_val_i(stats, "Shell is BASH") == 1
    assert parstat_val_i(stats, "Task working directory accessible") == 1
    assert parstat_val_i(stats, "Task working directory exists") == 1
    assert floats_are_close(parstat_val_f(stats, "Wall Clock Time"), 0.0)
    assert parstat_val_i(stats, "local scratch directory accessible") == 1
    assert parstat_val_i(stats, "local scratch directory exists") == 1
