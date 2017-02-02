#!/usr/bin/env python
#
# File: clustersize.py
#
# Time-stamp: <2016-12-07 13:11:24 au447708>
#
# Description: Analyse prediction results in terms of cluster size.
# Takes two arguments, the prediction file and 'assess' directory.
# Returns a list containing tuples of: protein id, lineno,
# SO3 distance, pattern, clustersize
#
# Author: Yuki Koyanagi
# History:
#
import os
import os.path
import itertools
import argparse
import collections

fields = ['protid', 'lineno', 'so3', 'pattern', 'step']
Prediction = collections.namedtuple('Prediction', fields)


def analyse(predf, assessd):
    """
    Return a list given prediction file and assessment dir
    """
    assert os.path.isdir(assessd),\
        '{} is not a directory'.format(assessd)
    assert os.path.isfile(predf),\
        '{} is not a file'.format(predf)

    result = []
    # Read prediction file
    with open(predf) as predf:
        lines = predf.readlines()
    for line in lines:
        args = [line.split()[i] for i in [0, 1, 3, 5, 7]]
        pred = Prediction(*args)
        rec = tuple(pred) + (getsize(pred, assessd),)
        result.append(rec)
    return result


def getsize(prediction, assessd):
    """
    Return the cluster size given step and pattern info
    """
    s = 'Processing step{}/{}'.format(prediction.step,
                                      prediction.pattern)
    f = os.path.join(assessd, 'step{}_assess'.format(prediction.step))
    with open(f) as assessf:
        for line in assessf:
            if s in line:
                t = list(itertools.islice(assessf, 5))[-1]
                break
    return t.split()[2]


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('pred_file', help='Prediction file')
    parser.add_argument('assess_dir', help='Directory containing '
                        'assess files')
    args = parser.parse_args()
    for line in analyse(args.pred_file, args.assess_dir):
        print '\t'.join(line)
