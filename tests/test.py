def test(kernel_filter, disabled):
    print("Received:\tKernel:[%r]\tDisabled:[%r]" % (kernel_filter, disabled))

    query = """
    SELECT AK.id,
           CASE WHEN AK.name REGEXP '.core$' = 1 THEN SUBSTR(AK.name, 1, CHAR_LENGTH(AK.name) - 5)
           ELSE AK.name END name,
           AK.enabled,
           AK.nodes_list
    FROM mod_akrr.app_kernels AK
    WHERE AK.name = %s
    """ if kernel_filter and disabled else """
    SELECT AK.id,
           CASE WHEN AK.name REGEXP '.core$' = 1 THEN SUBSTR(AK.name, 1, CHAR_LENGTH(AK.name) - 5)
           ELSE AK.name END name,
           AK.enabled,
           AK.nodes_list
    FROM mod_akrr.app_kernels AK
    WHERE AK.name = %s
      AND AK.enabled = TRUE
    """ if kernel_filter else """
    SELECT AK.id,
           CASE WHEN AK.name REGEXP '.core$' = 1 THEN SUBSTR(AK.name, 1, CHAR_LENGTH(AK.name) - 5)
           ELSE AK.name END name,
           AK.enabled,
           AK.nodes_list
    FROM mod_akrr.app_kernels AK
    WHERE AK.enabled = TRUE
    """ if not disabled else """
    SELECT AK.id,
           CASE WHEN AK.name REGEXP '.core$' = 1 THEN SUBSTR(AK.name, 1, CHAR_LENGTH(AK.name) - 5)
           ELSE AK.name END name,
           AK.enabled,
           AK.nodes_list
    FROM mod_akrr.app_kernels AK
    """
    return query


if __name__ == '__main__':
    import sys

    def string_to_bool(value):
        return value and value.lower() in ('yes', 'true', 't', '1')

    if len(sys.argv) == 3:
        print(test(sys.argv[1], sys.argv[2]))
    elif len(sys.argv) == 2:
        print(test(None, string_to_bool(sys.argv[1])))
    else:
        print('Usage: test.py [<kernel_filter>] <disabled_flag>')