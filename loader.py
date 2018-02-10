import yaml


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


class TGraph:
    def __init__(self, fname: str):
        f = open(fname, "r")
        y = yaml.safe_load(f)
        print(y)

    def buildScript(self, path, params):
        pass


yaml.SafeLoader.add_constructor(Range.yaml_tag, Range.from_yaml)
