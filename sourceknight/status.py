
from .dependencies import dependency

class status (object):
    def __init__(self, context):
        self._ctx = context

    @classmethod
    def install(cls, subparsers):
        parser = subparsers.add_parser('status', help='Print status of dependencies')
        parser.add_argument('-v,--verbose', dest='verbose', action='store_true', help="Print additional information")

    def __call__(self, args):
        for dep in map(dependency.from_yaml, self._ctx._defs['project']['dependencies']):
            d = dependency.from_yaml(self._ctx._state.dependencies[dep.name])
            print(dep.name)
            if d.version is not None:
                print(" Installed version: {:s}".format(d.version))
            if args.verbose:
                print(" Additional parameters:")
                for k, v in d.params.items():
                    print("  {:s} = {:s}".format(k,v))

