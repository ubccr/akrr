import xml.etree.ElementTree


def parstat_val(params: xml.etree.ElementTree, param_id: str) -> str:
    """
    find parameter or statistic from ElementTree
    """
    if params.tag == "parameters":
        param_record = params.find(".//parameter[ID='%s']" % param_id)
    elif params.tag == "statistics":
        param_record = params.find(".//statistic[ID='%s']" % param_id)
    else:
        raise ValueError("Unknown tag for element")

    if param_record is None:
        raise IndexError("Can not find element with parameter name: " + param_id)
    param_value = param_record.find('value')
    if param_value is None:
        raise IndexError("Can not find value for parameter: " + param_id)
    return param_value.text


def parstat_val_f(params: xml.etree.ElementTree, param_id: str) -> float:
    return float(parstat_val(params, param_id))


def parstat_val_i(params: xml.etree.ElementTree, param_id: str) -> int:
    val = parstat_val(params, param_id)
    if not val.isdigit():
        ValueError("Value is not integer")
    return int(val)


def print_params_or_stats_for_comparisons(elm: xml.etree.ElementTree):
    """
    Print python code for comparison of parameters or statistics.

    Parameters
    ----------
    elm - params or stats
    parent_name parameters or statistics

    Returns
    -------

    """
    from akrr.util import is_float, is_int
    if elm.tag == "parameters":
        record_tag = "parameter"
    elif elm.tag == "statistics":
        record_tag = "statistic"
    else:
        raise ValueError("Unknown tag for element")

    all_record = elm.findall(record_tag)
    for record in all_record:
        record_id = record.find('ID').text
        record_value = record.find('value').text
        elm_name = "params" if record_tag == "parameter" else "stats"
        record_type = "s"
        if is_float(record_value):
            record_type = "f"
        if is_int(record_value):
            record_type = "i"

        if record_type == "s":
            print('assert parstat_val(%s, "%s") == "%s"' % (elm_name, record_id, record_value))
        elif record_type == "i":
            print('assert parstat_val_i(%s, "%s") == %s' % (elm_name, record_id, record_value))
        elif record_type == "f":
            print('assert floats_are_close(parstat_val_f(%s, "%s"), %s)' % (elm_name, record_id, record_value))


