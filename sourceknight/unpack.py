
from .dependencies import depmgr
from .utils import filemgr
import os
import shutil
import logging

class unpack (object):
    def __init__(self, context):
        self._ctx = context

    @classmethod
    def install(cls, subparsers):
        return subparsers.add_parser('unpack', help='Unpack dependencies into build directory')
    
    @classmethod
    def add_args(cls, parser):
        parser.add_argument('-a,--all', dest='force', action='store_true', help="Force unpacking all dependencies, even if they have not been updated")
        parser.add_argument('-c,--clean', dest='clean', action='store_true', help="Force creating a new unpack directory, even if one already exists")

    def __call__(self, args):
        self._ctx.ensure_working_directory_exists()

        if args.clean:
            d = os.path.join(self._ctx._path, '.sourceknight', 'build')
            logging.info("Deleting existing build directory ({:s})...".format(d))
            for k in list(self._ctx._state.build):
                del self._ctx._state.build[k]
            try:
                shutil.rmtree(d)
            except FileNotFoundError:
                pass

        dmgr = depmgr(self._ctx)
        with filemgr(self._ctx, "build", True) as fmgr:
            try:
                for dep in self._ctx._defs['project']['dependencies']:
                    dmgr.unpack(self._ctx._state.dependencies[dep['name']], dep['unpack'], fmgr, args.force)
                fmgr.release_dir()
            except:
                logging.info("Error occurred during unpack, removing build tree...")
                raise
