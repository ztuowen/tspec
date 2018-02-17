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
        odims = list()
        for n in nlist:
            self.path += n.hash()
            odims += n.get_odims()
        optparam = {'kappa': 0}
        self.opt = Optimizer(odims, base_estimator='RF', acq_optimizer='sampling',
                             acq_func='LCB', acq_func_kwargs=optparam)
        self.lv = self.FAIL
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
        return self.lv


class Tspec:
    VER = 0.01

    def __init__(self, spec: str, reporter: GenericReporter):
        self.spec = spec
        self.reporter = reporter
        self.graph = TGraph(spec)

    def dfs(self, nodes: List[TNode]):
        node = nodes[-1]
        # Leaf node
        if len(node.children) == 0:
            return [LeafOptimizer(nodes, self.reporter)]
        else:
            ret = list()
            # Internal node continue dfs
            for c in node.children:
                nodes.append(c)
                # use dfs to build a set of leaf optimizer
                ret += self.dfs(nodes)
                nodes.pop()
            return ret

    def run(self, wait=1000):
        # Path explore
        opts = self.dfs([self.graph.root])
        if len(opts) < 1:
            return
        # Optimize
        minimum = LeafOptimizer.FAIL
        lst_imprv = 0
        while True:
            lst_imprv += 1
            leaf = random.choice(opts)
            print(minimum, end=" ")
            val = leaf.execscript()
            if val < minimum:
                minimum = val
                lst_imprv = 0
            if lst_imprv >= wait:
                break
        self.reporter.flush()

# use exec with global/local dictionary mapping: {} will mask value
