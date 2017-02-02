#!/usr/bin/env python
#
# File: rotab.py
#
# Time-stamp: <2017-01-23 11:41:28 au447708>
#
# Run get_rotations on Abacus, for the given min. freq. limit.
# Output is a python pickle file of dict {pattern: list of rotations}
#
# Author: Yuki Koyanagi
# History:
#

import cPickle as pickle
import os
import shutil


def main(infile, outfile, protdir):
    # Build list of bonds from input file
    bonds = []
    with open(infile) as f:
        for line in f:
            cols = line.split()
            protein = cols[0]
            l_num = cols[1]
            dist = cols[5]
            pattern = cols[6]
            residue = cols[7]
            bonds.append((protein, l_num, dist, pattern, residue))

    # Load protein files in protdir into dict {protein/l_num: rot}
    # Assumes rotation vectors are in cols 16-19
    prots = {}
    for protf in os.listdir(protdir):
        with open(os.path.join(protdir, protf)) as f:
            protn = os.path.splitext(protf)[0]
            for i, line in enumerate(f):
                lnum = i+1
                cols = line.split()
                rot = (cols[15], cols[16], cols[17], cols[18])
                protln = '{}/{}'.format(protn, lnum)
                prots[protln] = rot

    # Create rotation dict {pattern: list of rotations}
    rots = {}
    for protein, lnum, dist, pattern, residue in bonds:
        s = '{}/{}'.format(protein, lnum)
        desc = '{}_{}_{}'.format(pattern, dist, residue)
        if desc in rots:
            rots[desc].append(prots[s])
        else:
            rots[desc] = [prots[s]]

    with open(outfile, 'wb') as o:
        pickle.dump(rots, o)


if __name__ == '__main__':
    # default values
    cdpdir = os.path.join(os.path.expandvars('$WORK'), 'cdp')
    protdir = os.path.join(cdpdir, 'prot')
    filtf = 'filtered.txt'
    cutoff = 4
    jobname = os.path.expandvars('$SLURM_JOB_NAME')
    if len(jobname.split('-')) > 1:
        try:
            cutoff = int(jobname.split('-')[-1])
        except ValueError:
            # jobname contains '-', but the last part is not int
            pass

    # copy input protein files
    dstdir = os.path.join(os.path.expandvars('$LOCALSCRATCH'),
                          os.path.expandvars('$SLURM_PROCID'))
    dstprot = os.path.join(dstdir, 'prot')
    shutil.copytree(protdir, dstprot)

    steps = [int(os.path.expandvars('$SLURM_PROCID'))+i*24
             for i in range(33)]
    for step in steps:
        filtdir = os.path.join(cdpdir,
                               'step{}'.format(step),
                               'n{}'.format(cutoff))
        inf = os.path.join(filtdir, filtf)
        shutil.copy(inf, dstdir)
        locinf = os.path.join(dstdir, filtf)
        outf = os.path.join(filtdir, 'rotations.pkl')
        main(locinf, outf, dstprot)
