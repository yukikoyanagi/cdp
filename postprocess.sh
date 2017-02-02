#!/usr/bin/env bash
#
# File: postprocess.sh
#
# Time-stamp: <2017-01-25 09:18:45 au447708>
#
# Description: Runs post-processing of cdp data.
# To be used in spencer:~/grendel
#
# Usage: ./postprocess.sh [path to tar file]
#
# Output: prediction.txt, stat_*.txt files in the same dir as
#  the input tar file.
#
# Author: Yuki Koyanagi
# History:
#  2017-01-25: Updated for use with Abacus output files
#

if [ $# -eq 0 ]
then
    echo "Argument missing"
    exit 1
fi

dir=$(dirname $1)
tarfile=$(basename $1)
cd $dir
mkdir assess

tar xjf $tarfile -C assess

ln -s ~/grendel/predict_rotation .
ln -s ~/grendel/find_local_patterns.py .
ln -s ~/grendel/cdp.py .
ln -s ~/grendel/test .
ln -s ~/grendel/getstat.py .

./predict_rotation --dir=assess/ test/* > prediction.txt
cut -f 4 prediction.txt \
    | ./getstat.py -t so3 > stat_out200_so3.txt
awk '$7=="L" {print $4}' prediction.txt \
    | ./getstat.py -t so3 > stat_L_out200_so3.txt
awk '$7!="L" {print $4}' prediction.txt \
    | ./getstat.py -t so3 > stat_nonL_out200_so3.txt
