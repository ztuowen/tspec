from tspec.reporter import GenericReporter
from datetime import datetime
from typing import List
import csv


class CSVReporter(GenericReporter):
    def __init__(self, filename, interval=100):
        super().__init__()
        self.filename = filename
        self.result_cache = list()
        self.interval = interval

    def finalize(self, path: str, param: List[str]):
        # log time
        self.report("path", path)
        self.report("param", param)
        self.report("date", datetime.utcnow())
        self.result_cache.append(self.metrics)
        if len(self.result_cache) >= self.interval:
            self.flush()

    def flush(self):
        if len(self.result_cache) > 0:
            with open(self.filename, 'a') as f:
                writer = csv.writer(f)
                for res in self.result_cache:
                    val = [res[key] for key in sorted(res.keys())]
                    writer.writerow(val)
        self.result_cache = list()
