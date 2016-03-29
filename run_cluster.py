#!/usr/bin/env python
#
# File: run_cluster.py
#
# Author: Yuki Koyanagi


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
        files = ' '.join(fs)
    elif os.path.isfile(input):
        files = input

    flp_out = os.path.join(temp_dir, 'flp.txt')

    cmd = ('python find_local_patterns.py ' +
           files +
           ' --output ' +
           flp_out +
           ' --window-size ' + str(window_size))
    os.system(cmd)

    # run filter_bonds
    fb_out = os.path.join(temp_dir, 'filtered.txt')
    filter_bonds.filter(flp_out, fb_out, min_occurrence)

    # run get_rotations
    get_rotations.get_rotations(fb_out, out_dir, None,
                                os.path.dirname(input))

# run cluster analysis

# run as script
