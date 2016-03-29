#!/usr/bin/env python
#
# File: filter_bonds.py
#
# usage: filter_bonds.py [-h] source destination minimum
#
# Filters out bonds with no. of occurrence less than the specified number
#
# positional arguments:
#   source       File to be filtered
#   destination  Filtered file
#   minimum      Minimum no. of occurrence
#
# optional arguments:
#   -h, --help   show this help message and exit
#
# Author: Yuki Koyanagi
# History:
#  2016/03/08: yk: Created
#  2016/03/17: yk: Can now be imported as module
#

import argparse
import collections

bond_col = 6  # Bond description is 7th column in the input file


def filter(source, dest, minimum):
    # Read bonds
    bonds = collections.Counter()
    with open(source) as f:
        for line in f:
            cols = line.split('\t')
            bonds[cols[bond_col].strip()] += 1

    # If count greater than specified, copy to output
    with open(source) as s, open(dest, 'w') as d:
        for line in s:
            cols = line.split('\t')
            bond = cols[bond_col].strip()
            if bonds.get(bond) >= minimum:
                d.write(line)


if __name__ == '__main__':
    # Get arguments
    parser = argparse.ArgumentParser(
        description='Filters out bonds with no. of occurrence less '
        'than the specified number')
    parser.add_argument('source',
                        help='File to be filtered')
    parser.add_argument('destination', help='Filtered file')
    parser.add_argument('minimum', type=int,
                        help='Minimum no. of occurrence')
    args = parser.parse_args()
    filter(args.source, args.destination, args.minimum)
