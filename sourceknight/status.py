
from .dependencies import dependency

import logging

class status (object):
    def __init__(self, context):
        self._ctx = context

    @classmethod
    def install(cls, subparsers):
        return subparsers.add_parser('status', help='Print status of dependencies')
    
    @classmethod
    def add_args(cls, parser):
        parser.add_argument('-v,--verbose', dest='verbose', action='store_true', help="Print additional information")

    def __call__(self, args):
        for dep in map(dependency.from_yaml, self._ctx._defs['project']['dependencies']):
            cache = dependency()
            build = dependency()
            if dep.name in self._ctx._state.dependencies:
                cache = dependency.from_yaml(self._ctx._state.dependencies[dep.name])
            if dep.name in self._ctx._state.build:
                build = dependency.from_yaml(self._ctx._state.build[dep.name])
            logging.info(dep.name)
            if cache.version is not None:
                logging.info(" Cached version: {:s}".format(cache.version))
            if build.version is not None:
                logging.info(" Unpacked version: {:s}".format(build.version))
            if args.verbose:
                logging.info(" Additional parameters:")
                for k, v in cache.params.items():
                    logging.info("  {:s} = {:s}".format(k,v))
