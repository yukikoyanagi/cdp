#!/usr/bin/env python
#
# File: run_cluster.py
#
# Time-stamp: <2016-04-08 11:39:02 au447708>
#
# Author: Yuki Koyanagi
#
# History:
#  2016/03/29: yk: Created
#  2016/04/08: yk: Split arg for find_local_patterns


import os
import filter_bonds
import get_rotations


def run(min_occurrence, temp_dir, out_dir, input, window_size):
    # create temp and out dir if they don't exist
    if not os.path.exists(temp_dir):
        os.mkdir(temp_dir)
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    # run find_local_pattern with given parameters
    # Using os.system to avoid editing find_local_patterns.py.
    if os.path.isdir(input):
        fs = []
        for file in os.listdir(input):
            fs.append(os.path.join(input, file))
    elif os.path.isfile(input):
        fs.append(input)

    # List of files might be too long -split it
    flist = [fs[i:i+200] for i in xrange(0, len(fs), 200)]
    flp_out = os.path.join(temp_dir, 'flp.txt')

    for s in flist:
        files = ' '.join(s)
        cmd = ('python find_local_patterns.py ' +
               files +
               ' --window-size ' + str(window_size) +
               ' >> {}'.format(flp_out))
        os.system(cmd)

    # run filter_bonds
    fb_out = os.path.join(temp_dir, 'filtered.txt')
    filter_bonds.filter(flp_out, fb_out, min_occurrence)

    # run get_rotations
    if os.path.isdir(input):
        prot_dir = input
    else:
        prot_dir = os.path.dirname(input)
    get_rotations.get_rotations(fb_out, out_dir, prot_dir)

    # run cluster analysis

# run as script
