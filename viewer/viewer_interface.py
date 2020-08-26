from __future__ import absolute_import, division, print_function

import sys

from dials.array_family import flex
from dials.viewer.slice_viewer import show_reflections


def extract_n_show(table):
    show_reflections(table, two_windows=True)


if __name__ == "__main__":
    pick_name = sys.argv[1]

    table = flex.reflection_table.from_file(pick_name)
    extract_n_show(table)
