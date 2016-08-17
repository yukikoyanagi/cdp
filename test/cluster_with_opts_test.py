#!/usr/bin/env python
#
# File: cluster_with_opts_test.py
#
# Time-stamp: <2016-06-29 11:16:49 au447708>
#
# Author: Yuki Koyanagi
# History:
#  2016/05/19: yk: Created


import cluster_with_opts


# temp_dir = "~/QGM/data"
out_dir = "/home/au447708/QGM/data"
input_dir = "/home/au447708/QGM/data/training"
opts_file = "/home/au447708/QGM/data/step0_opts"

cluster_with_opts.run(input_dir, out_dir, opts_file)
