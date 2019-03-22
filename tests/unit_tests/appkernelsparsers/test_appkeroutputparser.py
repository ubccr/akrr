def test_appkeroutputparser(datadir):
    from akrr.parsers.akrrappkeroutputparser import AppKerOutputParser, total_seconds
    import xml.etree.ElementTree as ElementTree

    parser = AppKerOutputParser(
        name='test',
        version=1,
        description="Test the resource deployment",
        url='http://xdmod.buffalo.edu',
        measurement_name='test'
    )
    parser.add_common_must_have_params_and_stats()
    assert len(parser.mustHaveParameters) == 2
    parser.add_must_have_parameter("Must have parameter 1")
    parser.add_must_have_parameter("Must have parameter 2")
    parser.add_must_have_parameter("Must have parameter 3")
    parser.add_must_have_statistic("Must have statistic 1")
    parser.add_must_have_statistic("Must have statistic 2")
    parser.add_must_have_statistic("Must have statistic 3")

    assert "Must have parameter 1" in parser.mustHaveParameters
    assert "Must have parameter 2" in parser.mustHaveParameters
    assert "Must have parameter 3" in parser.mustHaveParameters
    assert "Must have statistic 1" in parser.mustHaveStatistics
    assert "Must have statistic 2" in parser.mustHaveStatistics
    assert "Must have statistic 3" in parser.mustHaveStatistics

    # parse common parameters and statistics
    parser.parse_common_params_and_stats(
        str(datadir / 'appstdout'),  str(datadir / 'stdout'), str(datadir / 'stderr'), str(datadir / 'gen.info'),
        resource_appker_vars={'resource': {'name': 'HPC-Cluster'}, 'app': {'name': 'test'}})

    # set statistics
    if parser.wallClockTime is not None:
        parser.set_statistic("Wall Clock Time", total_seconds(parser.wallClockTime), "Second")

    # check resulting xml
    xml_text_out = parser.get_xml()
    xml_out = ElementTree.fromstring(xml_text_out)
    params = xml_out.find(".//parameters")
    stats = xml_out.find(".//statistics")

    assert len(params.find(".//parameter[ID='RunEnv:Nodes']").find('value').text) > 5
    assert stats.find(".//statistic[ID='Network scratch directory accessible']").find('value').text == '1'
    assert stats.find(".//statistic[ID='Task working directory exists']").find('value').text == '1'
    assert float(xml_out.find(".//statistic[ID='Wall Clock Time']").find('value').text) == 2.0
    assert xml_out.find('./exitStatus/completed').text == "false"
