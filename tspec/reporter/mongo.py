from typing import List
from datetime import datetime
from tspec.reporter import GenericReporter


class MongoReporter(GenericReporter):
    def __init__(self, dbcollection, tag, interval=100):
        super().__init__()
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
        if self.result_cache:
            self.db.insert_many(self.result_cache)
        self.result_cache = list()

    def last_in_path(self, path):
        last = self.db.find_one({"tag": self.tag, "path": path},
                                sort=[("date", -1)])
        if last:
            return last['param']
        return None
