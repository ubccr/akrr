def test_parser(datadir):
    from akrr.parsers.hpcc_parser import process_appker_output
    import xml.etree.ElementTree as ElementTree
    from akrr.util import floats_are_close

    results = process_appker_output(
        appstdout=str(datadir / 'appstdout'),
        stdout=str(datadir / 'stdout'),
        stderr=str(datadir / 'stderr'),
        geninfo=str(datadir / 'gen.info'),
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
    assert params.find(".//parameter[ID='App:Version']").find('value').text == "1.4.2f"
    assert params.find(".//parameter[ID='Input:DGEMM Problem Size']").find('value').text == "2040"
    assert params.find(".//parameter[ID='Input:High Performance LINPACK Grid Cols']").find('value').text == "16"
    assert params.find(".//parameter[ID='Input:High Performance LINPACK Grid Rows']").find('value').text == "8"
    assert params.find(".//parameter[ID='Input:High Performance LINPACK Problem Size']").find('value').text == "40000"
    assert params.find(".//parameter[ID='Input:MPI Ranks']").find('value').text == "128"
    assert params.find(".//parameter[ID='Input:MPIRandom Problem Size']").find('value').text == "1024.0"
    assert params.find(".//parameter[ID='Input:OpenMP Threads']").find('value').text == "0"
    assert params.find(".//parameter[ID='Input:PTRANS Problem Size']").find('value').text == "20000"
    assert params.find(".//parameter[ID='Input:STREAM Array Size']").find('value').text == "4166666"
    assert params.find(".//parameter[ID='RunEnv:CPU Speed']").find('value').text == "2100.0"

    assert floats_are_close(float(stats.find(
        ".//statistic[ID='Average Double-Precision General Matrix Multiplication (DGEMM) Floating-Point Performance']"
        ).find('value').text), 47635.3)
    assert floats_are_close(
        float(stats.find(".//statistic[ID='Average STREAM Add Memory Bandwidth']").find('value').text), 4785.75616)
    assert floats_are_close(
        float(stats.find(".//statistic[ID='Average STREAM Copy Memory Bandwidth']").find('value').text), 5505.35168)
    assert floats_are_close(
        float(stats.find(".//statistic[ID='Average STREAM Scale Memory Bandwidth']").find('value').text), 4325.90848)
    assert floats_are_close(
        float(stats.find(".//statistic[ID='Average STREAM Triad Memory Bandwidth']").find('value').text), 4888.7808)
    assert floats_are_close(
        float(stats.find(
            ".//statistic[ID='Fast Fourier Transform (FFTW) Floating-Point Performance']").find('value').text), 67847.4)
    assert floats_are_close(
        float(stats.find(".//statistic[ID='High Performance LINPACK Efficiency']").find('value').text), 328.531)
    assert floats_are_close(
        float(stats.find(".//statistic[ID='High Performance LINPACK Floating-Point Performance']").find('value').text),
        3532370.0)
    assert floats_are_close(
        float(stats.find(".//statistic[ID='High Performance LINPACK Run Time']").find('value').text), 12.0794)
    assert floats_are_close(
        float(stats.find(".//statistic[ID='MPI Random Access']").find('value').text), 62.2572)
    assert floats_are_close(
        float(stats.find(".//statistic[ID='Parallel Matrix Transpose (PTRANS)']").find('value').text), 35308.1344)
    assert floats_are_close(
        float(stats.find(".//statistic[ID='Wall Clock Time']").find('value').text), 187.0)

    assert stats.find(".//statistic[ID='App kernel executable exists']").find('value').text == '1'
    assert stats.find(".//statistic[ID='App kernel input exists']").find('value').text == '1'
    assert stats.find(".//statistic[ID='Network scratch directory accessible']").find('value').text == '1'
    assert stats.find(".//statistic[ID='Network scratch directory exists']").find('value').text == '1'
    assert stats.find(".//statistic[ID='Task working directory accessible']").find('value').text == '1'
    assert stats.find(".//statistic[ID='Task working directory exists']").find('value').text == '1'
    assert stats.find(".//statistic[ID='local scratch directory accessible']").find('value').text == '1'
    assert stats.find(".//statistic[ID='local scratch directory exists']").find('value').text == '1'
