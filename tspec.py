from reporter.generic import genericReporter
import yaml


class Tspec:
    def __init__(self, spec: str, reporter: genericReporter):
        self.spec = spec
        self.reporter = reporter


class Range:
    yaml_tag = u'!range'

    def __init__(self, dat):
        self.dat = dat

    def __str__(self):
        return "Range({})".format(str(self.dat))

    def __repr__(self):
        return str(self)

    @classmethod
    def from_yaml(cls, loader, node):
        value = loader.construct_sequence(node)
        return Range(value)


f = open("example.yaml", "r")
yaml.SafeLoader.add_constructor(Range.yaml_tag, Range.from_yaml)
y = yaml.safe_load(f)
print(y)
