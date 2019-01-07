def test_parser(datadir):
    from akrr.appkernelsparsers.namd_parser import process_appker_output
    import xml.etree.ElementTree as ElementTree
    from akrr.util import floats_are_close

    results = process_appker_output(
        appstdout=str(datadir / 'appstdout'),
        stdout=str(datadir / 'stdout'),
        stderr=str(datadir / 'stderr'),
        geninfo=str(datadir / 'gen.info'),
        resource_appker_vars={'resource': 'HPC-Cluster'}
    )
    print(results)
    # check resulting xml
    xml_out = ElementTree.fromstring(results)
    params = xml_out.find(".//parameters")
    stats = xml_out.find(".//statistics")

    assert xml_out.find('./exitStatus/completed').text == "true"

    assert len(params.find(".//parameter[ID='App:ExeBinSignature']").find('value').text) > 5
    assert params.find(".//parameter[ID='App:NCores']").find('value').text == "128"
    assert params.find(".//parameter[ID='App:NNodes']").find('value').text == "4"
    assert len(params.find(".//parameter[ID='RunEnv:Nodes']").find('value').text) > 5
    assert params.find(".//parameter[ID='resource']").find('value').text == "HPC-Cluster"
    assert params.find(".//parameter[ID='App:Version']").find('value').text == "2.13b1"
    assert params.find(".//parameter[ID='Input:Coordinate File']").find('value').text == "apoa1.pdb"
    assert params.find(".//parameter[ID='Input:Number of Angles']").find('value').text == "74136"
    assert params.find(".//parameter[ID='Input:Number of Atoms']").find('value').text == "92224"
    assert params.find(".//parameter[ID='Input:Number of Bonds']").find('value').text == "70660"
    assert params.find(".//parameter[ID='Input:Number of Dihedrals']").find('value').text == "74130"
    assert params.find(".//parameter[ID='Input:Number of Steps']").find('value').text == "1200"
    assert params.find(".//parameter[ID='Input:Structure File']").find('value').text == "apoa1.psf"
    assert params.find(".//parameter[ID='Input:Timestep']").find('value').text == "2e-15"

    assert floats_are_close(
        float(stats.find(".//statistic[ID='Memory']").find('value').text), 586.160156)
    assert floats_are_close(
        float(stats.find(".//statistic[ID='Molecular Dynamics Simulation Performance']").find('value').text),
        1.8502551501852105e-08)
    assert floats_are_close(
        float(stats.find(".//statistic[ID='Wall Clock Time']").find('value').text), 36.651707)

    assert stats.find(".//statistic[ID='App kernel executable exists']").find('value').text == '1'
    assert stats.find(".//statistic[ID='App kernel input exists']").find('value').text == '1'
    assert stats.find(".//statistic[ID='Network scratch directory accessible']").find('value').text == '1'
    assert stats.find(".//statistic[ID='Network scratch directory exists']").find('value').text == '1'
    assert stats.find(".//statistic[ID='Task working directory accessible']").find('value').text == '1'
    assert stats.find(".//statistic[ID='Task working directory exists']").find('value').text == '1'
    assert stats.find(".//statistic[ID='local scratch directory accessible']").find('value').text == '1'
    assert stats.find(".//statistic[ID='local scratch directory exists']").find('value').text == '1'
