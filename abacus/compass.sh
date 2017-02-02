#!/usr/bin/env bash
#
#SBATCH --account austmathjea_slim      # account
#SBATCH --nodes 1                 # number of nodes
#SBATCH --time 0:30:00            # max time (HH:MM:SS)
#
# File: compass.sh
#
# Time-stamp: <>
#
# Author: Yuki Koyanagi
# History:
#
n=5

start=$(date +%s)
echo Start time: "$(date)"

mkdir "${WORK}/cdp/n${n}assess"

for i in $(seq 0 791)
do
    cp "${WORK}/cdp/step${i}/n${n}/step${i}_assess" "${WORK}/cdp/n${n}assess/"
done

cd "${WORK}/cdp/n${n}assess"
tar cjf "../n${n}assess.tar.bz2" ./*
cd ../
rm -rf "${WORK}/cdp/n${n}assess"

end=$(date +%s)
echo End time: "$(date)"
dur=$(date -d "0 $end sec - $start sec" +%T)
echo Duration: "$dur"
