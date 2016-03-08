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
#

import argparse
import collections

bond_col = 6  # Bond description is at the 7th column in the input file

# Get arguments
parser = argparse.ArgumentParser(
    description='Filters out bonds with no. of occurrence less '
    'than the specified number')
parser.add_argument('source',
                    help='File to be filtered')
parser.add_argument('destination', help='Filtered file')
parser.add_argument('minimum', type=int, help='Minimum no. of occurrence')
args = parser.parse_args()

# Read bonds
bonds = collections.Counter()
with open(args.source) as f:
    for line in f:
        cols = line.split('\t')
        bonds[cols[bond_col].strip()] += 1


# If count greater than specified, copy to output
with open(args.source) as s, open(args.destination, 'w') as d:
    for line in s:
        cols = line.split('\t')
        bond = cols[bond_col].strip()
        if bonds.get(bond) >= args.minimum:
            d.write(line)
