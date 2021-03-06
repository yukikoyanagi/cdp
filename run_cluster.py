#!/usr/bin/env python
#
# File: run_cluster.py
#
# Time-stamp: <2016-05-27 10:13:48 au447708>
#
# Author: Yuki Koyanagi
#
# History:
#  2016/03/29: yk: Created
#  2016/04/08: yk: Split arg for find_local_patterns
#  2016/04/19: yk: Now runs cluster analysis
#  2016/05/19: yk: Delete temp_dir at the end
#  2016/05/24: yk: Changed outpur redirect to solve bad fd number
#  2016/05/27: yk: Run clustering for files without extenstion (".")


import os
import shutil
import filter_bonds
import get_rotations

cluster_script = 'Rasmus2.r'
cluster_file = 'StartClustSubsetVers4.txt'


def run(min_occurrence, temp_dir, out_dir, input, window_size,
        nearby_remotes=None, nearby_twists=None, residue_scheme=None):
    # create temp and out dir if they don't exist
    if not os.path.exists(temp_dir):
        os.mkdir(temp_dir)
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    # run find_local_pattern with given parameters
    # Using os.system to avoid editing find_local_patterns.py.
    if os.path.isdir(input):
        fs = []
        for file in os.listdir(input):
            fs.append(os.path.join(input, file))
    elif os.path.isfile(input):
        fs.append(input)

    # Sensible values for parameters if not given
    if nearby_remotes is None:
        nearby_remotes = 0  # No remote info
    if nearby_twists is None:
        nearby_twists = -1  # No twist info
    if residue_scheme is None:
        residue_scheme = 0  # Disable residue

    # List of files might be too long -split it
    flist = [fs[i:i+200] for i in xrange(0, len(fs), 200)]
    flp_out = os.path.join(temp_dir, 'flp.txt')

    for s in flist:
        files = ' '.join(s)
        cmd = ('python find_local_patterns.py {f}'
               ' --window-size {w}'
               ' --nearby-remotes {r}'
               ' --nearby-twists {t}'
               ' --residue-scheme {s}'
               ' --always-include-remotes'
               ' --show-residues'
               ' >> {o}').format(
                   f=files,
                   w=str(window_size),
                   r=str(nearby_remotes),
                   t=str(nearby_twists),
                   s=str(residue_scheme),
                   o=flp_out)
        os.system(cmd)

    # run filter_bonds
    fb_out = os.path.join(temp_dir, 'filtered.txt')
    filter_bonds.filter(flp_out, fb_out, min_occurrence)

    # run get_rotations
    if os.path.isdir(input):
        prot_dir = input
    else:
        prot_dir = os.path.dirname(input)
    get_rotations.get_rotations(fb_out, out_dir, prot_dir)

    # run cluster analysis
    shutil.copy(cluster_script, out_dir)
    shutil.copy(cluster_file, out_dir)
    rscript = os.path.join(out_dir, cluster_script)
    for rot_file in os.listdir(out_dir):
        if "." not in rot_file:
            f = os.path.join(out_dir, rot_file)
            out = '.'.join([os.path.splitext(f)[0], 'out'])
            cmd = ' '.join(['Rscript', rscript, f, '>', out, '2>&1'])
            os.system(cmd)

    # cleanup
    shutil.rmtree(temp_dir)

# run as script
