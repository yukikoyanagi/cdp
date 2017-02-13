#!/usr/bin/env bash
#
# File: submit2.sh
#
# Time-stamp: <2017-02-03 15:41:31 au447708>
#
# Author: Yuki Koyanagi
# History:
#
n=0
for i in $(cat unfinished)
do
    if [ $n -le 4 ]
    then
	rm -f cls-${i}-50.out
	sbatch -J cls-${i}-50 -o cls-${i}-50.out \
	       --time=6:00:00 clstrab.sh
	(( n++ ))
    else
	rm -f cls-${i}-50.out
	sbatch -J cls-${i}-50 -o cls-${i}-50.out \
	       --time=6:00:00 --begin=now+6hours clstrab.sh
    fi
done
