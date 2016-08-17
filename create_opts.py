#!/usr/bin/env python
#
# File: create_opts.py
#
# Time-stamp: <2016-06-29 10:04:45 au447708>
#
# Usage: create_opts.py
#
# Creates _opts files in the current directory
#
# Author: Yuki Koyanagi
# History:
#  2016/06/27: yk: Created


w_min = 0
w_max = 10
w_step = 1
r_min = 0
r_step = 1
residue = [0, 4, 3, 2]

opts = [(w, r, t, s)
        for w in xrange(w_min, w_max+1, w_step)
        for r in xrange(r_min, w+1, r_step)
        for t in [-1, 0, w]
        for s in residue]

step = 0
for opt in opts:
    fname = 'step{}_opts'.format(step)
    with open(fname, 'w') as f:
        s = ['--window-size {}'.format(opt[0]),
             '--nearby-remotes {}'.format(opt[1]),
             '--nearby-twists {}'.format(opt[2]),
             '--residue-scheme {}'.format(opt[3]),
             '--always-include-remotes',
             '--show-residues']
        f.write('\n'.join(s))
    step += 1
