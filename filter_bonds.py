#!/usr/bin/env python
#
# File: filter_bonds.py
#
# Time-stamp: <2016-05-13 10:48:58 au447708>
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
#  2016/05/13: yk: Now filters by bond desc and residue class
#

import argparse
import collections

bond_col = 6  # Bond description is 7th column in the input file
res_col = 7  # Residue description is 8th column in the input file


def filter(source, dest, minimum):
    # Read bonds
    bonds = collections.Counter()
    with open(source) as f:
        for line in f:
            cols = line.split('\t')
            bond = '{b}_{r}'.format(
                b=cols[bond_col].strip(),
                r=cols[res_col].strip())
            bonds[bond] += 1

    # If count greater than specified, copy to output
    with open(source) as s, open(dest, 'w') as d:
        for line in s:
            cols = line.split('\t')
            bond = '{b}_{r}'.format(
                b=cols[bond_col].strip(),
                r=cols[res_col].strip())
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
