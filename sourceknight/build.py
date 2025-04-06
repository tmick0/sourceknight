from .update import update
from .unpack import unpack
from .compile import compile

import logging

class build (object):
    def __init__(self, ctx):
        self._ctx = ctx
        self._update = update
        self._unpack = unpack
        self._compile = compile

    @classmethod
    def install(cls, subparsers):
        return subparsers.add_parser('build', help='Equivalent to running update, unpack, compile')
    
    @classmethod
    def add_args(cls, parser):
        update.add_args(parser)
        unpack.add_args(parser)
        compile.add_args(parser)

    def __call__(self, args):
        logging.info("Updating...")
        self._update(self._ctx)(args)
        logging.info("Unpacking...")
        self._unpack(self._ctx)(args)
        logging.info("Compiling...")
        self._compile(self._ctx)(args)
        logging.info("Done")
