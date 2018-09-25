from typing import List
import dill
import pickle
from tspec.search.generic import GenericSearch
from tspec.search.helpers import *
from tspec.reporter import GenericReporter
from tspec.loader import TNode


class ExhaustiveSearch(GenericSearch):
    def __init__(self, spec: str, reporter: GenericReporter, obj, cont=False):
        super().__init__(spec, reporter, obj)
        self.cont = cont

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

            # start from last result
            if self.cont:
                last = self.reporter.last_in_path(path)
            else:
                last = None
            if last is not None:
                lpos = 0
                for n in range(len(nodes)):
                    pl = nodes[n].get_dims()
                    for p, p_cnt in enumerate(pl):
                        last_param = last[lpos + p]
                        last_pick = None
                        for param in range(p_cnt):
                            if nodes[n].get_pval_at(p, param) == last_param:
                                last_pick = param
                        psel[lpos + p] = last_pick
                    lpos += len(pl)
                # cnt is messed up here
                # Will rerun the last one
            c = 0
            cnt = 0
            TOT = 1
            for d in pdims:
                TOT *= d
            pos = -1
            while c == 0 and not self._stop:
                print("{} {} : {:.2%}".format(
                    self.best['obj'] if self.best else "None", path, cnt / TOT))
                b = 0
                val = list()
                cur = 0
                while b + len(nodes[cur].get_dims()) <= pos:
                    pl = len(nodes[cur].get_dims())
                    val += nodes[cur].get_pval(psel[b:(b + pl)])
                    b += pl
                    cur += 1
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
                for n in pdims[(pos + 1):]:
                    step *= n
                cnt = cnt + step
                self.reporter.clear()
                # prepare for next
                pos = len(pdims) - 1
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
