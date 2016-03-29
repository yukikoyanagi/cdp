#!/usr/bin/env python
#
# File: get_rotations.py
#
# usage: get_rotations.py [-h] [--suffix SUFFIX] input outdir prot_dir
#
# Get rotation vector for each bond in input file. Output is one file
# per bond description.
#
# positional arguments:
#   input            Input file containing bond information.
#   outdir           Output file directory.
#   prot_dir         Directory containing original protein data.
#
# optional arguments:
#   -h, --help       show this help message and exit
#   --suffix SUFFIX  Suffix for output files. (default: rot)
#
# Author: Yuki Koyanagi
# History:
#  2016/03/08: yk: Created
#  2016/03/16: yk: Made suffix optional. Added help & usage comment.
#  2016/03/21: yk: Output per bond description rather than per protein
#


import argparse


def get_rotations(input, outdir, suffix, prot_dir):
    """
    """
    # Build list of bonds from input
    bonds = []
    with open(input) as f:
        for line in f:
            cols = line.split()
            protein = cols[0]
            l_num = cols[1]
            pattern = cols[6]
            bonds.append((protein, l_num, pattern))

    # Build dict (protein:list of rotations) from list.
    # Assumes rotation vectors are in cols 16-19.
    rotations = dict()
    for bond in bonds:
        with open('{}/{}.txt'.format(prot_dir, bond[0])) as p:
            for i, line in enumerate(p):
                if i == int(bond[1])-1:
                    cols = line.split()
                    rot = (cols[15], cols[16], cols[17], cols[18])
                    if bond[2] in rotations:
                        rotations[bond[2]].append(rot)
                    else:
                        rotations[bond[2]] = [rot]

    for vs in rotations.iteritems():
        with open('{}/{}_{}.txt'.format(
                outdir, vs[0], suffix), 'w') as o:
            o.write('\n'.join(
                '{}\t{}\t{}\t{}'.format(v[0], v[1], v[2], v[3])
                for v in vs[1]))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Get rotation vector for each bond in '
        'input file. Output is one file per bond description.')
    parser.add_argument('input', help='Input file containing '
                        'bond information.')
    parser.add_argument('outdir', help='Output file directory.')
    parser.add_argument('prot_dir', help='Directory containing '
                        'original protein data.')
    parser.add_argument('--suffix', help='Suffix for output files. '
                        '(default: rot)', default='rot')
    args = parser.parse_args()
    get_rotations(args.input, args.outdir, args.suffix, args.prot_dir)
