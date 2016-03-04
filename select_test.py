#!/usr/bin/python
#
# File: select_test.py
# Description: Randomly selects a specified number of files from
#  'source' directory and copies to test directory under destination
#  directory. The unselected files are copied to training dir under
#  destination dir.
#
# Author: Yuki Koyanagi
# History:
#  2016/03/03: yk: created


from argparse import ArgumentParser
import os
import random
import shutil

# Get arguments
parser = ArgumentParser()
parser.add_argument('source',
                    help='Directory containing the files to be sorted')
parser.add_argument('destination', help='Directory for the sorted files')
parser.add_argument('--size', default=200, type=int,
                    help='The number of test files to be selected')
args = parser.parse_args()
source = args.source
dest = args.destination
size = args.size


files = os.listdir(source)
test = random.sample(files, size)
training = list(set(files) - set(test))

test_dir = dest + '/test'
training_dir = dest + '/training'
os.mkdir(test_dir)
os.mkdir(training_dir)


for f in test:
    shutil.copy('%s/%s' % (source, f), test_dir)
for f in training:
    shutil.copy('%s/%s' % (source, f), training_dir)
