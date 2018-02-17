# This is a reporter template
from typing import List
import abc


class GenericReporter:
    def __init__(self, evalfunc):
        self.metrics = dict()
        self._eval = evalfunc

    def evaluate(self):
        return self._eval(self.metrics)

    def clear(self):
        # called when script/program finishes/fails to clear internal state
        self.metrics = dict()
        pass

    def report(self, name: str, val):
        # this report a specific named value
        self.metrics[name] = val
        pass

    @abc.abstractmethod
    def finalize(self, path: str, param: List[str]):
        # to be called after one variant finished reporting
        pass

    @abc.abstractmethod
    def flush(self):
        # to be called to force flushing of pending result in cache
        pass

    def __call__(self, name: str, val):
        # alias for report, no need to overload
        return self.report(name, val)


class GenericQuery:
    @abc.abstractmethod
    def get(self, path: str, param: List[str], metric: str):
        # Usage:
        #   path   : a generated path from a script - always from root(prefix)
        #   param  : a list of parameters - TODO: best representation
        #       online can only store parameters in value format as the position
        #       might change with new variable added or deleted
        #   metric : the name of the interested metric
        pass
