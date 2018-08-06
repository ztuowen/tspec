from tspec.reporter import CSVReporter
from tspec.search import RFSearch
from tspec.search import ExhaustiveSearch

# connect to data base
rep = CSVReporter("result.csv")

tspec = ExhaustiveSearch("quadratic.yaml", rep, lambda x: x["y"])
tspec.run()
