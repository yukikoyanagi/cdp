#!/usr/bin/env bash
#
# File: submit.sh
#
# Time-stamp: <2017-01-26 17:00:03 au447708>
#
# Author: Yuki Koyanagi
# History:
#
n=0
for step in $(cat missing)
do
    if [ $n -le 4 ]
    then
	sbatch -J cls-${step}-100 -o cls-${step}-100.out \
	       --time=5:00:00 clstrab.sh
	((n++))
    elif [ $n -gt 4 ] && [ $n -le 14 ]
    then
	sbatch -J cls-${step}-100 -o cls-${step}-100.out \
	       --time=5:00:00 --begin=now+5hours clstrab.sh
	((n++))
    elif [ $n -gt 14 ] && [ $n -le 29 ]
    then
	sbatch -J cls-${step}-100 -o cls-${step}-100.out \
	       --time=5:00:00 --begin=now+10hours clstrab.sh
	((n++))
    else
	sbatch -J cls-${step}-100 -o cls-${step}-100.out \
	       --time=5:00:00 --begin=now+15hours clstrab.sh
    fi
done
