"""Output formatters using prettytable."""
from __future__ import print_function

import prettytable
import six

COLUMNS = ['status', 'original', 'formatted', 'reason']
ALIGNMENTS = {
    int: 'r',
    str: 'l',
    float: 'r',
}
try:
    ALIGNMENTS[unicode] = 'l'
except NameError:
    pass


def write_output(data):

    tab = prettytable.PrettyTable(
        COLUMNS,
        print_empty=False,
    )
    tab.padding_width = 1
    tab.max_width = 60

    # Figure out the types of the columns in the
    # first row and set the alignment of the
    # output accordingly.
    data_iter = iter(data)
    first_row = next(data_iter)

    for value, name in zip(first_row, COLUMNS):
        alignment = ALIGNMENTS.get(type(value), 'l')
        tab.align[name] = alignment

    # Now iterate over the data and add the rows.
    tab.add_row(first_row)
    for row in data_iter:
        row = [r.replace('\r\n', '\n').replace('\r', ' ')
               if isinstance(r, six.string_types) else r
               for r in row]
        tab.add_row(row)

    formatted = tab.get_string(fields=COLUMNS)
    print(formatted)
    print('\n')
