#!/usr/bin/env bash

tar cjf cdp.tar.bz2 \
    cdp_opts.sh cdp.py cluster_with_opts.py \
    evaluate_clustering.pl filter_bonds.py \
    find_local_patterns.py get_rotations.py \
    improve_modebox.pl run_cluster.py \
    Rasmus2.r StartClustSubsetVers4.txt
