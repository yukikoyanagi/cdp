#!/usr/bin/python
#
# File: cdp.py
# Time-stamp: <2015-11-03 11:16:10 villemoes>
# Author: Rasmus Villemoes

#CDP_Vertex = namedtuple('cdp_vertex', ["type", "data"])

import sys
import re

# C really means Calpha, and O means the other C in the peptide unit.
mod3_to_atom = ("N", "C", "O")
atom_to_mod3 = {"N": 0, "C": 1, "O": 2}

# A simple parser of a string of the form "a = b, c, d = e, f in {foo,
# bar}, g = xyz" into key-value pairs. Each key must be alphanumeric ([a-zA-Z_0-9]+). 
#
# If it is followed by a comma, it is taken as a boolean flag, so we
# create the key with value True; however, the _first_ key appearing
# without a value is treated as if it was the value associated to a
# key called "label".
#
# If the key is followed by a =, the value is the string following the = up
# to the next , or end of input string.
#
# If the key is followed by the word "in", a set of strings must
# follow; the value is that set of strings.
def parse_keyval(s):
    d = dict()
    s = s.strip()
    while s:
        # Remove leading whitespace and commas from s; if this makes s empty, we are done.
        s = re.sub("^[\s,]+", "", s)
        if s == "":
            break
        
        m = re.match("([a-zA-Z0-9_]+)\s+in\s+\{([^{}]*)\}", s)
        if m:
            k = m.group(1)
            v = set([x.strip() for x in m.group(2).split(",")])
            d[k] = v
            s = s[m.end():]
            continue
        
        m = re.match("([a-zA-Z0-9_]+)\s*=\s*([^,]*)", s)
        if m:
            k = m.group(1)
            v = m.group(2).strip()
            d[k] = v
            s = s[m.end():]
            continue
        
        m = re.match("([a-zA-Z0-9_]+)", s)
        if m:
            k = m.group(1)
            if "label" not in d:
                d["label"] = k
            else:
                d[k] = True
            s = s[m.end():]
            continue
        
        raise Exception("unable to make sense of '%s'", s)
    
    return d

    

class CDP_Hbond:
    def __init__(self, label = None, donor = None, accptr = None):
        self.label = label
        self.donor = donor
        self.accptr = accptr
        self.SO3class = None
        self.dist = None # signed distance from accptr to donor

    def set_donor(self, donor):
        assert(donor.atom() == "N")
        if self.donor is not None:
            raise Exception("donor for H-bond %s already set" % self.label)
        self.donor = donor

    def set_acceptor(self, accptr):
        assert(accptr.atom() == "O")
        if self.accptr is not None:
            raise Exception("acceptor for H-bond %s already set" % self.label)
        self.accptr = accptr

    def set_endpoint(self, vertex):
        if vertex.atom() == "N":
            self.set_donor(vertex)
        elif vertex.atom() == "O":
            self.set_acceptor(vertex)
        else:
            raise Exception("endpoint of a H-bond must be either an N or O backbone atom")

    def set_SO3class(self, c):
        if type(c) is str:
            self.SO3class = set([c])
        elif type(c) is set:
            self.SO3class = c
        else:
            raise Exception("invalid argument to set_SO3class; expected set or string")

    def set_dist(self, d):
        # d can be a set of strings, a set of integers, a string or an
        # integer. Each string should either be parsable as an
        # integer, or of the form "4...9" with exactly three dots,
        # representing the set {4,5,6,7,8,9}. Negative numbers are ok;
        # e.g. "-8...-2" or "-4...1" can also be unambigously parsed.
        def scalar_to_intset(s):
            if type(s) is int:
                return set([s])
            if type(s) is str:
                m = re.match("^(-?[0-9]+)\.\.\.(-?[0-9]+)$", s)
                if m:
                    return set(range(int(m.group(1)), int(m.group(2))+1))
                m = re.match("^(-?[0-9]+)$", s)
                if m:
                    return set([int(s)])
                m = re.match("^(-?[0-9]+)\.\.([0-9]+)\.\.(-?[0-9]+)$", s)
                if m:
                    return set(range(int(m.group(1)), int(m.group(3))+1, int(m.group(2))))
        self.dist = set()
        if type(d) is int or type(d) is str:
            self.dist = scalar_to_intset(d)
        else:
            for x in d:
                self.dist |= scalar_to_intset(x)

    def is_specified(self):
        return self.donor is not None and self.accptr is not None

    def set_properties(self, d):
        if "SO3class" in d:
            self.set_SO3class(d["SO3class"])
        if "dist" in d:
            self.set_dist(d["dist"])
        pass
    # for each of a set of keywords (corresponding min/max energy,
    # cluster classification, ...), check whether that keywords is in
    # the dictionary dict, and if so, set the corresponding property.

    def as_string(self, full = True):
        s = self.label
        if full:
            if self.SO3class is not None:
                s += ", SO3class in {%s}" % ", ".join([x for x in self.SO3class])
            if self.dist is not None:
                if len(self.dist) == 1:
                    s += ", dist = %d" % list(self.dist)[0]
                else:
                    s += ", dist in {%s}" % ", ".join([str(x) for x in sorted(list(self.dist))])
            pass
        return "Hb(%s)" % s

    def other_end(self, v):
        if v == self.donor:
            return self.accptr
        if v == self.accptr:
            return self.donor
        raise Exception("cannot determine other_end without knowing one end...")




    

class CDP_Vertex(object):
#    __slots__ = ["segment", "vidx", "atom", "type", "data"]

    _cache = {}

    @staticmethod
    def _new(cls):
        obj = super(CDP_Vertex, cls).__new__(cls)
        obj.segment = None
        obj.vidx = None
        obj.type = None
        obj.data = None
        return obj

    @staticmethod
    def _is_reusable(spec):
        return spec in ["*", "i"]

    @staticmethod
    def _create_singleton(cls, segment, vidx, spec):
        obj = CDP_Vertex._new(cls)
        obj.type = spec
        CDP_Vertex._cache[spec] = obj

    @staticmethod
    def _get_from_cache(cls, segment, vidx, spec):
        if spec not in CDP_Vertex._cache:
            CDP_Vertex._create_singleton(cls, segment, vidx, spec)
        return CDP_Vertex._cache[spec]

        

    def __new__(cls, segment, vidx, spec):
        if CDP_Vertex._is_reusable(spec):
            return CDP_Vertex._get_from_cache(cls, segment, vidx, spec)
        return CDP_Vertex._new(cls)

    def __init__(self, segment, vidx, spec):
        if self.type is not None:
            return
        self.segment = segment
        self.vidx = vidx
        # mod3 = (vidx + segment.mod3) % 3
        # self.atom = mod3_to_atom[mod3]
        self.type = None
        self.data = None

        # This is the hard part: Parse the vertex specification.
        spec = spec.strip()

        if spec == "*":
            self.type = "*"
        elif spec == "i":
            self.type = "i"
        elif re.match("Hb\s*\(([^()]+)\)", spec):
            # Grrr: Stupid Python for not allowing
            # assignment-in-conditional. Noone seems to have a really
            # good solution for this. So we just do the match again...
            m = re.match("Hb\s*\(([^()]+)\)", spec)
            self.type = "c" # c = chord
            kv = parse_keyval(m.group(1))
            if "label" not in kv:
                raise Exception("no label for H-bond")
            label = kv["label"]
            # look up this label in the self.segment.cdp.hbonds dictionary.
            if label in self.segment.cdp.hbonds:
                hb = self.segment.cdp.hbonds[label]
            else:
                hb = CDP_Hbond(label = label)
                self.segment.cdp.hbonds[label] = hb
            hb.set_endpoint(self)
            del kv["label"]
            hb.set_properties(kv)
            self.data = hb
        else:
            raise Exception("unable to parse vertex specification '%s'" % spec)

    def mod3(self):
        return (self.vidx + self.segment.mod3) % 3

    def atom(self):
        return mod3_to_atom[self.mod3()]

    def as_string(self):
        if self.type == "*":
            return "*"
        if self.type == "i":
            return "i"
        if self.type == "c":
            hb = self.data
            # Return Hb(label) for the acceptor, Hb(label, ...other properties...) for the donor
            return hb.as_string(self == hb.donor)
        return "???"

class CDP_Segment:
    def __init__(self, cdp, sidx, spec):
        self.cdp = cdp
        self.sidx = sidx

        spec = spec.strip()
        m = re.match("(N|C|O):\s*(.*)", spec)
        if not m:
            raise Exception("invalid segment specification '%s'; must begin with (N|C|O):", spec)
        self.vertices = []
        self.first_atom = m.group(1)
        self.mod3 = atom_to_mod3[self.first_atom]
        
        # if self.first_atom == "N":     self.mod3 = 0
        # elif self.first_atom == "Ca":  self.mod3 = 1
        # elif self.first_atom == "O":   self.mod3 = 2
        # else:   raise Exception("this can't happen: self.first_atom is not one of 'N', 'C', 'O'")
        vspecs = filter(None, [x.strip() for x in m.group(2).strip().split(";")])

        for i,vspec in enumerate(vspecs):
            self.vertices.append(CDP_Vertex(self, i, vspec))
            
    def __len__(self):
        return len(self.vertices)

    def as_string(self):
        s = self.first_atom + ": "
        s += "; ".join(v.as_string() for v in self.vertices)
        return s


class CDP:

    strict_default = True

    def __init__(self, name, spec, strict = None):
        """spec is a string, containing a newline-separated
        specification of the segments constituting this chord diagram
        pattern. (Instead of newlines, double semicolons may be used.)

        Each segment description must start with 'N:', 'C:' or 'O:' to
        indicate whether the first vertex is to correspond to a N,
        Calpha or C (no, not a typo: the latter being distinguished by
        being double-bonded to an O) in the backbone. After that comes
        a semicolon separated sequence of predicates, one for each
        vertex in the segment. The predicates can be the following:

        *:     Wildcard; no requirements are placed on that vertex
        i:     Isolated; no H-bond is allowed to be incident on this vertex
        Hb(x): There is a H-bond from this vertex to the other vertex
               with the same predicate; x is some identifying string
               used to distinguish the various H-bonds.
        
        More predicates may be added later.

        Example: Two consecutive bonds in a typical alpha-helix would
        be matched by

        "O: Hb(1); *; *; Hb(2);; N: Hb(1); *; *; Hb(2)"

        """

        if strict is None:
            strict = CDP.strict_default

        self.name = name
        self.strict = strict
        segspec = filter(None, [x.strip() for x in spec.strip().replace(";;", "\n").splitlines()])
        # each segment is abstracted by a cdp_segment.
        self.hbonds = dict()
        self.segments = []
        for i, ss in enumerate(segspec):
            self.segments.append(CDP_Segment(self, i, ss))

        for label,hb in self.hbonds.iteritems():
            if not hb.is_specified():
                raise Exception("H-bond with label %s incompletely specified" % label)


    def __len__(self):
        return len(self.segments)

    def as_string(self, oneline = False):
        """Get a representation of the chord diagram pattern in a
        format which is both human-readable and usable in the
        constructor."""
        sep = "\n"
        if oneline:
            sep = ";; "
        return sep.join(seg.as_string() for seg in self.segments)

    def find_matches(self, prot, strict = None, color_bonds = False):
        if strict is None:
            strict = self.strict
        if len(self.segments) == 0:
            return
        seg0 = self.segments[0]
        # The first segment must be mapped to a position matching its
        # first atom. We start from [(the largest multiple of 3 <=
        # prot.minidx) + (seg0.mod3)], then proceed in steps of 3.
        for f in range((prot.minidx//3)*3 + seg0.mod3, prot.maxidx, 3):
            offsets = [None] * len(self.segments)
            offsets[0] = f
            segs_to_process = [0]
            if self.check_match(prot, offsets, segs_to_process, strict):
                # We must also check that the segments we've mapped to do not overlap
                r = [(x, x+len(self.segments[j])) for j,x in enumerate(offsets)]
                if not strict:
                    r.sort()
                if all([r[j][1] <= r[j+1][0] for j in xrange(len(r)-1)]):
                    print "\t".join([prot.name, self.name, str(f), str(f//3)])
                    if color_bonds:
                        for label,hb in self.hbonds.iteritems():
                            # hb.donor is a CDP_Vertex, from which we
                            # can get its vidx and its containing
                            # segments sidx; these combine to tell us
                            # the atom number where this Hbond has
                            # been matched to.
                            vidx = hb.donor.vidx
                            sidx = hb.donor.segment.sidx
                            idx = offsets[sidx] + vidx
                            # We know that prot.get_Hbond must return an Hbond
                            prot.get_Hbond(idx).add_color(self.name + ":" + hb.label)

    # This is the actual matcher function. offsets contains a list of
    # segments which have already been mapped to offsets within the
    # protein prot (offsets[i] is None if segment i has not been
    # assigned to an offset yet); and segs_to_process is a stack of
    # segment indices which have been positioned within prot, but for
    # which matching has not been checked.
    #
    # As long as segs_to_process is non-empty, we pop an index from
    # the stack, then check whether that segment matches. This is done
    # in two passes: In the first pass, we check all the conditions
    # which can be checked using the segments which have been matched
    # to an offset within prot
    def check_match(self, prot, offsets, segs_to_process, strict):
        while segs_to_process:
            i = segs_to_process.pop()
            seg = self.segments[i]
            # A segment pushed on to segs_to_process must have been mapped to a position
            assert(offsets[i] is not None)
            os = offsets[i] # the offset where the i'th segment is mapped
            for j,v in enumerate(seg.vertices):
                if v is None:
                    return False
                # The wildcard type by definition matches
                if v.type == "*":
                    continue
                c = prot.get_Hbond(os+j)
                # The isolated type matches if and only if no Hbond is incident on vertex os+j.
                if v.type == 'i':
                    if c is not None:
                        return False
                    continue
                # "i" and "*" exhaust the possibilities for a vertex to be allowed not to have a chord incident. 
                if c is None:
                    return False
                other_end = c.other_end(os+j)
                if v.type == "+":
                    # The current vertex has absolute index os+j. It
                    # must have a chord incident, and that chord must
                    # end somewhere with larger index.
                    if other_end <= os+j:
                        return False
                    continue
                if v.type == "-":
                    # Completely similar to the above
                    if other_end >= os+j:
                        return False
                    continue
                if v.type != "c":
                    print "WTF: {%s}" % p['type']
                assert(v.type == "c")
                hb = v.data
                w = hb.other_end(v) # the other CDP_Vertex which this Hbond is incident to
                (k, m) = (w.segment.sidx, w.vidx)
                # The vertex at index os+j must be connected to the
                # vertex which the m'th vertex of the k'th segment is
                # mapped to. If the k'th segment has already been
                # mapped, we can decide that now; otherwise, this
                # chord determines where the k'th segment must be
                # mapped.
                if offsets[k] is None:
                    # The k'th segment must be mapped to position other_end-m. If in strict mode, check that this is ok.
                    if strict:
                        if k-1 >= 0 and offsets[k-1] is not None and other_end-m <= offsets[k-1]:
                            return False
                        if k+1 < len(self) and offsets[k+1] is not None and other_end-m >= offsets[k+1]:
                            return False
                    offsets[k] = other_end-m
                    segs_to_process.append(k)
                else:
                    cc = prot.get_Hbond(offsets[k]+m)
                    if cc is None or cc is not c:
                        return False

        # if we reach this point, all segments have been succesfully matched.
        return True

# TODO: Make Hbond and Tbond derive from the same base class, with common properties linenumber, donor, accptr (for Tbonds, we just pretend the "donor" is the lowest-numbered Calpha) and method other_end.

class Hbond:
    def __init__(self, linenumber, donoridx, accptridx, length = 0, cluster = None, ident = None, flags = None, residues = None, so3matrix = None):
        if residues is None:
            residues = "XXXX"
        self.linenumber = linenumber
        self.donor = donoridx
        self.accptr = accptridx
        self.cluster = cluster
        self.length = length
        self.ident = ident
        self.colors = list()
        self.flags = flags
        self.residues = residues
        self.so3matrix = so3matrix

    def add_color(self, s):
        self.colors.append(s)

    def get_donoridx(self):
        return self.donor

    def get_accptridx(self):
        return self.accptr

    def other_end(self, idx):
        if idx == self.donor:
            return self.accptr
        if idx == self.accptr:
            return self.donor
        raise Exception("cannot determine other_end without knowing one end...")

    # This only made sense when we were only looking at the HQ60
    # proteins used for the Nature paper. But in general, we don't
    # and can't know the cluster classification.
    def nature_cluster(self):
        if self.cluster is None:
            return "?"
        return self.cluster

    def length_class(self):
        if abs(self.length) >= 7:
            return "L"
        return str(self.length)

        # if self.cluster is None or self.cluster == "?":
        #     delta = self.donor - self.accptr
        #     if (delta > 0):
        #         delta += 2
        #         delta /= 3
        #         if delta > 6:
        #             return "L"
        #         return str(delta)
        #     delta += 2
        #     delta /= 3
        #     if delta < -6:
        #         return "L"
        #     return str(delta)

        #     return "?"
        # x = int(self.cluster)
        # if x == -1:
        #     return "0"
        # if x > 100:
        #     return "L"
        # if x > 0:
        #     return str(x // 10)
        # else:
        #     return str(-(abs(x)//10))

    def is_twisted(self):
        if self.so3matrix is None:
            return False
        return self.so3matrix[2][2] < 0.0;

class Tbond:
    def __init__(self, linenumber, left, right, d_VDW = None):
        if left > right:
            left, right = right, left
        
        self.linenumber = linenumber
        self.left = left
        self.right = right
        self.donor = left
        self.accptr = right
        self.d_VDW = d_VDW

    def other_end(self, idx):
        if idx == self.left:
            return self.right
        if idx == self.right:
            return self.left
        raise Exception("cannot determine other_end without knowing one end...")

    def is_twisted(self):
        return False;


class Protein:
    simplify_ssclass = {'G':'H', 'H':'H', 'I':'H', 'E':'S', 'B':'-', 'T':'-', 'S':'-', '-':'-', '?':'-', '*':'-'}

    def __init__(self, name="(noname)"):
        self.name = name
        self.vertices = dict()
        self.residues = dict() # indexed by amino acid number - the associated vertices have atom numbers 3n (N), 3n+1 (Calpha), 3n+2 (O)
        self.ssclass = dict() # similarly
        self.Hbonds = []
        self.Tbonds = []
        self.minidx = 2 ** 20
        self.maxidx = -1

    def add_residue(self, idx, r):
        if r == "?":
            r = "X"
        if not ord("@") <= ord(r) <= ord("Z"):
            r = "@"
        if not idx in self.residues:
            self.residues[idx] = r
            return
        if self.residues[idx] == r:
            return
        if self.residues[idx] in '@X' and r != "@":
            # Overwrite with, presumably, better information
            self.residues[idx] = r
            return
        
        sys.stderr.write("%s: residue %s for index %d conflicts with previous information (%s)\n" % (self.name, r, idx, self.residues[idx]))

    def add_ssclass_annotation(self, idx, s):
        # Some are "?" or "*"; treat these as "None", aka "-". This
        # way we have precisely 8 classes to deal with.
        if s == "?" or s == "*":
            s = "-"
        self.ssclass[idx] = s

    def get_residue(self, atomidx):
        if atomidx in self.residues:
            return self.residues[atomidx]
        return 'X'

    def get_residues(self, start, length):
        return "".join(self.get_residue(n) for n in range(start, start+length))

    def get_ssclass(self, aaidx):
        if aaidx in self.ssclass:
            return self.ssclass[aaidx]
        return "-"

    def get_ssclasses(self, start, length):
        return "".join(self.get_ssclass(n) for n in range(start, start+length))


    def add_residue_information(self, f):
        for line in open(f):
            p,start,res = line.strip().split()
            if not self.name.startswith(p):
                continue
            start = int(start)
            for i, r in enumerate(res):
                self.add_residue(i+start, r)

    # ssclass = secondary structure classification
    def add_ssclass_information(self, f):
        for line in open(f):
            p,start,ssclass = line.strip().split()
            if not self.name.startswith(p):
                continue
            start = int(start)
            for i, s in enumerate(ssclass):
                self.add_ssclass_annotation(i+start, s)


    def add_Hbond(self, linenumber, i, j, length = None, cluster = None, flags = None, residues = None, so3matrix = None):
        if i in self.vertices:
            hb = self.vertices[i]
            raise Exception("vertex %3d already has chord (%3d,%3d;%s) incident" % (i, hb.donor, hb.accptr, hb.flags))
        if j in self.vertices:
            hb = self.vertices[j]
            raise Exception("vertex %3d already has chord (%3d,%3d;%s) chord incident" % (j, hb.donor, hb.accptr, hb.flags))
        if i == j:
            raise Exception("cannot add chord from %d to itself" % i)
        if residues is not None:
            self.add_residue((i-2)//3, residues[0])
            self.add_residue((i+1)//3, residues[1])
            self.add_residue((j-1)//3, residues[2])
            self.add_residue((j+2)//3, residues[3])
        hb = Hbond(linenumber, i, j, length = length, cluster = cluster, flags = flags, residues = residues, so3matrix = so3matrix)
        self.Hbonds.append(hb)
        self.vertices[i] = hb
        self.vertices[j] = hb
        self.minidx = min(i,j,self.minidx)
        self.maxidx = max(i,j,self.maxidx)
        return self

    def add_tert(self, linenumber, i, j, VDW = None):
        if i in self.vertices:
            tb = self.vertices[i]
            raise Exception("vertex %3d already has a tertiary interaction (%3d,%3d,%f)" % (i, tb.left, tb.right, tb.d_VDW))
        if j in self.vertices:
            tb = self.vertices[j]
            raise Exception("vertex %3d already has a tertiary interaction (%3d,%3d,%f)" % (j, tb.left, tb.right, tb.d_VDW))
        if i == j:
            raise Exception("cannot add Tbond from %d to itself" % i)
        assert(i % 3 == 1)
        assert(j % 3 == 1)
        tb = Tbond(linenumber, i, j, VDW)
        self.Tbonds.append(tb)
        self.vertices[i] = tb
        self.vertices[j] = tb
        self.minidx = min(i,j,self.minidx)
        self.maxidx = max(i,j,self.maxidx)
        return self

    def from_file(self, fn):
        if self.name is None:
            self.name = fn

        # We use columns 12-13 (aka 13-14 with 1-based indexing); that
        # is what has been used for cluster classification etc.
        # src_col = 10
        # dst_col = 11
        src_col = 12
        dst_col = 13
        len_col = 14
        src_fn = lambda x: 3*x
        dst_fn = lambda x: 3*x+2
        energy_col = 20
        flags_col = 21
        cluster_col = 45
        # Columns 5-8 (1-based) contain the four residues around the N/O atoms.
        res_col_start = 4
        res_col_end = 8
        # Columns 51-59 (1-based) contain the entries of the SO3 matrix, in row-major order.
        so3_col_start = 50
        so3_col_end = 59

        class Record:
            def __init__(self, linenumber, i, j, length, cluster, energy, flags, residues, matrix):
                self.linenumber = linenumber
                self.i = i
                self.j = j
                self.length = length
                self.cluster = cluster
                self.energy = float(energy)
                self.flags = flags
                self.residues = residues
                self.so3matrix = matrix

        f = open(fn)
        records = []
        linenumber = 0
        for line in f:
            linenumber += 1
            fields = line.strip().split()
            i = src_fn(int(fields[src_col]))
            j = dst_fn(int(fields[dst_col]))
            length = int(fields[len_col])
            flags = fields[flags_col]
            residues = "".join(fields[res_col_start:res_col_end])
            # Sometimes ? is used for unknown, sometimes X. The latter is nicer in file names.
            residues = residues.replace("?", "X")

            # We are only interested in intra-chain bonds (indicated
            # by __), and further the last two characters must be
            # either U (unique) or S (strong)
            if not re.search("__[US][US]$", flags):
                # print "%s does not match!" % flag
                continue

            matrix=tuple([tuple([float(fields[so3_col_start + 3*x + y]) for y in range(3)]) for x in range(3)])

            records.append(Record(linenumber, i, j, length, fields[cluster_col], fields[energy_col], flags, residues, matrix))
        f.close()

        records.sort(key=lambda x: x.energy)
        for r in records:
            # print r.i, r.j, r.cluster, r.energy
            try:
                self.add_Hbond(r.linenumber, r.i, r.j, length = r.length, cluster = r.cluster, flags = r.flags, residues = r.residues, so3matrix = r.so3matrix)
            except Exception as e:
                pass
                # sys.stderr.write("%s: %s: chord [%3d,%3d;%s] not added\n" % (fn, e, r.i, r.j, r.flags))

        self.Hbonds.sort(key=lambda x: x.linenumber)

    def add_tertiary_interactions(self, fn, Calpha_max_dist = float("inf"), Cbeta_max_dist = float("inf")):
        # For tertiary interactions, there's no well-defined "donor"
        # and "acceptor". Instead, we simply use the left-most and
        # right-most along the backbone. The data seems to contain
        # each interaction twice (with certain columns swapped and/or
        # negated); we just keep the one with left < right.
        left_col = 6  # 7 with 1-based indexing
        right_col = 7 # 8 with 1-based indexing
        # The Calphas sit at atom positions 3n+1
        atom_fn = lambda x: 3*x + 1
        flags_col = 15 # KOL16: ... chain-pair: "__" denotes intra-chain), ...
        Calpha_dist_col = 19 # KOL20: CA(i)-CA(j) distance
        Cbeta_dist_col = 20 # KOL21: CB(i)-CB(j) distance
        VDW_col = 21   # KOL22: minimum distance, d_VDW between all pairs of heavy atoms in residues

        class Record:
            def __init__(self, linenumber, left, right, VDW):
                self.linenumber = linenumber
                self.left = left
                self.right = right
                self.VDW = VDW

        f = open(fn)
        records = []
        linenumber = 0
        for line in f:
            linenumber += 1
            fields = line.strip().split()
            left = atom_fn(int(fields[left_col]))
            right = atom_fn(int(fields[right_col]))
            if right < left:
                continue
            flags = fields[flags_col]
            # We are only interested in intra-chain bonds (indicated
            # by __)
            if not re.search("^..__..$", flags):
                # print "%s does not match!" % flag
                continue
            Calpha_dist = float(fields[Calpha_dist_col])
            Cbeta_dist = float(fields[Cbeta_dist_col])
            VDW = float(fields[VDW_col])
            if Calpha_dist <= Calpha_max_dist and Cbeta_dist <= Cbeta_max_dist:
                records.append(Record(linenumber, left, right, VDW))
        f.close()

        records.sort(key=lambda x: x.VDW)
        for r in records:
            # print r.i, r.j, r.cluster, r.energy
            try:
                self.add_tert(r.linenumber, r.left, r.right, r.VDW)
            except Exception as e:
                # ignore the many cases of extra tertiary
                # interactions, we can't handle that currently.
                pass 
                #                sys.stderr.write("%s: %s: tertiary interaction [%3d,%3d;%f] not added\n" % (fn, e, r.left, r.right, r.VDW))

        self.Tbonds.sort(key=lambda x: x.linenumber)



    def get_Hbond(self, idx):
        """Return the Hbond attached at index idx, or None if no Hbond is at that index."""
        assert(idx % 3 != 1)
        if idx in self.vertices:
            return self.vertices[idx]
        else:
            return None
    
    def get_Tbond(self, idx):
        """Return the tertiary interaction at index idx, or None if there is no Tbond there."""
        assert(idx % 3 == 1)
        if idx in self.vertices:
            return self.vertices[idx]
        else:
            return None


    def get_bond(self, idx):
        if idx % 3 == 1:
            return self.get_Tbond(idx)
        else:
            return self.get_Hbond(idx)



# class chord_diagram:
#     def __init__(self, name="(noname)"):
#         self.name = name
#         self.vertices = dict()
#         self.minidx = 2 ** 20
#         self.maxidx = -1

#     def add_chord(self, i, j):
#         if i in self.vertices:
#             raise Exception("vertex %d already has a chord incident" % i)
#         if j in self.vertices:
#             raise Exception("vertex %d already has a chord incident" % j)
#         if i == j:
#             raise Exception("cannot add chord from %d to itself" % i)
#         self.vertices[i] = j
#         self.vertices[j] = i
#         self.minidx = min(i,j,self.minidx)
#         self.maxidx = max(i,j,self.maxidx)
#         return self

#     def from_file(self, fn, src_col = 10, dst_col = 11, src_fn = lambda x: 3*x, dst_fn = lambda x: 3*x+2):
#         if self.name is None:
#             self.name = fn
#         f = open(fn)
#         for line in f:
#             fields = line.strip().split()
#             i = src_fn(int(fields[src_col]))
#             j = dst_fn(int(fields[dst_col]))
#             flag = fields[21]
#             # The last two characters must be either U (unique) or S (strong)
#             if not re.search("[US][US]$", flag):
#                 # print "%s does not match!" % flag
#                 continue
#             try:
#                 self.add_chord(i, j)
#             except:
#                 sys.stderr.write("%s: chord (%d,%d) not added\n" % (fn, i, j))
#         f.close()

#     def get_vertex(self, idx):
#         if idx in self.vertices:
#             return self.vertices[idx]
#         else:
#             return None

#     def dump(self):
#         print self.name
#         for i in self.vertices:
#             print "%d --> %d" % (i, self.vertices[i])

#     def compactify(self):
#         v = self.vertices.keys()
        
#         new = chord_diagram()
        
