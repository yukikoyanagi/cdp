#!/usr/bin/env python
#
# File: cluster_with_opts.py
#
# Time-stamp: <2016-06-28 11:56:08 yuki>
#
# Author: Yuki Koyanagi
# History:
#  2016/05/19: yk: Created


import os
import argparse
import run_cluster

# We ignore all bond descriptions with less than 30 occurrences
min_occurrence = 30
window_size = 'window-size'
nearby_remotes = 'nearby-remotes'
nearby_twists = 'nearby-twists'
residue_scheme = 'residue-scheme'


def getstep(path):
    step = os.path.basename(path).split('_')[0]
    return step


def run(input_dir, out_dir, opts_file):

    assert os.path.isdir(input_dir)
    if not os.path.isdir(out_dir):
        os.mkdir(out_dir)
    assert os.path.isfile(opts_file)

    step_dir = os.path.join(out_dir, getstep(opts_file))
    os.mkdir(step_dir)
    o_dir = os.path.join(step_dir, 'out')
    os.mkdir(o_dir)
    t_dir = os.path.join(step_dir, 'temp')
    os.mkdir(t_dir)

    params = {}
    with open(opts_file) as opts:
        for opt in opts:
            opt_col = opt.split()
            if len(opt_col) > 1:
                params[opt_col[0].lstrip('-')] = opt_col[1]

    run_cluster.run(min_occurrence, t_dir, o_dir, input_dir,
                    params[window_size],
                    nearby_remotes=params[nearby_remotes],
                    nearby_twists=params[nearby_twists],
                    residue_scheme=params[residue_scheme])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input_dir', help='Directory '
                        'containing protein files')
    parser.add_argument('out_dir', help='Output directory')
    parser.add_argument('opts_file', help='.opts file with flp '
                        'parameters')
    args = parser.parse_args()
    run(args.input_dir, args.out_dir, args.opts_file)
