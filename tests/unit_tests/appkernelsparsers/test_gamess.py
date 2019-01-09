def test_parser(datadir):
    from akrr.parsers.gamess_parser import process_appker_output
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
    assert len(params.find(".//parameter[ID='RunEnv:Nodes']").find('value').text) > 5
    assert params.find(".//parameter[ID='resource']").find('value').text == "HPC-Cluster"
    assert params.find(".//parameter[ID='App:NCores']").find('value').text == "128"
    assert params.find(".//parameter[ID='App:NNodes']").find('value').text == "4"
    assert params.find(".//parameter[ID='App:Version']").find('value').text == "02 AUG 2018 (R2)"

    assert floats_are_close(
        float(stats.find(".//statistic[ID='Time Spent in MP2 Energy Calculation']").find('value').text), 134.28)
    assert floats_are_close(
        float(stats.find(".//statistic[ID='Time Spent in Restricted Hartree-Fock Calculation']").find('value').text),
        376.44)
    assert floats_are_close(
        float(stats.find(".//statistic[ID='User Time']").find('value').text), 539.367)
    assert floats_are_close(
        float(stats.find(".//statistic[ID='Wall Clock Time']").find('value').text), 978.0)

    assert stats.find(".//statistic[ID='App kernel executable exists']").find('value').text == '1'
    assert stats.find(".//statistic[ID='App kernel input exists']").find('value').text == '1'
    assert stats.find(".//statistic[ID='Network scratch directory accessible']").find('value').text == '1'
    assert stats.find(".//statistic[ID='Network scratch directory exists']").find('value').text == '1'
    assert stats.find(".//statistic[ID='Task working directory accessible']").find('value').text == '1'
    assert stats.find(".//statistic[ID='Task working directory exists']").find('value').text == '1'
    assert stats.find(".//statistic[ID='local scratch directory accessible']").find('value').text == '1'
    assert stats.find(".//statistic[ID='local scratch directory exists']").find('value').text == '1'
