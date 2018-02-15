from tspec.reporter import GenericReporter
from tspec.loader import TGraph, TNode
from typing import List
import pickle
import dill


class ScriptExit(Exception):
    pass


class Tspec:
    VER = 0.01

    def __init__(self, spec: str, reporter: GenericReporter):
        self.spec = spec
        self.reporter = reporter
        self.graph = TGraph(spec)

    def runseg(self, scr, state):
        state['global']['report'] = self.reporter
        try:
            exec(scr, state['global'], state['local'])
            del state['global']['report']
        except SystemExit:
            print("Script exit early")
            return False
        except Exception as e:
            print("Encountered error when running:")
            print(e)
            print("Script:\n{}".format(scr))
            return False
        return True

    def dfs(self, nodes: List[TNode], path: str, pdims: List[int]):
        node = nodes[-1]
        path += node.hash()
        pdims += node.get_dims()
        # node ends here
        if len(node.children) == 0:
            # build script
            psel = [0] * len(pdims)
            state = [0] * (len(nodes) + 1)
            state[0] = dill.dumps({'global': dict(), 'local': dict()})
            reports = [0] * (len(nodes) + 1)
            reports[0] = pickle.dumps(dict())
            c = 0
            cnt = 1
            TOT = 1
            for d in pdims:
                TOT *= d
            pos = -1
            while c == 0:
                print("{} : {:.2%}".format(path, cnt / TOT))
                cnt += 1
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
                        if self.runseg(scr, pstate):
                            state[n + 1] = dill.dumps(pstate)
                            reports[n + 1] = pickle.dumps(self.reporter.metrics)
                        else:
                            pos = b - 1
                            raise ScriptExit()
                    self.reporter.finalize(path, val)
                except ScriptExit:
                    pass
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
            # continue dfs
            for c in node.children:
                nodes.append(c)
                self.dfs(nodes, path, pdims)
                nodes.pop()

    def run(self):
        # Path explore
        self.dfs([self.graph.root], "", list())

# use exec with global/local dictionary mapping: {} will mask value
