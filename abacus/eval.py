#!/usr/bin/env python
#
# File: eval.py
#
# Time-stamp: <2017-01-23 12:36:37 au447708>
#
# Description: Run evaluate_clustering on Abacus
#
# Author: Yuki Koyanagi
# History:
#
import os
import subprocess
import cPickle as pickle


if __name__ == '__main__':
    cutoff = 4
    jobname = os.path.expandvars('$SLURM_JOB_NAME')
    if len(jobname.split('-')) > 1:
        try:
            cutoff = int(jobname.split('-')[-1])
        except ValueError:
            # jobname contains '-', but the last part is not int
            print ("Warning: Can't parse SLURM_JOB_NAME. "
                   "Using cutoff={}.".format(cutoff))
            pass

    # Use 1 node, 24 cores
    steps = [int(os.path.expandvars('$SLURM_PROCID'))+i*24
             for i in range(33)]
    for step in steps:
        outdir = os.path.join(os.path.expandvars('$WORK'),
                              'cdp',
                              'step{}'.format(step),
                              'n{}'.format(cutoff))
        sumf = os.path.join(outdir, 'summary.pkl')
        with open(sumf, 'rb') as f:
            summary = pickle.load(f)

        lines = []
        for pattern in summary:
            prep = 'step{s}/{p}_Summary2.txt\t'.format(
                s=step,
                p=pattern
            )
            # Exclude the last item which is empty when we split at
            # '\n' character
            lst = summary[pattern].split('\n')[:-1]
            for l in lst:
                lines.append(prep + l)

        tempdir = os.path.expandvars('$LOCALSCRATCH')
        tempf = os.path.join(tempdir,
                             'step{}_summary2.txt'.format(step))
        with open(tempf, 'w') as o:
            o.write('\n'.join(lines))

        optsdir = os.path.join(os.path.expandvars('$WORK'),
                               'cdp', 'opts')
        perlscript = os.path.join(
            os.path.expandvars('$SLURM_SUBMIT_DIR'),
            'evaluate_clustering.pl')
        try:
            subprocess.check_output([perlscript,
                                     tempf,
                                     '--flp-out-dir', optsdir,
                                     '--output-dir', outdir],
                                    stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as cpe:
            print 'Error while processing {}'.format(tempf)
            print cpe.output
            continue
