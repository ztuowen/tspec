# This is a reporter template
from typing import List


class genericReporter:
    def report(self, name: str, val):
        # this report a specific named value
        pass

    def finalize(self, path: List[str], config: List[int]):
        # to be called after one variant finished reporting
        #
        pass

    def __call__(self, name: str, val):
        # alias for report, no need to overload
        return self.report(name, str)