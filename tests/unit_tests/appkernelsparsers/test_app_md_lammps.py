def test_parser(datadir):
    from akrr.appkernelsparsers.lammps_parser import process_appker_output
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
    assert parstat_val(params, "App:Version") == "1 May 2010"
    assert parstat_val_i(params, "Input:Number of Atoms") == 32000
    assert parstat_val_i(params, "Input:Number of Steps") == 4000
    assert floats_are_close(parstat_val_f(params, "Input:Timestep"), 2e-15)

    # Compare stats to reference
    assert parstat_val_i(stats, "App kernel executable exists") == 1
    assert parstat_val_i(stats, "App kernel input exists") == 1
    assert parstat_val_i(stats, "Task working directory accessible") == 1
    assert parstat_val_i(stats, "Task working directory exists") == 1
    assert parstat_val_i(stats, "local scratch directory accessible") == 1
    assert parstat_val_i(stats, "local scratch directory exists") == 1
    assert parstat_val_i(stats, "Network scratch directory accessible") == 1
    assert parstat_val_i(stats, "Network scratch directory exists") == 1

    assert floats_are_close(parstat_val_f(stats, "Molecular Dynamics Simulation Performance"), 7.1538502141911645e-09)
    assert floats_are_close(parstat_val_f(stats, "Per-Process Memory"), 11.8058)
    assert floats_are_close(parstat_val_f(stats, "Time Spent in Bond Potential Calculation"), 3.04537)
    assert floats_are_close(parstat_val_f(stats, "Time Spent in Communication"), 3.19531)
    assert floats_are_close(parstat_val_f(stats, "Time Spent in Long-Range Coulomb Potential (K-Space) Calculation"),
                            22.1585)
    assert floats_are_close(parstat_val_f(stats, "Time Spent in Neighbor List Regeneration"), 9.04183)
    assert floats_are_close(parstat_val_f(stats, "Time Spent in Pairwise Potential Calculation"), 54.2335)
    assert floats_are_close(parstat_val_f(stats, "Wall Clock Time"), 96.6193)

