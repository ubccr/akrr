def test_parser(datadir):
    from akrr.parsers.mdtest_parser import process_appker_output
    import xml.etree.ElementTree as ElementTree
    from akrr.util import floats_are_close
    from .xml_comparison import parstat_val, parstat_val_f, parstat_val_i

    results = process_appker_output(
        appstdout=str(datadir / 'v1' / 'appstdout'),
        stdout=str(datadir / 'v1' / 'stdout'),
        stderr=str(datadir / 'v1' / 'stderr'),
        geninfo=str(datadir / 'v1' / 'gen.info'),
        resource_appker_vars={'resource': {'name': 'HPC-Cluster'}}
    )
    # check resulting xml
    xml_out = ElementTree.fromstring(results)
    params = xml_out.find(".//parameters")
    stats = xml_out.find(".//statistics")

    assert xml_out.find('./exitStatus/completed').text == "true"

    # Compare parameters to reference
    assert len(parstat_val(params, "App:ExeBinSignature")) > 5
    assert len(parstat_val(params, "RunEnv:Nodes")) > 5
    assert parstat_val(params, "Arguments (single directory per process)") == "-v -I 32 -z 0 -b 0 -i 2 -u"
    assert parstat_val(params, "Arguments (single directory)") == "-v -I 32 -z 0 -b 0 -i 2"
    assert parstat_val(params, "Arguments (single tree directory per process)") == "-v -I 4 -z 4 -b 2 -i 2 -u"
    assert parstat_val(params, "Arguments (single tree directory)") == "-v -I 4 -z 4 -b 2 -i 2"
    assert parstat_val_i(params, "files/directories (single directory per process)") == 3072
    assert parstat_val_i(params, "files/directories (single directory)") == 3072
    assert parstat_val_i(params, "files/directories (single tree directory per process)") == 11904
    assert parstat_val_i(params, "files/directories (single tree directory)") == 11904
    assert parstat_val(params, "resource") == "HPC-Cluster"
    assert parstat_val_i(params, "tasks (single directory per process)") == 96
    assert parstat_val_i(params, "tasks (single directory)") == 96
    assert parstat_val_i(params, "tasks (single tree directory per process)") == 96
    assert parstat_val_i(params, "tasks (single tree directory)") == 96

    # Compare stats to reference
    assert parstat_val_i(stats, "App kernel executable exists") == 1
    assert parstat_val_i(stats, "App kernel input exists") == 1
    assert parstat_val_i(stats, "Network scratch directory accessible") == 1
    assert parstat_val_i(stats, "Network scratch directory exists") == 1
    assert parstat_val_i(stats, "Task working directory accessible") == 1
    assert parstat_val_i(stats, "Task working directory exists") == 1
    assert parstat_val_i(stats, "local scratch directory accessible") == 1
    assert parstat_val_i(stats, "local scratch directory exists") == 1

    assert floats_are_close(parstat_val_f(stats, "Directory creation (single directory per process)"), 25485.108)
    assert floats_are_close(parstat_val_f(stats, "Directory creation (single directory)"), 100.331)
    assert floats_are_close(parstat_val_f(stats, "Directory creation (single tree directory per process)"), 14795.304)
    assert floats_are_close(parstat_val_f(stats, "Directory creation (single tree directory)"), 1159.207)
    assert floats_are_close(parstat_val_f(stats, "Directory removal (single directory per process)"), 106924.358)
    assert floats_are_close(parstat_val_f(stats, "Directory removal (single directory)"), 83.151)
    assert floats_are_close(parstat_val_f(stats, "Directory removal (single tree directory per process)"), 98807.620)
    assert floats_are_close(parstat_val_f(stats, "Directory removal (single tree directory)"), 1013.108)
    assert floats_are_close(parstat_val_f(stats, "Directory stat (single directory per process)"), 1474174.388)
    assert floats_are_close(parstat_val_f(stats, "Directory stat (single directory)"), 157316.373)
    assert floats_are_close(parstat_val_f(stats, "Directory stat (single tree directory per process)"), 1081034.251)
    assert floats_are_close(parstat_val_f(stats, "Directory stat (single tree directory)"), 123501.252)
    assert floats_are_close(parstat_val_f(stats, "File creation (single directory per process)"), 35892.066)
    assert floats_are_close(parstat_val_f(stats, "File creation (single directory)"), 113.827)
    assert floats_are_close(parstat_val_f(stats, "File creation (single tree directory per process)"), 26951.173)
    assert floats_are_close(parstat_val_f(stats, "File creation (single tree directory)"), 1807.941)
    assert floats_are_close(parstat_val_f(stats, "File read (single directory per process)"), 294344.471)
    assert floats_are_close(parstat_val_f(stats, "File read (single directory)"), 277066.971)
    assert floats_are_close(parstat_val_f(stats, "File read (single tree directory per process)"), 286266.660)
    assert floats_are_close(parstat_val_f(stats, "File read (single tree directory)"), 289428.427)
    assert floats_are_close(parstat_val_f(stats, "File removal (single directory per process)"), 147540.803)
    assert floats_are_close(parstat_val_f(stats, "File removal (single directory)"), 123.151)
    assert floats_are_close(parstat_val_f(stats, "File removal (single tree directory per process)"), 100810.329)
    assert floats_are_close(parstat_val_f(stats, "File removal (single tree directory)"), 2973.052)
    assert floats_are_close(parstat_val_f(stats, "File stat (single directory per process)"), 1548423.892)
    assert floats_are_close(parstat_val_f(stats, "File stat (single directory)"), 1483281.640)
    assert floats_are_close(parstat_val_f(stats, "File stat (single tree directory per process)"), 1161124.965)
    assert floats_are_close(parstat_val_f(stats, "File stat (single tree directory)"), 114689.532)
    assert floats_are_close(parstat_val_f(stats, "Tree creation (single directory per process)"), 2.446)
    assert floats_are_close(parstat_val_f(stats, "Tree creation (single directory)"), 3734.746)
    assert floats_are_close(parstat_val_f(stats, "Tree creation (single tree directory per process)"), 48.073)
    assert floats_are_close(parstat_val_f(stats, "Tree creation (single tree directory)"), 4143.686)
    assert floats_are_close(parstat_val_f(stats, "Tree removal (single directory per process)"), 2.046)
    assert floats_are_close(parstat_val_f(stats, "Tree removal (single directory)"), 132.413)
    assert floats_are_close(parstat_val_f(stats, "Tree removal (single tree directory per process)"), 58.162)
    assert floats_are_close(parstat_val_f(stats, "Tree removal (single tree directory)"), 188.171)
    assert floats_are_close(parstat_val_f(stats, "Wall Clock Time"), 320.0)
