from tspec.reporter import GenericReporter
from typing import List
from datetime import datetime


class MongoReporter(GenericReporter):
    def __init__(self, evalfunc, dbcollection, tag, interval=100):
        super().__init__(evalfunc)
        self.db = dbcollection
        self.tag = tag
        self.result_cache = list()
        self.interval = interval

    def finalize(self, path: str, param: List[str]):
        # log time
        self.report("tag", self.tag)
        self.report("path", path)
        self.report("param", param)
        self.report("date", datetime.utcnow())
        self.result_cache.append(self.metrics)
        if len(self.result_cache) >= self.interval:
            self.flush()

    def flush(self):
        if len(self.result_cache) > 0:
            self.db.insert_many(self.result_cache)
        self.result_cache = list()
