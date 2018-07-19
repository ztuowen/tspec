from tspec.reporter import CSVReporter
from tspec.search import RFSearch

# connect to data base
rep = CSVReporter("result.csv")

tspec = RFSearch("quadratic.yaml", rep, lambda x: x["y"])
tspec.run(wait=100)
