from tspec.loader import TGraph, TNode
from tspec.reporter import GenericReporter
from typing import List
from tspec.search.helpers import *
import signal


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
            print(n.name, end=": ")
            pl = len(n.get_dims())
            for p, v in zip(n.pname, self.best['params'][b:(b + pl)]):
                print("[{},{}]".format(p, str(repr(v))), end=" ")
            print()
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
        print("Ran {} tests with best objective value {:.5}".format(self.total, float(self.best['obj'])))
        print("Running the best performing configuration")
        self.runBest()
        self.reporter.clear()
