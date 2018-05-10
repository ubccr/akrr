
def test_akrr_daemon_status():
    from akrr.akrrscheduler import akrrd_main2
    akrrd_main2(action='status')
