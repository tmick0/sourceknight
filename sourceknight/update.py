
from .dependencies import depmgr
from .utils import filemgr

class update (object):
    def __init__(self, context):
        self._ctx = context

    def __call__(self, args):
        self._ctx.ensure_working_directory_exists()
        dmgr = depmgr(self._ctx)
        with filemgr(self._ctx, "cache") as fmgr:
            for dep in self._ctx._defs['project']['dependencies']:
                dmgr.update(dep, fmgr, args.force)
