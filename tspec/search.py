from tspec.reporter import GenericReporter
from tspec.loader import TGraph, TNode
from typing import List
from skopt import Optimizer
from dill import dill
import numpy as np
import signal
import pickle
import random


class ScriptExit(Exception):
    pass


def runseg(reporter, scr, state):
    state['global']['report'] = reporter
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


class LeafOptimizer:
    FAIL = 0

    def __init__(self, nlist: List[TNode], rfsearch):
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
        self.rfsearch = rfsearch
        self.reporter = rfsearch.reporter

    def execscript(self):
        psel = self.opt.ask()
        for i in range(len(psel)):
            if isinstance(psel[i], np.generic):
                psel[i] = np.asscalar(psel[i])
        print(self.path, psel)
        pstate = {'global': dict(), 'local': dict()}
        b = 0
        try:
            for n in self.nlist:
                pl = len(n.get_dims())
                scr = n.compile_val(psel[b:(b + pl)])
                b += pl
                if not runseg(self.reporter, scr, pstate):
                    raise ScriptExit()
            self.lv = self.rfsearch.obj(self.reporter.metrics)
            self.rfsearch.update(self.nlist, psel)
            self.reporter.finalize(self.path, psel)
        except ScriptExit:
            self.lv = self.FAIL
        self.opt.tell(psel, self.lv)
        self.reporter.clear()
        if self.lv < self.minimum:
            self.minimum = self.lv
            return True
        return False


class GenericSearch:
    def __init__(self, spec: str, reporter: GenericReporter, obj):
        self.spec = spec
        self._stop = False
        self.best = None
        self.reporter = reporter
        self.obj = obj
        self.total = 0
        self.graph = TGraph(spec)

    def update(self, path: List[TNode], params):
        self.total += 1
        obj = self.obj(self.reporter.metrics)
        if self.best is None:
            self.best = {'obj': obj, 'path': path[:], 'params': params}
        else:
            if self.best['obj'] > obj:
                self.best = {'obj': obj, 'path': path[:], 'params': params}

    def runBest(self):
        if self.best is None:
            return
        pstate = {'global': dict(), 'local': dict()}
        b = 0
        for n in self.best['path']:
            pl = len(n.get_dims())
            scr = n.compile_val(self.best['params'][b:(b + pl)])
            b += pl
            runseg(self.reporter, scr, pstate)

    def run(self):
        def hdlr(sig, frame):
            self._stop = True

        signal.signal(signal.SIGTERM, hdlr)
        signal.signal(signal.SIGINT, hdlr)

    def stop(self):
        if self.best is None:
            return
        print("Ran {} tests with best objective value {:.5}".format(self.total, self.best['obj']))
        print("Running the best performing configuration")
        self.runBest()
        self.reporter.clear()


class RFSearch(GenericSearch):
    def __init__(self, spec: str, reporter: GenericReporter, obj):
        super().__init__(spec, reporter, obj)

    def dfs(self, nodes: List[TNode], space: int):
        node = nodes[-1]
        nspace = space
        for i in node.get_dims():
            nspace = nspace * i
        # Leaf node
        if len(node.children) == 0:
            return [LeafOptimizer(nodes, self)]
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
        super().run()
        # Path explore
        opts = self.dfs([self.graph.root], 1)
        if len(opts) < 1:
            return
        # Optimize
        minimum = LeafOptimizer.FAIL - 1e-5
        lst_imprv = 0
        for i in opts:
            i.l = 1
        while not self._stop:
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
        super().stop()


class ExhaustiveSearch(GenericSearch):
    def __init__(self, spec: str, reporter: GenericReporter, obj):
        super().__init__(spec, reporter, obj)

    def dfs(self, nodes: List[TNode], path: str, pdims: List[int]):
        node = nodes[-1]
        path += node.hash()
        # Copy dimensions
        pdims = pdims[:]
        pdims += node.get_dims()
        # Leaf node
        if len(node.children) == 0:
            # build script
            psel = [0] * len(pdims)
            state = [0] * (len(nodes) + 1)
            state[0] = dill.dumps({'global': dict(), 'local': dict()})
            reports = [0] * (len(nodes) + 1)
            reports[0] = pickle.dumps(dict())
            c = 0
            cnt = 0
            TOT = 1
            for d in pdims:
                TOT *= d
            pos = -1
            while c == 0 and not self._stop:
                print("{} : {:.2%}".format(path, cnt / TOT))
                b = 0
                val = list()
                cur = 0
                while b + len(nodes[cur].get_dims()) <= pos:
                    pl = len(nodes[cur].get_dims())
                    val += nodes[cur].get_pval(psel[b:(b + pl)])
                    b += pl
                    cur += 1
                pos = len(pdims) - 1
                # setup program state
                pstate = dill.loads(state[cur])
                # setup report state
                self.reporter.metrics = pickle.loads(reports[cur])
                try:
                    for n in range(cur, len(nodes)):
                        pl = len(nodes[n].get_dims())
                        val += nodes[n].get_pval(psel[b:(b + pl)])
                        scr = nodes[n].compile(psel[b:(b + pl)])
                        b += pl
                        if runseg(self.reporter, scr, pstate):
                            state[n + 1] = dill.dumps(pstate)
                            reports[n + 1] = pickle.dumps(self.reporter.metrics)
                        else:
                            pos = b - 1
                            raise ScriptExit()
                    self.update(nodes, val)
                    self.reporter.finalize(path, val)
                except ScriptExit:
                    pass
                step = 1
                for n in pdims[(pos+1):]:
                    step *= n
                cnt = cnt + step
                self.reporter.clear()
                # prepare for next
                c = 1
                while c > 0 and pos >= 0:
                    psel[pos] += c
                    if psel[pos] == pdims[pos]:
                        psel[pos] = 0
                        c = 1
                    else:
                        c = 0
                    pos -= 1
                pos += 1
            self.reporter.flush()
        else:
            # Internal node continue dfs
            for c in node.children:
                nodes.append(c)
                self.dfs(nodes, path, pdims)
                nodes.pop()

    def run(self):
        super().run()

        # Path explore
        self.dfs([self.graph.root], "", list())

        self.reporter.flush()
        super().stop()
