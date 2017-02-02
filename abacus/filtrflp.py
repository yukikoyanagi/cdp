#!/usr/bin/env python
#
# File: filtrflp.py
#
# Time-stamp: <2017-01-23 11:39:18 au447708>
#
# Filters out bond patterns fewer than the specified number. Based on
# filter_bonds.py adapted for running on Abacus
#
# Author: Yuki Koyanagi
# History:
#

import collections
import os

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
    cutoff = 4  # Bond pattern must have freq. >= this number
    jobname = os.path.expandvars('$SLURM_JOB_NAME')
    if len(jobname.split('-')) > 1:
        try:
            cutoff = int(jobname.split('-')[-1])
        except ValueError:
            # jobname contains '-', but the last part is not int
            pass

    cdpdir = os.path.join(os.path.expandvars('$WORK'), 'cdp')
    flpfn = 'flp.txt'

    # Use 1 node, 24 cores
    steps = [int(os.path.expandvars('$SLURM_PROCID'))+i*24
             for i in range(33)]
    for step in steps:
        stepdir = os.path.join(cdpdir, 'step{}'.format(step))
        outdir = os.path.join(stepdir, 'n{}'.format(cutoff))
        os.mkdir(outdir)
        outf = os.path.join(outdir, 'filtered.txt')
        sf = os.path.join(stepdir, flpfn)
        filter(sf, outf, cutoff)
