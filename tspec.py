from reporter.generic import GenericReporter
from loader import TGraph


class Tspec:
    def __init__(self, spec: str, reporter: GenericReporter):
        self.spec = spec
        self.reporter = reporter
        self.graph = TGraph(spec)

    def run(self):
        # Path explore
        #
        pass

# use exec with global/local dictionary mapping: {} will mask value
