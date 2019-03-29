def test_intel_hpcg_parser(datadir):
    from akrr.parsers.hpcg_parser import process_appker_output
    import xml.etree.ElementTree as ElementTree
    from akrr.util import floats_are_close

    results = process_appker_output(
        appstdout=str(datadir / "intel_hpcg" / 'appstdout'),
        stdout=str(datadir / "intel_hpcg" / 'stdout'),
        stderr=str(datadir / "intel_hpcg" / 'stderr'),
        geninfo=str(datadir / "intel_hpcg" / 'gen.info'),
        resource_appker_vars={'resource': {'name': 'HPC-Cluster'}}
    )

    # check resulting xml
    xml_out = ElementTree.fromstring(results.replace("'", ""))
    params = xml_out.find(".//parameters")
    stats = xml_out.find(".//statistics")

    assert xml_out.find('./exitStatus/completed').text == "true"

    assert len(params.find(".//parameter[ID='App:ExeBinSignature']").find('value').text) > 5
    assert len(params.find(".//parameter[ID='RunEnv:Nodes']").find('value').text) > 5
    assert params.find(".//parameter[ID='resource']").find('value').text == "HPC-Cluster"
    assert params.find(".//parameter[ID='App:Version']").find('value').text == "n104-4p-1t version V3.0"
    assert params.find(".//parameter[ID='RunEnv:CPU Speed']").find('value').text == "2100.0"
    assert params.find(".//parameter[ID='Input:Global Problem Dimensions Nx']").find('value').text == "208"
    assert params.find(".//parameter[ID='Input:Global Problem Dimensions Ny']").find('value').text == "208"
    assert params.find(".//parameter[ID='Input:Global Problem Dimensions Nz']").find('value').text == "104"
    assert params.find(".//parameter[ID='Input:Local Domain Dimensions Nx']").find('value').text == "104"
    assert params.find(".//parameter[ID='Input:Local Domain Dimensions Ny']").find('value').text == "104"
    assert params.find(".//parameter[ID='Input:Local Domain Dimensions Nz']").find('value').text == "104"
    assert params.find(".//parameter[ID='Input:Number of Coarse Grid Levels']").find('value').text == "3"
    assert params.find(".//parameter[ID='Input:Distributed Processes']").find('value').text == "4"
    assert params.find(".//parameter[ID='Input:Threads per processes']").find('value').text == "1"

    assert floats_are_close(float(stats.find(
        ".//statistic[ID='Floating-Point Performance, Raw DDOT']").find('value').text), 18.2061)
    assert floats_are_close(float(stats.find(
        ".//statistic[ID='Floating-Point Performance, Raw MG']").find('value').text), 2.5673)
    assert floats_are_close(float(stats.find(
        ".//statistic[ID='Floating-Point Performance, Raw SpMV']").find('value').text), 1.92444)
    assert floats_are_close(float(stats.find(
        ".//statistic[ID='Floating-Point Performance, Raw Total']").find('value').text), 2.38135)
    assert floats_are_close(float(stats.find(
        ".//statistic[ID='Floating-Point Performance, Raw WAXPBY']").find('value').text), 9.62525)
    assert floats_are_close(float(stats.find(
        ".//statistic[ID='Floating-Point Performance, Total']").find('value').text), 2.36085)
    assert floats_are_close(float(stats.find(
        ".//statistic[ID='Memory Bandwidth, Read']").find('value').text), 14.6723)
    assert floats_are_close(float(stats.find(
        ".//statistic[ID='Memory Bandwidth, Total']").find('value').text), 18.0631)
    assert floats_are_close(float(stats.find(
        ".//statistic[ID='Memory Bandwidth, Write']").find('value').text), 3.3908)
    assert floats_are_close(float(stats.find(
        ".//statistic[ID='Setup Time']").find('value').text), 1.4719)
    assert floats_are_close(float(stats.find(
        ".//statistic[ID='Wall Clock Time']").find('value').text), 138.0)

    assert stats.find(".//statistic[ID='App kernel executable exists']").find('value').text == '1'
    assert stats.find(".//statistic[ID='App kernel input exists']").find('value').text == '1'
    assert stats.find(".//statistic[ID='Network scratch directory accessible']").find('value').text == '1'
    assert stats.find(".//statistic[ID='Network scratch directory exists']").find('value').text == '1'
    assert stats.find(".//statistic[ID='Task working directory accessible']").find('value').text == '1'
    assert stats.find(".//statistic[ID='Task working directory exists']").find('value').text == '1'
    assert stats.find(".//statistic[ID='local scratch directory accessible']").find('value').text == '1'
    assert stats.find(".//statistic[ID='local scratch directory exists']").find('value').text == '1'


def test_original_hpcg_parser(datadir):
    from akrr.parsers.hpcg_parser import process_appker_output
    import xml.etree.ElementTree as ElementTree
    from akrr.util import floats_are_close

    results = process_appker_output(
        appstdout=str(datadir / "original_hpcg" / 'appstdout'),
        stdout=str(datadir / "original_hpcg" / 'stdout'),
        stderr=str(datadir / "original_hpcg" / 'stderr'),
        geninfo=str(datadir / "original_hpcg" / 'gen.info'),
        resource_appker_vars={'resource': {'name': 'HPC-Cluster'}}
    )

    # check resulting xml
    xml_out = ElementTree.fromstring(results.replace("'", ""))
    params = xml_out.find(".//parameters")
    stats = xml_out.find(".//statistics")

    assert xml_out.find('./exitStatus/completed').text == "true"

    assert len(params.find(".//parameter[ID='App:ExeBinSignature']").find('value').text) > 5
    assert len(params.find(".//parameter[ID='RunEnv:Nodes']").find('value').text) > 5
    assert params.find(".//parameter[ID='resource']").find('value').text == "HPC-Cluster"
    assert params.find(".//parameter[ID='App:Version']").find('value').text == "HPCG-Benchmark version 3.0"
    assert params.find(".//parameter[ID='RunEnv:CPU Speed']").find('value').text == "2100.0"
    assert params.find(".//parameter[ID='Input:Global Problem Dimensions Nx']").find('value').text == "208"
    assert params.find(".//parameter[ID='Input:Global Problem Dimensions Ny']").find('value').text == "208"
    assert params.find(".//parameter[ID='Input:Global Problem Dimensions Nz']").find('value').text == "104"
    assert params.find(".//parameter[ID='Input:Local Domain Dimensions Nx']").find('value').text == "104"
    assert params.find(".//parameter[ID='Input:Local Domain Dimensions Ny']").find('value').text == "104"
    assert params.find(".//parameter[ID='Input:Local Domain Dimensions Nz']").find('value').text == "104"
    assert params.find(".//parameter[ID='Input:Number of Coarse Grid Levels']").find('value').text == "3"
    assert params.find(".//parameter[ID='Input:Distributed Processes']").find('value').text == "4"
    assert params.find(".//parameter[ID='Input:Threads per processes']").find('value').text == "1"

    assert floats_are_close(float(stats.find(
        ".//statistic[ID='Floating-Point Performance, Raw DDOT']").find('value').text), 0.637654)
    assert floats_are_close(float(stats.find(
        ".//statistic[ID='Floating-Point Performance, Raw MG']").find('value').text), 0.778318)
    assert floats_are_close(float(stats.find(
        ".//statistic[ID='Floating-Point Performance, Raw SpMV']").find('value').text), 0.91135)
    assert floats_are_close(float(stats.find(
        ".//statistic[ID='Floating-Point Performance, Raw Total']").find('value').text), 0.80397)
    assert floats_are_close(float(stats.find(
        ".//statistic[ID='Floating-Point Performance, Raw WAXPBY']").find('value').text), 5.65298)
    assert floats_are_close(float(stats.find(
        ".//statistic[ID='Floating-Point Performance, Total']").find('value').text), 0.773896)
    assert floats_are_close(float(stats.find(
        ".//statistic[ID='Memory Bandwidth, Read']").find('value').text), 4.95353)
    assert floats_are_close(float(stats.find(
        ".//statistic[ID='Memory Bandwidth, Total']").find('value').text), 6.0983)
    assert floats_are_close(float(stats.find(
        ".//statistic[ID='Memory Bandwidth, Write']").find('value').text), 1.14477)
    assert floats_are_close(float(stats.find(
        ".//statistic[ID='Setup Time']").find('value').text), 40.2448)
    assert floats_are_close(float(stats.find(
        ".//statistic[ID='Wall Clock Time']").find('value').text), 385.0)

    assert stats.find(".//statistic[ID='App kernel executable exists']").find('value').text == '1'
    assert stats.find(".//statistic[ID='App kernel input exists']").find('value').text == '1'
    assert stats.find(".//statistic[ID='Network scratch directory accessible']").find('value').text == '1'
    assert stats.find(".//statistic[ID='Network scratch directory exists']").find('value').text == '1'
    assert stats.find(".//statistic[ID='Task working directory accessible']").find('value').text == '1'
    assert stats.find(".//statistic[ID='Task working directory exists']").find('value').text == '1'
    assert stats.find(".//statistic[ID='local scratch directory accessible']").find('value').text == '1'
    assert stats.find(".//statistic[ID='local scratch directory exists']").find('value').text == '1'
