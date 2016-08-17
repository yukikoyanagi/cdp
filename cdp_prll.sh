#!/bin/bash
#
# File: cdp_prll.sh
#
# Time-stamp: <2016-08-17 09:46:18 au447708>
#
# Usage: cdp_prll.sh {step number}
#
# Description: Run cdp analysis for the given step number.
# Use this with GNU parallel: i.e.
# cat {file with step numbers} | parallel ./cdp_prll.sh {}
#
# Author: Yuki Koyanagi
# History:
#  

set -e

IMPROVE_SCRIPT="improve_modebox.pl"
EVALUATE_SCRIPT="evaluate_clustering.pl"
STEP="step$1"

echo "$(date +"%Y-%m-%d %T"): Starting ${STEP}"

./cluster_with_opts.py prot . opts/${STEP}_opts

echo "$(date +"%Y-%m-%d %T"): Finished clustering for ${STEP}"

#cd into output dir and run post analysis
#cd /scratch/${PBS_JOBID}/${STEP}/out
cd ${STEP}/out

cp ../../${IMPROVE_SCRIPT} .
find . -name '*Summary.txt' | \
    sed 's#_Summary.txt##' | \
    xargs ./${IMPROVE_SCRIPT}

echo "$(date +"%Y-%m-%d %T"): Finished improve script for ${STEP}"

#Note each line in the summary file should start with 
#step**/filename
p=$(dirname $(pwd))
find . -name '*Summary2.txt' | \
    xargs awk -v d="${p##*/}" '$0=d"/"FILENAME"\t"$0' | \
    sed 's|/./|/|' > ${STEP}_summary2.txt

echo "$(date +"%Y-%m-%d %T"): Finished evaluation for  ${STEP}"

#We only need the summary file now, and evaluate_clustering
#require dir name to be step**

cd ../  # Now in ${STEP} dir
cp out/${STEP}_summary2.txt .
cp ../${EVALUATE_SCRIPT} .
cp ../opts/${STEP}_opts .
./${EVALUATE_SCRIPT} ${STEP}_summary2.txt --flp-out-dir .

tar cjf ${STEP}.tar.bz2 ./${STEP}*

cp ${STEP}.tar.bz2 ../

#Cleanup
cd ../
rm -rf ./${STEP}

echo "$(date +"%Y-%m-%d %T"): Finished ${STEP}"
