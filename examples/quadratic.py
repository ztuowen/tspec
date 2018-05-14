from tspec.reporter import GenericReporter
from tspec import *

# connect to data base
rep = GenericReporter()

tspec = RFSearch("quadratic.yaml", rep, lambda x: x["y"])
tspec.run(wait=50)
