#!/usr/bin/env bash
#
# File: postprocess.sh
#
# Time-stamp: <2016-11-11 10:04:55 au447708>
#
# Description: Runs post-processing of cdp data.
# To be used in spqncer:~/grendel
#
# Usage: ./postprocess.sh [path to tar file]
#
# Output: prediction.txt, stat_*.txt files in the same dir as
#  the input tar file.
#
# Author: Yuki Koyanagi
# History:
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

tar xf $tarfile
find . -name 'step*' \
    | sed 's#./##' \
    | sed 's#.tar.bz2##' \
    | parallel tar xjf {}.tar.bz2 -C assess ./{}_assess

rm step*.tar.bz2

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
