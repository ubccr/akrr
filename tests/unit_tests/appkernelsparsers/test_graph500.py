def test_parser(datadir):
    from akrr.parsers.graph500_parser import process_appker_output
    import xml.etree.ElementTree as ElementTree
    from akrr.util import floats_are_close

    subdir = '1node'

    results = process_appker_output(
        appstdout=str(datadir / subdir / 'appstdout'),
        stdout=str(datadir / subdir / 'stdout'),
        stderr=str(datadir / subdir / 'stderr'),
        geninfo=str(datadir / subdir / 'gen.info'),
        resource_appker_vars={'resource': 'HPC-Cluster'}
    )
    # check resulting xml
    xml_out = ElementTree.fromstring(results)
    params = xml_out.find(".//parameters")
    stats = xml_out.find(".//statistics")

    print(results)

    assert xml_out.find('./exitStatus/completed').text == "true"

    assert len(params.find(".//parameter[ID='App:ExeBinSignature']").find('value').text) > 5
    assert len(params.find(".//parameter[ID='RunEnv:Nodes']").find('value').text) > 5
    assert params.find(".//parameter[ID='resource']").find('value').text == "HPC-Cluster"
    assert params.find(".//parameter[ID='App:Version']").find('value').text == "2.1.4 replicated csc"
    assert params.find(".//parameter[ID='Edge Factor']").find('value').text == "16"
    assert params.find(".//parameter[ID='Number of Edges']").find('value').text == "134217728"
    assert params.find(".//parameter[ID='Number of Roots to Check']").find('value').text == "64"
    assert params.find(".//parameter[ID='Number of Vertices']").find('value').text == "8388608"
    assert params.find(".//parameter[ID='Scale']").find('value').text == "23"

    assert floats_are_close(
        float(stats.find(".//statistic[ID='Harmonic Mean TEPS']").find('value').text), 6.60498e+09)
    assert floats_are_close(
        float(stats.find(".//statistic[ID='Harmonic Standard Deviation TEPS']").find('value').text), 1.88566e+08)
    assert floats_are_close(
        float(stats.find(".//statistic[ID='Median TEPS']").find('value').text), 7.22041e+09)
    assert floats_are_close(
        float(stats.find(".//statistic[ID='Wall Clock Time']").find('value').text), 336.0)

    assert stats.find(".//statistic[ID='App kernel executable exists']").find('value').text == '1'
    assert stats.find(".//statistic[ID='App kernel input exists']").find('value').text == '1'
    assert stats.find(".//statistic[ID='Network scratch directory accessible']").find('value').text == '1'
    assert stats.find(".//statistic[ID='Network scratch directory exists']").find('value').text == '1'
    assert stats.find(".//statistic[ID='Task working directory accessible']").find('value').text == '1'
    assert stats.find(".//statistic[ID='Task working directory exists']").find('value').text == '1'
    assert stats.find(".//statistic[ID='local scratch directory accessible']").find('value').text == '1'
    assert stats.find(".//statistic[ID='local scratch directory exists']").find('value').text == '1'
