
def check_and_change():
    from . import cfg_test

    cfg_test.new_var = "New Variable"
    cfg_test.fruit = "Pineapple"


def check_and_change2():
    from . import cfg_test

    cfg_test.new_var = "New Variable 2"
    cfg_test.fruit = "Banana"