from typing import List, Any
import base64
import hashlib
import yaml
from skopt.space import Categorical


class ParseError(Exception):
    pass


class Range:
    yaml_tag = u'!range'

    def __init__(self, dat):
        self.dat = dat
        self.plist = []

    def __str__(self):
        return "Range({})".format(str(self.dat))

    def __repr__(self):
        return str(self)

    def compile(self):
        if len(self.dat) != 2:
            raise ParseError("Range with wrong number of parameters")
        if isinstance(self.dat[0], float) or isinstance(self.dat[1], float):
            return self.dat[:]
        return list(range(self.dat[0], self.dat[1] + 1))

    def __len__(self):
        return len(self.plist)

    @classmethod
    def from_yaml(cls, loader, node):
        value = loader.construct_sequence(node)
        rng = Range(value)
        rng.plist = rng.compile()
        return rng


class TNode:
    def __init__(self, name: str, pname: List[str], pvals: List[List[Any]],
                 scr: str):
        # name shall be sorted alphabetically in case parser messes up
        self.name = name
        self.pname = pname
        self.pvals = pvals
        self.scr = scr
        self.dims = []
        for pval in pvals:
            self.dims.append(len(pval))
        self.children = list()

    def get_dims(self):
        return self.dims

    def get_odims(self):
        odims = list()
        for p in self.pvals:
            if isinstance(p, Range):
                odims.append(p.dat)
            else:
                odims.append(Categorical(p[:]))
        return odims

    def add_child(self, child):
        self.children.append(child)

    def get_child(self, name: str):
        for c in self.children:
            if c.name == name:
                return c
        raise NameError("No child named {}".format(name))

    def compile(self, ppos: List[int]):
        vals = self.get_pval(ppos)
        return self.compile_val(vals)

    def get_pval_at(self, p, pp):
        if isinstance(self.pvals[p], Range):
            return self.pvals[p].plist[pp]
        else:
            return self.pvals[p][pp]

    def get_pval(self, ppos: List[int]):
        vals = []
        for p, pp in enumerate(ppos):
            vals.append(self.get_pval_at(p, pp))
        return vals

    def compile_val(self, pval: List[Any]):
        res = ""
        for p, pn in enumerate(self.pname):
            res += ("{}={}\n".format(pn, str(repr(pval[p]))))
        res += self.scr
        return res

    def hash(self):
        return base64.b64encode(hashlib.shake_256(
            '{}:{}\n{}'.format(self.name, str(self.pname), self.scr)
            .encode('utf-8')).digest(6)).decode('utf-8')

    def __str__(self):
        return "Node({},{},{})".format(self.name, self.hash(),
                                       str(self.children))

    def __repr__(self):
        return str(self)


class TGraph:
    VER = 0.01

    def __init__(self, fname: str):
        f = open(fname, "r")
        self.y = yaml.safe_load(f)
        try:
            ver = self.y['TSPEC']
        except KeyError as key_error:
            raise ParseError("TSPEC field doesn't exist") from key_error
        if abs(ver - self.VER) > 0.001:
            raise ParseError(
                "TSpec version mismatch given {} expect {}".format(ver,
                                                                   self.VER))
        del self.y['TSPEC']
        # create list of children from list of depends
        self.root = None
        for name, val in self.y.items():
            if not val:
                val = dict()
                self.y[name] = val
            if 'depends' not in val:
                val['depends'] = list()
            if not val['depends']:
                if self.root:
                    raise ParseError("Tree have multiple roots")
                else:
                    self.root = name
            val['children'] = list()
            if 'scr' not in val:
                val['scr'] = ""
        self.nodes = dict()
        for name, val in self.y.items():
            # create nodes and gather children
            pname = list()
            pvals = list()
            if 'param' in val.keys():
                for param in sorted(val['param'].keys()):
                    pname.append(param)
                    pvals.append(val['param'][param])
            self.nodes[name] = TNode(name, pname, pvals, val['scr'])
            for dep in val['depends']:
                self.y[dep]['children'].append(name)
        for name, val in self.y.items():
            for child in val['children']:
                self.nodes[name].add_child(self.nodes[child])
        self.root = self.nodes[self.root]


yaml.SafeLoader.add_constructor(Range.yaml_tag, Range.from_yaml)
