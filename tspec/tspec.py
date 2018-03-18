from tspec.reporter import GenericReporter
from tspec.loader import TGraph, TNode
from typing import List
from skopt import Optimizer
import math
import random


class ScriptExit(Exception):
    pass


class LeafOptimizer:
    FAIL = 0

    def __init__(self, nlist: List[TNode], reporter: GenericReporter):
        self.nlist = nlist[:]
        self.path = ""
        self.minimum = self.FAIL
        odims = list()
        self.space = 1
        for n in nlist:
            self.path += n.hash()
            odims += n.get_odims()
            for i in n.get_dims():
                self.space = self.space * i
        optparam = {'kappa': 1.96}
        self.opt = Optimizer(odims, base_estimator='RF', acq_optimizer='sampling',
                             acq_func='LCB', acq_func_kwargs=optparam)
        self.lv = self.FAIL
        self.l = 1
        self.exp = 0
        self.reporter = reporter

    def runseg(self, scr, state):
        state['global']['report'] = self.reporter
        try:
            exec(scr, state['global'], state['local'])
            del state['global']['report']
            return True
        except SystemExit:
            print("Script exit early")
            return False
        except Exception as e:
            print("Encountered error when running:")
            print(e)
            print("Script:\n{}".format(scr))
            return False

    def execscript(self):
        psel = self.opt.ask()
        print(self.path, psel)
        pstate = {'global': dict(), 'local': dict()}
        b = 0
        try:
            for n in self.nlist:
                pl = len(n.get_dims())
                scr = n.compile_val(psel[b:(b + pl)])
                b += pl
                if not self.runseg(scr, pstate):
                    raise ScriptExit()
            self.lv = self.reporter.evaluate()
            self.reporter.finalize(self.path, psel)
        except ScriptExit:
            self.lv = self.FAIL
        self.opt.tell(psel, self.lv)
        self.reporter.clear()
        if self.lv < self.minimum:
            self.minimum = self.lv
            return True
        return False


class Tspec:
    VER = 0.01

    def __init__(self, spec: str, reporter: GenericReporter):
        self.spec = spec
        self.reporter = reporter
        self.graph = TGraph(spec)

    def dfs(self, nodes: List[TNode], space: int):
        node = nodes[-1]
        nspace = space
        for i in node.get_dims():
            nspace = nspace * i
        # Leaf node
        if len(node.children) == 0:
            return [LeafOptimizer(nodes, self.reporter)]
        else:
            ret = list()
            # Internal node continue dfs
            for c in node.children:
                nodes.append(c)
                # use dfs to build a set of leaf optimizer
                ret += self.dfs(nodes, space)
                nodes.pop()
            return ret

    def run(self, wait=1000, rho=2 ** (-1 / 10), k=3):
        # Path explore
        opts = self.dfs([self.graph.root], 1)
        if len(opts) < 1:
            return
        # Optimize
        minimum = LeafOptimizer.FAIL - 1e-5
        lst_imprv = 0
        for i in opts:
            i.l = 1
        while True:
            lst_imprv += 1
            weight = list()
            lw = 0
            m = 1e200
            for l in opts:
                m = min(m, l.exp)
            for l in opts:
                lw = lw + (rho ** (l.exp - m)) * l.space * l.l * (k * l.minimum + minimum) / minimum
                weight.append(lw)
            lw = lw * random.random()
            leaf = None
            for item, cp in zip(opts, weight):
                if cp >= lw:
                    leaf = item
                    break
            if leaf is None:
                leaf = opts[-1]
            print(minimum, lst_imprv, end=" ")
            leaf.exp = leaf.exp + 1
            if leaf.execscript():
                leaf.l = leaf.l * (rho ** leaf.exp) + 1
                leaf.exp = 0
                lst_imprv = 0
                self.reporter.flush()
            minimum = min(leaf.lv, minimum)
            if lst_imprv >= wait:
                break
        self.reporter.flush()

# use exec with global/local dictionary mapping: {} will mask value
