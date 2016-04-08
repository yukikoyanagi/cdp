#!/usr/bin/env python
#
# File: run_cluster_test.py
#
# Time-stamp: <2016-04-08 11:23:01 au447708>
#
# Author: Yuki Koyanagi
# History:
#  2016/03/29: yk: Created


import run_cluster


min_occurrence = 30
temp_dir = "/home/au447708/QGM/data/temp"
out_dir = "/home/au447708/QGM/data/out"
input = "/home/au447708/QGM/data/test"
window_size = 5

run_cluster.run(min_occurrence, temp_dir, out_dir, input, window_size)
