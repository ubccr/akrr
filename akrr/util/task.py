"""
Utils for task
"""
from prettytable import PrettyTable


def wrap_str_dict(s, width=20):
    if s is None:
        return "None"
    if s is "NA":
        return "NA"
    import textwrap
    return "\n".join(textwrap.wrap(str(eval(s)), width=width))


def wrap_text(s, width=20):
    if s is None:
        return "None"
    import textwrap
    return "\n".join(textwrap.wrap(s, width=width))


def pack_details(result, template):
    table = PrettyTable(border=False, header=False)
    table.field_names = ["F1", "F2"]
    table.align["F1"] = "l"
    table.align["F2"] = "l"
    for title, (key, align, convert) in template.items():
        table.add_row([title + ":", convert(result.get(key, "NA"))])

    return str(table)


def get_task_list_table(tasks, table_title_key):
    table = PrettyTable()
    for title, (key, align, convert) in table_title_key.items():
        if type(key) is str:
            table.add_column(title, [convert(r.get(key, "NA")) for r in tasks])
        else:
            table.add_column(title, [convert(r, key) for r in tasks])
        table.align[title] = align
    return table
