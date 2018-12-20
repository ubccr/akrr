def test_parser(datadir):
    from akrr.appkernelsparsers.app_md_gromacs_micro import process_appker_output
    results = process_appker_output(
        appstdout=str(datadir.join('appstdout')),
        stdout=str(datadir.join('stdout')),
        stderr=str(datadir.join('stderr')),
        geninfo=str(datadir.join('gen.info')),
    )
    print(results)
