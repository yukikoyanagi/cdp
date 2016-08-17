#!/bin/bash
#PBS -q q8
#PBS -S /bin/bash
#PBS -l nodes=1:ppn=8
#PBS -l walltime=24:00:00
#PBS -M yuki@qgm.au.dk
#PBS -m abe


echo "========= Job started at `date` =========="

#  Copy the inputfiles and the program to the local scratch-
#  directory on each node. One set of files per executionnode!
#  pbsdsh-flags: -s : one node at a time; -u : once on each node 
pbsdsh -s -u cp $PBS_O_WORKDIR/prot.tar.bz2  /scratch/$PBS_JOBID
pbsdsh -s -u cp $PBS_O_WORKDIR/cdp.tar.bz2    /scratch/$PBS_JOBID
pbsdsh -s -u cp $PBS_O_WORKDIR/opts.tar.bz2     /scratch/$PBS_JOBID
pbsdsh -s -u cp $PBS_O_WORKDIR/need /scratch/$PBS_JOBID
pbsdsh -s -u tar -xjf /scratch/$PBS_JOBID/prot.tar.bz2 \
    -C /scratch/$PBS_JOBID
pbsdsh -s -u tar -xjf /scratch/$PBS_JOBID/cdp.tar.bz2 \
    -C /scratch/$PBS_JOBID
pbsdsh -s -u tar -xjf /scratch/$PBS_JOBID/opts.tar.bz2 \
    -C /scratch/$PBS_JOBID


#  Set up runtime environment
module load intel/16.0.2.181
module load python/2.7.12
module load gsl/2.0

cd /scratch/$PBS_JOBID

#  Launch dispatch with these flags::
#  -T 4 :     Allocate 4 cores per subtask (set OMP_NUM_THREADS=4)
#  -e ssh :   Use ssh to spawn subtasks on other nodes
#             Remember to setup passwordless login!
#  -SS :      Log runtime statistics for each subtask
#  {1..150} : Specify arguments for the 150 subtasks: 1,...,150
dispatch -e pbs -SS -s ./cdp_opts.sh -f need -v

# Copy back outputfiles.
# Be carefull with wildcards together with pbsdsh, 
# use construction like:
#pbsdsh -s -u bash -c 'cp /scratch/$PBS_JOBID/*.out  $PBS_O_WORKDIR/'


echo "========= Job finished at `date` ==========" 
