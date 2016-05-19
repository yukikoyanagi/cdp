#!/usr/bin/env python
#
# File: cluster_with_opts_test.py
#
# Time-stamp: <2016-05-19 12:56:18 au447708>
#
# Author: Yuki Koyanagi
# History:
#  2016/05/19: yk: Created


import cluster_with_opts


temp_dir = "/home/au447708/QGM/data/temp2"
out_dir = "/home/au447708/QGM/data/out2"
input_dir = "/home/au447708/QGM/data/test"
opts_file = "/home/au447708/QGM/data/out2/step1_opts"

cluster_with_opts.run(input_dir, out_dir, temp_dir, opts_file)
