#!/usr/bin/python
#
# File: find_local_patterns.py
# Author: Rasmus Villemoes
# History:
#  2016/03/04: yk: added output argument

import sys
import os
import platform
import itertools

import string
import gc
import re


from cdp import *

window_size = 3

nearby_remotes = 2
remote_sign = False
always_include_remotes = False
nearby_twists = -1

residue_scheme = 0

pid = os.getpid()
hostname = platform.node()


# Hm, ok, assuming that "i" was late enough in the alphabet so that
# we'd never conflict with the a,b,c,... enumeration of local Hbonds
# was too naive. Let's use variables for this, so it's easier to
# change in the future.
isolated_N_char = "I"
isolated_C_char = "X"
isolated_O_char = "I"
remote_N_char = "R"
remote_C_char = "R" # only needed if we ever try using tertiary info again...
remote_O_char = "R"

# Tuples for easy indexing via a mod 3 computation
isolated_char = (isolated_N_char, isolated_C_char, isolated_O_char)
remote_char = (remote_N_char, remote_C_char, remote_O_char)

# A residue scheme is a mapping defining groups of "similar"
# residues. The trivial scheme is the one where each residue is mapped
# to its own group. We represent a group simply by its first
# member. It is up to the user to keep track of which scheme was used.
def create_residue_scheme(*args):
    scheme = dict()
    for x in args:
        for c in x:
            scheme[c] = x[0]
    return scheme

# There are a few X and ? in the data (these will come out as X), so
# make sure X is also mapped to something. We always just assign it as
# a last group of its own, except in the first catch-all scheme, we
# actually use X as the generic symbol, so that one can effectively
# disable taking residues into account by using --residue-scheme 0
# (one wil then always just get XXXX).
residue_schemes = [
    create_residue_scheme("XLVIFMAGSCEKRDTYNQHWP"),
    create_residue_scheme("L", "A", "V", "I", "E", "G", "K", "R", "S", "D", "T", "F", "Y", "N", "Q", "P", "H", "M", "W", "C", "X"),
    create_residue_scheme("LVIFM", "AGSC", "EKRDTYNQHW", "P", "X"),
    create_residue_scheme("LVIFM", "AGSC", "EKRDTYNQHWP", "X"),
    create_residue_scheme("LVIFMAGSC", "EKRDTYNQHWP", "X"),
]

def simplify_residues(s):
    d = residue_schemes[residue_scheme]
    return "".join(d[c] for c in s)

# def spec_to_str(spec, leftmost):
#     specstr = "%s: %s" % (mod3_to_atom[leftmost % 3],
#                           "; ".join(spec));
#     return specstr

# Since we need to describe somewhat complex local patterns, I no
# longer think it is feasible to stick to precisely one character per
# backbone atom. Instead, let's say that that each backbone atom is
# represented by some letter, optionally followed by a sequence of
# zero or more non-letters (digits or some of @%-+ or whatever we find
# useful; just try to stay away from shell-unfriendly chars such as #
# and $).

# 
# nearby_remotes: Only include remote bonds attached to one of the (up
# to) 4*nearby_remotes N/O atoms closest to the a-bond, ignore all
# other remote bonds. Set to a large value to include all remote
# bonds. Set to 0 to ignore all remote bonds.
#
# remote_sign: If false (default), instead of using + or - to indicate
# whether the other end of a remote bond is upstream or downstream in
# the backbone, simply use the letter R. This can be used independent
# of the nearby_remotes
#
# ignore_remotes_if_local: If there is at least one other local bond
# (besides the a-bond) within the window (or connecting the two
# segments), ignore _all_ remote bonds.
#

# def count_uppercase(s):
#     c = 0
#     for x in s:
#         if re.match("[A-Z]", x):
#             c += 1
#     return c
# def count_lowercase(s):
#     c = 0
#     for x in s:
#         if re.match("[a-z]", x):
#             c += 1
#     return c

def handle_nearby_remotes(central_char, s, leftmost):
    if s is None:
        return None

    # s is a list of backbone atom specs; each consist of a single
    # letter followed by zero or more special characters. Lower-case
    # letters are for N and O atoms, upper-case for Calphas.

    apos = [i for i in range(len(s)) if s[i][0] == central_char]
    assert(len(apos) == 1 or len(apos) == 2)

    for i in range(len(s)):
        if s[i][0] not in remote_char:
            continue
        # Count the number of atoms between position i and each of the
        # a-positions.
        nearby = False
        for a in apos:
            if i < a and a - i <= nearby_remotes:
                nearby = True
            elif i > a and i - a <= nearby_remotes:
                nearby = True
        if not nearby:
            s[i] = isolated_char[(leftmost + i) % 3]

    return s

def handle_nearby_twists(central_char, s, leftmost):
    if s is None:
        return None

    # A twisted H-bond is indicated by a lowercase letter followed
    # somewhere by the 'flag' ~. If we are too far from the central
    # bond, we want to just delete the ~. If we are close enough, the
    # leading char should be replaced by its opposite cousin (a by z,
    # b by y etc.).
    #
    # Note that this is actually somewhat broken, since the two ends
    # of a bond may end up being denoted by different characters. So
    # for now one should only use a value of --nearby-twists of either
    # -1 (disable, the default), 0 (only annotate the a-bond), or
    # "infinity" (in practice, the selected window size).

    apos = [i for i in range(len(s)) if s[i][0] == central_char]
    assert(len(apos) == 1 or len(apos) == 2)

    for i in range(len(s)):
        if "~" not in s[i]:
            continue

        # Count the number of atoms between position i and each of the
        # a-positions.
        nearby = False
        for a in apos:
            if i <= a and a - i <= nearby_twists:
                nearby = True
            elif i >= a and i - a <= nearby_twists:
                nearby = True
        new = s[i].replace("~", "")
        if nearby:
            s[i] = chr(ord("z") - (ord(new[0]) - ord("a"))) + new[1:]
        else:
            s[i] = new

    return s



def read_whitelist_files(l):
    wl = dict()
    for f in l:
        for line in open(f):
            fields = line.strip().split()
            prot = fields[0]
            lineno = int(fields[1])
            if prot not in wl:
                wl[prot] = set()
            wl[prot].add(lineno)
    return wl

def normalized_toptype(central_char, specL, specL_index, specR = None, specR_index = None):
    specL = handle_nearby_remotes(central_char, specL, specL_index)
    specR = handle_nearby_remotes(central_char, specR, specR_index)
    specL = handle_nearby_twists(central_char, specL, specL_index)
    specR = handle_nearby_twists(central_char, specR, specR_index)

    top = "".join(specL)
    if specR is not None:
        top += ":"
        top += "".join(specR)

    if not remote_sign:
        top = re.sub("[-+]", "", top)

    if not always_include_remotes:
        if ((specR is None and re.search("[b-k]", top)) or
            re.search(r"([b-k])[^:]*:.*\1", top)):
            top = re.sub(remote_N_char + "[-+]?", isolated_N_char, top)
            top = re.sub(remote_C_char + "[-+]?", isolated_C_char, top)
            top = re.sub(remote_O_char + "[-+]?", isolated_O_char, top)
        
    return str(window_size) + top


def describe_local_pattern(prot, bond):
    hbond_char = (x for x in string.ascii_lowercase)
    tbond_char = (x for x in string.ascii_uppercase)

    donor = bond.donor
    accptr = bond.accptr
    left = min(donor, accptr)
    right = max(donor, accptr)

    if isinstance(bond, Hbond):
        central_char = hbond_char.next()
    else:
        central_char = tbond_char.next()

    if bond.is_twisted():
        central_str = central_char + "~"
    else:
        central_str = central_char

    # We will look at a window window_size atoms on either side of the
    # two endpoints. These two windows may overlap (or be just
    # adjacent), in which case we create one long segment; otherwise,
    # we create two segments of length 2*window_size+1, with our Hbond
    # joining the two middle atoms.

    if (left + window_size + 1 >= right - window_size):
        # One long segment. We need [left-window_size
        # .. right+window_size], which means a length of
        # right-left+2*window_size+1. We translate from protein
        # indices to segment indices by subtracting segleft.
        segleft = left-window_size
        segright = right+window_size
        spec = [None]*((segright-segleft)+1)

        # Add the spec for our central bond.
        spec[left-segleft] = central_str
        spec[right-segleft] = central_str

        # Now loop over all the other atoms, and check if they have an Hbond or a Tbond.
        for i in range(segleft, segright+1):
            # Skip if we've already decided the spec at this index
            if spec[i-segleft] is not None:
                continue

            chargen = tbond_char if i % 3 == 1 else hbond_char
            bond = prot.get_bond(i)
            if bond is None:
                continue
            assert(isinstance(bond, Tbond) or isinstance(bond, Hbond))
            j = bond.other_end(i)
            assert(i != j)
            if segleft <= j and j <= segright:
                # A "local" bond
                char = chargen.next()
                if bond.is_twisted():
                    char += "~"
                spec[i-segleft] = char
                spec[j-segleft] = char
            else:
                # A "remote" bond
                spec[i-segleft] = remote_char[i % 3]
                spec[i-segleft] += "+" if i < j else "-"

        # All indices where we did not place an Hbond are isolated or correspond to Calphas.
        for i in range(len(spec)):
            if spec[i] is None:
                spec[i] = isolated_char[(i + segleft) % 3]

        return normalized_toptype(central_char, spec, segleft)

        # print "\t".join((prot.name, str(hb.linenumber), str(hb.donor/3), str((hb.accptr-2)/3), 
        #                  hb.cluster, hb.length_class(), normalized_toptype(spec)))

    else:
        specL = [None]*(2*window_size+1)
        specR = [None]*(2*window_size+1)
        segLL = left-window_size
        segLR = left+window_size
        segRL = right-window_size
        segRR = right+window_size
        assert(segLR + 1 < segRL)

        specL[left-segLL] = central_str
        specR[right-segRL] = central_str
        
        for i in range(segLL, segLR+1):
            # Skip if we've already decided the spec at this index
            if specL[i-segLL] is not None:
                continue

            chargen = tbond_char if i % 3 == 1 else hbond_char
            bond = prot.get_bond(i)
            if bond is None:
                continue
            assert(isinstance(bond, Tbond) or isinstance(bond, Hbond))
            j = bond.other_end(i)
            assert(i != j)
            if segLL <= j and j <= segLR:
                # A "local" bond
                char = chargen.next()
                if bond.is_twisted():
                    char += "~"
                specL[i-segLL] = char
                assert(specL[j-segLL] is None)
                specL[j-segLL] = char
            elif segRL <= j and j <= segRR:
                char = chargen.next()
                if bond.is_twisted():
                    char += "~"
                specL[i-segLL] = char
                assert(specR[j-segRL] is None)
                specR[j-segRL] = char
            else:
                # A "remote" bond
                specL[i-segLL] = remote_char[i % 3]
                specL[i-segLL] += "+" if i < j else "-"


        for i in range(segRL, segRR+1):
            # Skip if we've already decided the spec at this index
            if specR[i-segRL] is not None:
                continue

            chargen = tbond_char if i % 3 == 1 else hbond_char
            bond = prot.get_bond(i)
            if bond is None:
                continue
            assert(isinstance(bond, Tbond) or isinstance(bond, Hbond))
            j = bond.other_end(i)
            assert(i != j)
            if segLL <= j and j <= segLR:
                # A bond to the other segment; should have been handled above
                assert(0)
                char = chargen.next()
                specR[i-segRL] = char
                specL[j-segLL] = char
                print "!!! i=%d, j=%d, char = %s" % (i, j, char)

            elif segRL <= j and j <= segRR:
                char = chargen.next()
                if bond.is_twisted():
                    char += "~"
                specR[i-segRL] = char
                assert(specR[j-segRL] is None)
                specR[j-segRL] = char
            else:
                # A "remote" bond
                specR[i-segRL] = remote_char[i % 3]
                specR[i-segRL] += "+" if i < j else "-"

        for i in range(len(specL)):
            if specL[i] is None:
                specL[i] = isolated_char[(i + segLL) % 3]

        for i in range(len(specR)):
            if specR[i] is None:
                specR[i] = isolated_char[(i + segRL) % 3]

        return normalized_toptype(central_char, specL, segLL, specR, segRL)

        # print "\t".join((prot.name, str(hb.linenumber), str(hb.donor/3), str((hb.accptr-2)/3),
        #                  hb.cluster, hb.length_class(), normalized_toptype(specL, specR)))
    
def cleanup_window_pattern(s):
    if not remote_sign:
        s = re.sub("[-+]", "", s)
    if not always_include_remotes:
        s = re.sub("r[-+]?", "i", s)
    return s

def describe_pattern_window(prot, start, length, trim=0):
    """Describe the pattern of Hbonds within the window consisting of the
    LENGTH amino acids starting at START."""

    assert(length > 2*trim)

    hbond_char = (x for x in string.ascii_lowercase)
    spec = [None] * (3*length)
    for i in xrange(len(spec)):
        if spec[i] is not None:
            continue
        if i % 3 == 1:
            spec[i] = isolated_C_char
            continue
        bond = prot.get_bond(3*start + i)
        if bond is None:
            spec[i] = isolated_char[i % 3]
            continue
        j = bond.other_end(3*start + i)
        if (3*start <= j and j < 3*(start+length)):
            # A local bond
            char = hbond_char.next()
            spec[i] = char
            spec[j - 3*start] = char
        else:
            # A remote bond
            # spec[i] = 'r(%c:%d)' % ('+' if 3*start + i < j else "-", j)
            spec[i] = '%c%c' % (remote_char[i % 3], '+' if 3*start + i < j else '-')

    # spec = spec[3*trim:3*(length-trim)]

    return cleanup_window_pattern("".join(spec))


# sys.stdout = open("out/local_pattern.txt_%s_%d" % (hostname, pid), "w")

from argparse import ArgumentParser
parser = ArgumentParser()

parser.add_argument("files", nargs='*')

parser.add_argument("--output", help="output file")

parser.add_argument("--window-size", type=int,
                    help="the window size (in atoms) to use on either side of each H-bond", metavar="SIZE",
                    default=window_size)

parser.add_argument("--nearby-remotes", type=int,
                    help="the number of N/O atoms around the primary bond at which to retain remote bond information", metavar="COUNT",
                    default=nearby_remotes)

parser.add_argument("--nearby-twists", type=int,
                    help="the number of N/O atoms around the primary bond at which to retain twist information", metavar="COUNT",
                    default=nearby_twists)

parser.add_argument("--remote-sign", action="store_true",
                    help="whether to include forward/backward information (+/-) for remote bonds (r or R) (default %(default)s)")

parser.add_argument("--always-include-remotes", action="store_true",
                    help="whether to include remote bonds even if there is at least one other 'local' H-bond (default %(default)s)")

parser.add_argument("--tert-dir", type=str,
                    help="directory containing tertiary interaction information")

parser.add_argument("--Tbonds", action="store_true",
                    help="whether to describe tertiary interactions (T-bonds) rather than H-bonds (default %(default)s). Meaningless without --tert-dir.")

parser.add_argument("--show-residues", action="store_true",
                    help="whether to include a column with the four residues around N/O (default %(default)s)", default=True)

parser.add_argument("--residue-scheme", type=int,
                    help="which scheme to use for grouping residues", metavar="IDX",
                    default=residue_scheme)

parser.add_argument("--show-ssclass", action="store_true",
                    help="whether to include a column with the four secondary structure classifications around N/O (default %(default)s)")


parser.add_argument("--acid-length", type=int,
                    help="describe all patterns in a sliding window of this size, instead of around each Hbond", metavar="LENGTH",
                    default=0)

parser.add_argument("--trim-size", type=int, default=0,
                    help="trim this many amino acids from either end of the printed pattern when in sliding window mode")

parser.add_argument("--residue-dir", type=str,
                    help="directory containing residue information")

parser.add_argument("--ssclass-dir", type=str,
                    help="directory containing secondary structure information")

parser.add_argument("--whitelist", type=str, action='append',
                    help="file(s) with list of protein/line number pairs of Hbonds to ignore")

args = parser.parse_args()

window_size = args.window_size
nearby_remotes = args.nearby_remotes
nearby_twists = args.nearby_twists
remote_sign = args.remote_sign
always_include_remotes = args.always_include_remotes
tert_dir = args.tert_dir
Tbonds = args.Tbonds
show_residues = args.show_residues
show_ssclass = args.show_ssclass
residue_scheme = args.residue_scheme

acid_length = args.acid_length
residue_dir = args.residue_dir
ssclass_dir = args.ssclass_dir
trim_size = args.trim_size
whitelist_files = args.whitelist
if whitelist_files is None:
    whitelist_files = []
whitelist = read_whitelist_files(whitelist_files)

if args.output:
    sys.stdout = open(args.output, "w")

# For acid_length > 0, the --show-residues, --always-include-remotes and --remote-sign options also have meaning.

# if show_residues and acid_length > 0 and not residue_dir:
#     raise Exception("--show-residues requires --residue-dir when doing sliding window (acid-length > 0)")

# if not ssclass_dir:
#     ssclass_dir = "/home/qgm/QGM/cdp/data/20150626/HQ60"
# if not residue_dir:
#     residue_dir = "/home/qgm/QGM/cdp/data/20150428/HQ60"


for f in args.files:
    base, ext = os.path.splitext(os.path.basename(f))
    prot = Protein(name = base)
    prot.from_file(f)

    if base in whitelist:
        wl = whitelist[base]
    else:
        wl = set()

    if tert_dir:
        tfile = tert_dir + "/" + os.path.basename(f)
        try:
            prot.add_tertiary_interactions(tfile)
        except Exception as e:
            pass
            # sys.stderr.write("Failed to add tertiary interaction info for %s: %s\n" % (base, e))

    if residue_dir:
        resfile = residue_dir + "/" + os.path.basename(f)
        prot.add_residue_information(resfile)

    if ssclass_dir:
        ssfile = ssclass_dir + "/" + os.path.basename(f)
        prot.add_ssclass_information(ssfile)

    if acid_length > 0:
        # Hm. Should we compute the actual pattern for the entire
        # window, then strip the outermost 2*3*trim specifiers, or
        # should we just compute the pattern for the central segment
        # we're actually interested in? The former may give slightly
        # more details (presence of an 'a' or 'b' without a buddy
        # would indicate a 'short' bond), but at the same time it
        # would complicate interpreting these patterns. Moreover, when
        # we include 'remote signs', we would miss the direction of
        # those 'a' and 'b' bonds. So for now, we use the latter
        # option.

        for start in xrange(prot.minidx//3, max(prot.maxidx//3 - acid_length + 1, prot.minidx//3) + 1):
            # toptype = describe_pattern_window(prot, start, acid_length, trim_size)
            toptype = describe_pattern_window(prot, start+trim_size, acid_length-2*trim_size)
            print "\t".join((prot.name, str(start), toptype)),
            if show_residues:
                print "\t" + prot.get_residues(start, acid_length),
            if show_ssclass:
                print "\t" + prot.get_ssclasses(start, acid_length),
            print "\n",

    elif Tbonds:
        for tb in prot.Tbonds:
            toptype = describe_local_pattern(prot, tb)
            print "\t".join((prot.name, str(tb.linenumber), str((tb.donor-1)/3), str((tb.accptr-1)/3), toptype))
    else:
        for hb in prot.Hbonds:
            if hb.linenumber in wl:
                continue
            toptype = describe_local_pattern(prot, hb)
            print "\t".join((prot.name, str(hb.linenumber), str(hb.donor/3), str((hb.accptr-2)/3), hb.nature_cluster(), hb.length_class(), toptype)),
            if show_residues:
                print "\t" + str(residue_scheme) + simplify_residues(hb.residues),
            print "\n",
                
