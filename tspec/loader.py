import yaml
from typing import List, Any
import base64
import hashlib


class ParseError(Exception):
    pass


class Range:
    yaml_tag = u'!range'

    def __init__(self, dat):
        self.dat = dat

    def __str__(self):
        return "Range({})".format(str(self.dat))

    def __repr__(self):
        return str(self)

    def compile(self):
        if len(self.dat) < 2 or len(self.dat) > 3:
            raise ParseError("Range with wrong number of parameters")
        if len(self.dat) < 3:
            self.dat.append(1)
        self.dat[1] += self.dat[2]
        return list(range(self.dat[0], self.dat[1], self.dat[2]))

    @classmethod
    def from_yaml(cls, loader, node):
        value = loader.construct_sequence(node)
        return Range(value).compile()


class TNode:
    def __init__(self, name: str, pname: List[str], pvals: List[List[Any]], scr: str):
        # name shall be sorted alphabetically in case parser messes up
        self.name = name
        self.pname = pname
        self.pvals = pvals
        self.scr = scr
        self.dims = []
        for p in pvals:
            self.dims.append(len(p))
        self.children = list()

    def get_dims(self):
        return self.dims

    def get_odims(self):
        odims = list()
        for p in self.pvals:
            odims.append(p[:])
        return odims

    def add_child(self, child):
        self.children.append(child)

    def get_child(self, name: str):
        for c in self.children:
            if c.name == name:
                return c

    def compile(self, ppos: List[int]):
        vals = self.get_pval(ppos)
        return self.compile_val(vals)

    def get_pval(self, ppos: List[int]):
        vals = []
        for p, pp in enumerate(ppos):
            vals.append(self.pvals[p][pp])
        return vals

    def compile_val(self, pval: List[Any]):
        res = ""
        for p, pn in enumerate(self.pname):
            res += ("{}={}\n".format(pn, str(repr(pval[p]))))
        res += self.scr
        return res

    def hash(self):
        return base64.b64encode(hashlib.shake_256(('{}:{}\n{}'.format(self.name, str(self.pname), self.scr))
                                                  .encode('utf-8')).digest(6)).decode('utf-8')

    def __str__(self):
        return "Node({},{},{})".format(self.name, self.hash(), str(self.children))

    def __repr__(self):
        return str(self)


class TGraph:
    VER = 0.01

    def __init__(self, fname: str):
        f = open(fname, "r")
        self.y = yaml.safe_load(f)
        try:
            ver = self.y['TSPEC']
        except KeyError as ke:
            raise ParseError("TSPEC field doesn't exist") from ke
        if abs(ver - self.VER) > 0.001:
            raise ParseError("TSpec version mismatch given {} expect {}".format(ver, self.VER))
        del self.y['TSPEC']
        # create list of children from list of depends
        self.root = None
        for name, val in self.y.items():
            if not ('depends' in val):
                val['depends'] = list()
            if len(val['depends']) == 0:
                if self.root:
                    raise ParseError("Tree have multiple roots")
                else:
                    self.root = name
            val['children'] = list()
            if not ('scr' in val):
                val['scr'] = ""
        self.nodes = dict()
        for name, val in self.y.items():
            # create nodes and gather children
            pname = list()
            pvals = list()
            if 'param' in val.keys():
                for p in sorted(val['param'].keys()):
                    pname.append(p)
                    pvals.append(val['param'][p])
            self.nodes[name] = TNode(name, pname, pvals, val['scr'])
            for p in val['depends']:
                self.y[p]['children'].append(name)
        for name, val in self.y.items():
            for c in val['children']:
                self.nodes[name].add_child(self.nodes[c])
        self.root = self.nodes[self.root]


yaml.SafeLoader.add_constructor(Range.yaml_tag, Range.from_yaml)
