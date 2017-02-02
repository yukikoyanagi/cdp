#!/usr/bin/env bash
#
#SBATCH --account austmathjea_slim      # account
#SBATCH --nodes 1                 # number of nodes
#SBATCH --ntasks-per-node 24      # number of MPI tasks per node
#SBATCH --time 0:30:00            # max time (HH:MM:SS)
#
# File: flpab.sh
#
# Time-stamp: <>
#
# Author: Yuki Koyanagi
# History:
#

echo Running on "$(hostname)"
echo Available nodes: "$SLURM_NODELIST"
echo Slurm_submit_dir: "$SLURM_SUBMIT_DIR"
echo Start time: "$(date)"

# Load the modules previously used when compiling the application
module purge
module load python-intel

# Start in total [nodes]*24 MPI ranks on all available CPU cores
# srun python ./flp.py
# srun python ./filtrflp.py
# srun python ./rotab.py
srun python ./eval.py

echo Done: "$(date)"
