#!/usr/bin/env bash
#
# File: submit.sh
#
# Time-stamp: <2017-02-02 20:07:33 yuki>
#
# Author: Yuki Koyanagi
# History:
#
n=0
for step in $(seq 0 49)
do
    if [ $step -le 9 ]
    then
	sbatch -J cls-${step}-50 -o cls-${step}-50.out \
	       --time=6:00:00 clstrab.sh
    elif [ $step -gt 9 ] && [ $step -le 19 ]
    then
	sbatch -J cls-${step}-50 -o cls-${step}-50.out \
	       --time=6:00:00 --begin=now+3hours clstrab.sh
    elif [ $step -gt 19 ] && [ $step -le 29 ]
    then
	sbatch -J cls-${step}-50 -o cls-${step}-50.out \
	       --time=6:00:00 --begin=now+6hours clstrab.sh
    elif [ $step -gt 29 ] && [ $step -le 39 ]
    then
	sbatch -J cls-${step}-50 -o cls-${step}-50.out \
	       --time=6:00:00 --begin=now+9hours clstrab.sh
    else
	sbatch -J cls-${step}-50 -o cls-${step}-50.out \
	       --time=6:00:00 --begin=now+12hours clstrab.sh
    fi
done
