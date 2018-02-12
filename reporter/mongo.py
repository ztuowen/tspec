import pymongo
from reporter.generic import GenericReporter
from typing import List


class MongoReporter(GenericReporter):
    def __init__(self, dbcollection):
        super()
        self.db = dbcollection

    def report(self, name: str, val):
        pass

    def finalize(self, path: List[str], config: List[int]):
        pass
