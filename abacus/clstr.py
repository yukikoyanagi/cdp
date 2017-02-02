#!/usr/bin/env python
#
# File: clstr.py
#
# Time-stamp: <2017-01-28 22:18:35 yuki>
#
# Description: Run cluster analysis on Abacus. Step no's are obtained
#  from $SLURM_JOB_NAME, which should be in the form {name}.start.end
#  or {name}-group#-#ofgroups.
#  Change minn parameter as required.
#
# Author: Yuki Koyanagi
# History:
#  2017-01-16: Created
#  2017-01-18: Submit job for sets of patterns to avoid starting
#   too many threads.
#  2017-01-20: Use subprocess module instead of os.system() to run
#   improve_modebox script.
#
import os
import cPickle as pickle
import subprocess
import pp
from itertools import islice, tee

stepn = 100
minn = 1


# Set up servers
ppservers = open('/tmp/nodelist').read().strip().split()
ppservers = tuple(pp + ':2048' for pp in ppservers)
job_server = pp.Server(0, ppservers=ppservers)


def chunk(data, n=24*16):
    '''Splits input data (dict) into n equal chunks.'''
    it = iter(data)
    for i, iterator in enumerate(tee(it, n)):
        yield {k: data[k] for k in islice(iterator, i, None, n)}


def runclstrs(data, step):
    d = {}
    for pattern in data:
        # If R script has error runclstr returns None
        summ = runclstr(pattern, data[pattern], step)
        if summ:
            d[pattern] = summ
    return step, d


def runclstr(pattern, data, step):
    # Files and dirs
    rscript = os.path.join(os.path.expandvars('$SLURM_SUBMIT_DIR'),
                           'Rasmus2.r')
    imprv = os.path.join(os.path.expandvars('$SLURM_SUBMIT_DIR'),
                         'improve_modebox.pl')
    stepd = os.path.join(os.path.expandvars('$LOCALSCRATCH'),
                         'step{}'.format(step))
    rotf = os.path.join(stepd, pattern)

    if not os.path.exists(stepd):
        try:
            os.mkdir(stepd)
        except OSError:
            # stepd now exists -prob. created by another worker proc.
            pass

    with open(rotf, 'w') as f:
        f.write('\n'.join(['\t'.join(d) for d in data]))

    try:
        subprocess.check_output(['Rscript', rscript, rotf],
                                stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as cpe:
        print 'Error while processing step{}/{}'.format(step, pattern)
        print cpe.output
        return None

    # sumf = rotf + '_Summary.txt'

    cmd = ' '.join([imprv, rotf])
    os.system(cmd)

    sumf = rotf + '_Summary2.txt'

    with open(sumf) as f:
        res = f.read()

    return res


# Parse jobname to get start and end step no's
jobname = os.path.expandvars('$SLURM_JOB_NAME')
if '.' in jobname:
    _, startstep, endstep = jobname.split('.')
    steps = range(int(startstep), int(endstep)+1)
elif '-' in jobname:
    _, grp, total = jobname.split('-')
    steps = range(int(grp), 792, int(total))
else:
    raise SyntaxError('SLURM_JOB_NAME not set correctly.')

cdpdir = os.path.join(os.path.expandvars('$WORK'), 'cdp')

# Submit jobs to server
clsts = []

for step in steps:
    # Load the rotation data
    workdir = os.path.join(cdpdir,
                           'step{}'.format(step),
                           'n{}'.format(minn))
    # Test workdir
    # workdir = os.path.join(os.path.expandvars('$WORK'), 'test')
    rotfile = os.path.join(workdir, 'rotations.pkl')
    with open(rotfile, 'rb') as r:
        rotations = pickle.load(r)

    # Submit jobs for subset of data to avoid too many threads
    for subset in chunk(rotations):
        clstr = job_server.submit(runclstrs,
                                  (subset, step),
                                  (runclstr,),
                                  ('os', 'subprocess'))
        clsts.append(clstr)

job_server.wait()
job_server.print_stats()

# Get the results in dict of ditcs; {step:{pattern:content}}
summary = {}
for clst in clsts:
    step, d = clst()
    if step in summary:
        summary[step].update(d)
    else:
        summary[step] = d

for step in summary:
    outf = os.path.join(cdpdir,
                        'step{}'.format(step),
                        'n{}'.format(minn),
                        'summary.pkl')
    with open(outf, 'wb') as o:
        pickle.dump(summary[step], o)

# job_server.destroy()
