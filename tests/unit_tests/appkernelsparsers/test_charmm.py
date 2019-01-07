def test_parser(datadir):
    from akrr.appkernelsparsers.charmm_parser import process_appker_output
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
    xml_out = ElementTree.fromstring(results.replace("'", ""))
    params = xml_out.find(".//parameters")
    stats = xml_out.find(".//statistics")

    assert xml_out.find('./exitStatus/completed').text == "true"

    # Compare parameters to reference
    assert len(parstat_val(params, "App:ExeBinSignature")) > 5
    assert len(parstat_val(params, "RunEnv:Nodes")) > 5
    assert parstat_val(params, "resource") == "HPC-Cluster"
    assert parstat_val_i(params, "Input:Number of Angles") == 16145
    assert parstat_val_i(params, "Input:Number of Atoms") == 26047
    assert parstat_val_i(params, "Input:Number of Bonds") == 26115
    assert parstat_val_i(params, "Input:Number of Dihedrals") == 13402
    assert parstat_val_i(params, "Input:Number of Steps") == 1000
    assert floats_are_close(parstat_val_f(params, "Input:Timestep"), 1e-15)

    # Compare stats to reference
    assert parstat_val_i(stats, "App kernel executable exists") == 1
    assert parstat_val_i(stats, "App kernel input exists") == 1
    assert parstat_val_i(stats, "Task working directory accessible") == 1
    assert parstat_val_i(stats, "Task working directory exists") == 1
    assert parstat_val_i(stats, "local scratch directory accessible") == 1
    assert parstat_val_i(stats, "local scratch directory exists") == 1
    assert parstat_val_i(stats, "Network scratch directory accessible") == 1
    assert parstat_val_i(stats, "Network scratch directory exists") == 1

    assert floats_are_close(parstat_val_f(stats, "Molecular Dynamics Simulation Performance"), 2.478485370051635e-09)
    assert floats_are_close(parstat_val_f(stats, "Time Spent in External Energy Calculation"), 16.0)
    assert floats_are_close(parstat_val_f(stats, "Time Spent in Integration"), 0.2)
    assert floats_are_close(parstat_val_f(stats, "Time Spent in Internal Energy Calculation"), 2.3)
    assert floats_are_close(parstat_val_f(stats, "Time Spent in Non-Bond List Generation"), 3.2)
    assert floats_are_close(parstat_val_f(stats, "Time Spent in Waiting (Load Unbalance-ness)"), 0.1)
    assert floats_are_close(parstat_val_f(stats, "User Time"), 33.00)
    assert floats_are_close(parstat_val_f(stats, "Wall Clock Time"), 34.86)
