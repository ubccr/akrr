def test_parser(datadir):
    from akrr.appkernelsparsers.app_chem_nwchem import process_appker_output
    import xml.etree.ElementTree as ElementTree
    from akrr.util import floats_are_close

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

    assert len(params.find(".//parameter[ID='App:ExeBinSignature']").find('value').text) > 5
    assert len(params.find(".//parameter[ID='RunEnv:Nodes']").find('value').text) > 5
    assert params.find(".//parameter[ID='resource']").find('value').text == "HPC-Cluster"
    assert params.find(".//parameter[ID='App:Version']").find('value').text == "6.8"
    assert params.find(".//parameter[ID='Input:File']").find('value').text == "aump2.nw"

    assert floats_are_close(
        float(stats.find(".//statistic[ID='Global Arrays Accumulate Amount']").find('value').text), 421.5240478515625)
    assert floats_are_close(
        float(stats.find(".//statistic[ID='Global Arrays Accumulate Calls']").find('value').text), 176000)
    assert floats_are_close(
        float(stats.find(".//statistic[ID='Global Arrays Create Calls']").find('value').text), 580)
    assert floats_are_close(
        float(stats.find(".//statistic[ID='Global Arrays Destroy Calls']").find('value').text), 580)
    assert floats_are_close(
        float(stats.find(".//statistic[ID='Global Arrays Get Amount']").find('value').text), 963.2110595703125)
    assert floats_are_close(
        float(stats.find(".//statistic[ID='Global Arrays Get Calls']").find('value').text), 24900)
    assert floats_are_close(
        float(stats.find(".//statistic[ID='Global Arrays Put Amount']").find('value').text), 152.587890625)
    assert floats_are_close(
        float(stats.find(".//statistic[ID='Global Arrays Put Calls']").find('value').text), 17800)
    assert floats_are_close(
        float(stats.find(".//statistic[ID='User Time']").find('value').text), 9.4)
    assert floats_are_close(
        float(stats.find(".//statistic[ID='Wall Clock Time']").find('value').text), 20.1)

    assert stats.find(".//statistic[ID='App kernel executable exists']").find('value').text == '1'
    assert stats.find(".//statistic[ID='App kernel input exists']").find('value').text == '1'
    assert stats.find(".//statistic[ID='Network scratch directory accessible']").find('value').text == '1'
    assert stats.find(".//statistic[ID='Network scratch directory exists']").find('value').text == '1'
    assert stats.find(".//statistic[ID='Task working directory accessible']").find('value').text == '1'
    assert stats.find(".//statistic[ID='Task working directory exists']").find('value').text == '1'
    assert stats.find(".//statistic[ID='local scratch directory accessible']").find('value').text == '1'
    assert stats.find(".//statistic[ID='local scratch directory exists']").find('value').text == '1'
