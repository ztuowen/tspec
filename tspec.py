from reporter.generic import GenericReporter
from loader import TGraph, TNode
from typing import List


class Tspec:
    VER = 0.01

    def __init__(self, spec: str, reporter: GenericReporter):
        self.spec = spec
        self.reporter = reporter
        self.graph = TGraph(spec)

    def runscr(self, scr, path, param):
        try:
            # exec(scr, {'report': self.reporter}, {})
            print(scr, path, param)
            self.reporter.finalize(path, param)
        except SystemExit:
            print("Script error")
        self.reporter.clear()

    def dfs(self, nodes: List[TNode], path: str, pdims: List[int]):
        node = nodes[-1]
        path += node.hash()
        pdims += node.get_dims()
        # node ends here
        if len(node.children) == 0:
            print(path)
            # build script
            psel = [0] * len(pdims)
            c = 0
            while c == 0:
                scr = ""
                b = 0
                val = list()
                for n in nodes:
                    pl = len(n.get_dims())
                    val += n.get_pval(psel[b:(b + pl)])
                    scr += n.compile(psel[b:(b + pl)])
                    b += pl
                self.runscr(scr, path, val)
                # prepare for next
                i = 0
                c = 1
                while c > 0 and i < len(pdims):
                    psel[i] += c
                    if psel[i] == pdims[i]:
                        psel[i] = 0
                        c = 1
                    else:
                        c = 0
                    i += 1
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
