def test_parser(datadir):
    from akrr.appkernelsparsers.app_astro_enzo import process_appker_output
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
    xml_out = ElementTree.fromstring(results)
    params = xml_out.find(".//parameters")
    stats = xml_out.find(".//statistics")

    assert xml_out.find('./exitStatus/completed').text == "true"

    assert len(params.find(".//parameter[ID='RunEnv:Nodes']").find('value').text) > 5
    assert params.find(".//parameter[ID='resource']").find('value').text == "HPC-Cluster"
    assert floats_are_close(
        float(stats.find(".//statistic[ID='All Data Group Write Time']").find('value').text), 10.915409)
    assert floats_are_close(
        float(stats.find(".//statistic[ID='All Grid Level 00 Calculation Time']").find('value').text), 42.9321762)
    assert floats_are_close(
        float(stats.find(".//statistic[ID='All Grid Level 01 Calculation Time']").find('value').text), 87.9636495)
    assert floats_are_close(
        float(stats.find(".//statistic[ID='All Grid Level 02 Calculation Time']").find('value').text), 34.781478992)
    assert floats_are_close(
        float(stats.find(".//statistic[ID='Boundary Conditions Setting Time']").find('value').text), 30.76190286)
    assert floats_are_close(
        float(stats.find(".//statistic[ID='Communication Transpose Time']").find('value').text), 1.244992267)
    assert floats_are_close(
        float(stats.find(".//statistic[ID='Final Simulation Time']").find('value').text), 26.413138)
    assert floats_are_close(
        float(stats.find(".//statistic[ID='Gravitational Potential Field Computing Time']").find('value').text),
        2.461694230)
    assert floats_are_close(
        float(stats.find(".//statistic[ID='Grid Hierarchy Rebuilding Time']").find('value').text), 29.1920113)
    assert floats_are_close(
        float(stats.find(".//statistic[ID='Hydro Equations Solving Time']").find('value').text), 60.4315396)
    assert floats_are_close(
        float(stats.find(".//statistic[ID='Poisson Equation Solving Time']").find('value').text), 32.91500784812)
    assert floats_are_close(
        float(stats.find(".//statistic[ID='Radiative Transfer Calculation Time']").find('value').text), 104.8994714547)
    assert floats_are_close(
        float(stats.find(".//statistic[ID='Total Cycles']").find('value').text), 161)
    assert floats_are_close(
        float(stats.find(".//statistic[ID='Total Time Spent in Cycles']").find('value').text), 327.22692)
    assert floats_are_close(
        float(stats.find(".//statistic[ID='Wall Clock Time']").find('value').text), 328.044961)

    assert stats.find(".//statistic[ID='App kernel executable exists']").find('value').text == '0'
    assert stats.find(".//statistic[ID='App kernel input exists']").find('value').text == '1'
    assert stats.find(".//statistic[ID='Network scratch directory accessible']").find('value').text == '1'
    assert stats.find(".//statistic[ID='Network scratch directory exists']").find('value').text == '1'
    assert stats.find(".//statistic[ID='Task working directory accessible']").find('value').text == '1'
    assert stats.find(".//statistic[ID='Task working directory exists']").find('value').text == '1'
    assert stats.find(".//statistic[ID='local scratch directory accessible']").find('value').text == '1'
    assert stats.find(".//statistic[ID='local scratch directory exists']").find('value').text == '1'
