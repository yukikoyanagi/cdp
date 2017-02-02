#!/usr/bin/env bash
#
# File: postproc2.sh
#
# Time-stamp: <2017-01-25 09:09:10 au447708>
#
# Description: postprocess.sh clone for abacus output files.
#
# Author: Yuki Koyanagi
# History:
#

./predict_rotation --dir=assess2/ test/* > prediction_abc.txt
cut -f 4 prediction_abc.txt \
    | ./getstat.py -t so3 > stat_out200_so3_abc.txt
awk '$7=="L" {print $4}' prediction_abc.txt \
    | ./getstat.py -t so3 > stat_L_out200_so3_abc.txt
awk '$7!="L" {print $4}' prediction_abc.txt \
    | ./getstat.py -t so3 > stat_nonL_out200_so3_abc.txt
