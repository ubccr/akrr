def test_parser(datadir):
    from akrr.parsers.akrr_network_check_parser import process_appker_output
    import xml.etree.ElementTree as ElementTree
    from akrr.util import floats_are_close

    results = process_appker_output(
        appstdout=str(datadir / 'appstdout'),
        stdout=str(datadir / 'stdout'),
        stderr=str(datadir / 'stderr'),
        geninfo=str(datadir / 'gen.info'),
        resource_appker_vars={'resource': {'name': 'HPC-Cluster'}}
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

    assert floats_are_close(
        float(stats.find(".//statistic[ID='Ping, Mean']").find('value').text), 25.6462)
    assert floats_are_close(
        float(stats.find(".//statistic[ID='Secure Copy Bandwidth (in), Mean']").find('value').text), 47.635894)
    assert floats_are_close(
        float(stats.find(".//statistic[ID='Secure Copy Bandwidth (out), Mean']").find('value').text), 51.487587149999996)
    assert floats_are_close(
        float(stats.find(".//statistic[ID='WGet Bandwidth, Mean']").find('value').text), 44.2)

    assert floats_are_close(
        float(stats.find(".//statistic[ID='Wall Clock Time']").find('value').text), 336.0)

    assert stats.find(".//statistic[ID='App kernel executable exists']").find('value').text == '0'
    assert stats.find(".//statistic[ID='App kernel input exists']").find('value').text == '1'
    assert stats.find(".//statistic[ID='Network scratch directory accessible']").find('value').text == '1'
    assert stats.find(".//statistic[ID='Network scratch directory exists']").find('value').text == '1'
    assert stats.find(".//statistic[ID='Task working directory accessible']").find('value').text == '1'
    assert stats.find(".//statistic[ID='Task working directory exists']").find('value').text == '1'
    assert stats.find(".//statistic[ID='local scratch directory accessible']").find('value').text == '1'
    assert stats.find(".//statistic[ID='local scratch directory exists']").find('value').text == '1'
