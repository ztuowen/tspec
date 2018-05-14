from tspec.reporter import GenericReporter
from tspec.search import RFSearch

# connect to data base
rep = GenericReporter()

tspec = RFSearch("quadratic.yaml", rep, lambda x: x["y"])
tspec.run(wait=100)
