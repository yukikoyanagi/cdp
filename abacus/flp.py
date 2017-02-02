#!/usr/bin/env python
#
# File: flp.py
#
# Time-stamp: <2017-01-23 09:18:19 au447708>
#
# Description: Run flp on Abacus cluster. Writes 'flp.txt' file in
# each stepnnn folder.
#
# Author: Yuki Koyanagi
# History:
#

import os


def main(cdpdir, protdir, optsf, outdir):
    '''Write output from find_local_pattern using optsf'''
    params = parseopt(optsf)
    fs = [os.path.join(protdir, f) for f in os.listdir(protdir)]

    flist = [fs[i:i+200] for i in xrange(0, len(fs), 200)]
    flp_out = os.path.join(outdir, 'flp.txt')

    for s in flist:
        files = ' '.join(s)
        cmd = ('python find_local_patterns.py {f}'
               ' --window-size {w}'
               ' --nearby-remotes {r}'
               ' --nearby-twists {t}'
               ' --residue-scheme {s}'
               ' --always-include-remotes'
               ' --show-residues'
               ' >> {o}').format(
                   f=files,
                   w=str(params['window-size']),
                   r=str(params['nearby-remotes']),
                   t=str(params['nearby-twists']),
                   s=str(params['residue-scheme']),
                   o=flp_out)
        os.system(cmd)


def parseopt(optsf):
    params = {}
    with open(optsf) as opts:
        for opt in opts:
            opt_col = opt.split()
            if len(opt_col) > 1:
                params[opt_col[0].lstrip('-')] = opt_col[1]
    return params


if __name__ == '__main__':
    # default values
    cdpdir = os.path.join(os.path.expandvars('$WORK'), 'cdp')
    protdir = os.path.join(cdpdir, 'prot')
    optsdir = os.path.join(cdpdir, 'opts')

    # We'll use 3 nodes, so 3*24=72 cores avail.
    steps = [int(os.path.expandvars('$SLURM_PROCID'))+i*72
             for i in range(11)]
    for step in steps:
        fname = 'step{}_opts'.format(step)
        optsf = os.path.join(optsdir, fname)
        outdir = os.path.join(cdpdir, 'step{}'.format(step))
        if not os.path.exists(outdir):
            os.mkdir(outdir)
        main(cdpdir, protdir, optsf, outdir)
