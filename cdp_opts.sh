#!/usr/bin/env bash
#
# File: cdp_opts.sh
#
# Time-stamp: <2016-10-07 09:22:58 au447708>
#
# Usage: cdp_opts.sh {step number}
#
# Description: Runs cdp analysis for the given step number.
# Call this from cdp.sh
#
# Author: Yuki Koyanagi
# History:
#  

set -e

IMPROVE_SCRIPT="improve_modebox.pl"
EVALUATE_SCRIPT="evaluate_clustering.pl"
STEP="step$1"
LOG="${STEP}.log"
MIN_NO=10

echo "$(date +'%Y-%m-%d %T'): Start clustering" >> $LOG

./cluster_with_opts.py prot . opts/${STEP}_opts -m ${MIN_NO}

echo "$(date +'%Y-%m-%d %T'): Finished clustering" >> $LOG

#cd into output dir and run post analysis
#Remenber log file!
cp $LOG ${STEP}/out
cd ${STEP}/out

echo "$(date +'%Y-%m-%d %T'): Start improve_modebox.pl" >> $LOG

cp ../../${IMPROVE_SCRIPT} .
find . -name '*Summary.txt' | \
    sed 's#_Summary.txt##' | \
    xargs ./${IMPROVE_SCRIPT}

#Note each line in the summary file should start with 
#step**/filename
p=$(dirname $(pwd))
find . -name '*Summary2.txt' | \
    xargs awk -v d="${p##*/}" '$0=d"/"FILENAME"\t"$0' | \
    sed 's|/./|/|' > ${STEP}_summary2.txt

echo "$(date +'%Y-%m-%d %T'): Finished improve_modebox.pl" >> $LOG

#We only need the summary file now, and evaluate_clustering
#require dir name to be step**

cp $LOG ../
cd ../
cp out/${STEP}_summary2.txt .
cp ../${EVALUATE_SCRIPT} .
cp ../opts/${STEP}_opts .

echo "$(date +'%Y-%m-%d %T'): Start evaluate_clustering.pl" >> $LOG

./${EVALUATE_SCRIPT} ${STEP}_summary2.txt --flp-out-dir .

echo "$(date +'%Y-%m-%d %T'): Finished evaluate_clustering.pl" >> $LOG

tar -cjf ${STEP}.tar.bz2 ./${STEP}*

cp ${STEP}.tar.bz2 ${PBS_O_WORKDIR}

#Cleanup
cd ../
rm -rf ./${STEP}
