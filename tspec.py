from reporter.generic import genericReporter
from loader import TGraph


class Tspec:
    def __init__(self, spec: str, reporter: genericReporter):
        self.spec = spec
        self.reporter = reporter


# use exec with global/local dictionary mapping: {} will mask value


