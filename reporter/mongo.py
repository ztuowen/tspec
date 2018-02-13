from reporter.generic import GenericReporter
from typing import List
from datetime import datetime


class MongoReporter(GenericReporter):
    def __init__(self, dbcollection, tag):
        super().__init__()
        self.db = dbcollection
        self.tag = tag

    def finalize(self, path: str, param: List[str]):
        # log time
        self.report("tag", self.tag)
        self.report("path", path)
        self.report("param", param)
        self.report("date", datetime.utcnow())
        self.db.insert_one(self.metrics)
