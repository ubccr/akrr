def test_parser(datadir):
    from akrr.appkernelsparsers.quantum_espresso_parser import process_appker_output
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
    xml_out = ElementTree.fromstring(results.replace("'",""))
    params = xml_out.find(".//parameters")
    stats = xml_out.find(".//statistics")

    assert xml_out.find('./exitStatus/completed').text == "true"

    # Compare parameters to reference
    assert len(parstat_val(params, "App:ExeBinSignature")) > 5
    assert len(parstat_val(params, "RunEnv:Nodes")) > 5
    assert parstat_val(params, "resource") == "HPC-Cluster"
    assert parstat_val(params, "App:Version") == "v.4.2.1"
    assert parstat_val_i(params, "Input:Number of Atomic Types") == 2
    assert parstat_val_i(params, "Input:Number of Atoms per Cell") == 63
    assert floats_are_close(parstat_val_f(params, "Input:Number of Electrons"), 564.00)

    # Compare stats to reference
    assert parstat_val_i(stats, "App kernel executable exists") == 1
    assert parstat_val_i(stats, "App kernel input exists") == 1
    assert parstat_val_i(stats, "Task working directory accessible") == 1
    assert parstat_val_i(stats, "Task working directory exists") == 1
    assert parstat_val_i(stats, "local scratch directory accessible") == 1
    assert parstat_val_i(stats, "local scratch directory exists") == 1
    assert parstat_val_i(stats, "Network scratch directory accessible") == 1
    assert parstat_val_i(stats, "Network scratch directory exists") == 1

    assert floats_are_close(parstat_val_f(stats, "Per-Process Dynamical Memory"), 77.6)
    assert floats_are_close(parstat_val_f(stats, "Time Spent in Electron Energy Calculation"), 149.84)
    assert floats_are_close(parstat_val_f(stats, "Time Spent in Force Calculation"), 2.24)
    assert floats_are_close(parstat_val_f(stats, "Time Spent in Program Initialization"), 2.79)
    assert floats_are_close(parstat_val_f(stats, "User Time"), 155.69)
    assert floats_are_close(parstat_val_f(stats, "Wall Clock Time"), 157.34)
