
from .dependencies import depmgr
from .utils import filemgr
import os
import shutil

class unpack (object):
    def __init__(self, context):
        self._ctx = context

    @classmethod
    def install(cls, subparsers):
        parser = subparsers.add_parser('unpack', help='Unpack dependencies into build directory')
        parser.add_argument('-f,--force', dest='force', action='store_true', help="Force unpacking all dependencies, even if they have not been updated")
        parser.add_argument('-c,--clean', dest='clean', action='store_true', help="Force creating a new unpack directory, even if one already exists")

    def __call__(self, args):
        self._ctx.ensure_working_directory_exists()

        if args.clean:
            d = os.path.join(self._ctx._path, '.sourceknight', 'build')
            print("Deleting existing build directory ({:s})...".format(d))
            shutil.rmtree(d)

        dmgr = depmgr(self._ctx)
        with filemgr(self._ctx, "build", True) as fmgr:
            try:
                for dep in self._ctx._defs['project']['dependencies']:
                    dmgr.unpack(self._ctx._state.dependencies[dep['name']], dep['unpack'], fmgr, args.force)
                fmgr.release_dir()
            except:
                print("Error occurred during unpack, removing build tree...")
                raise
