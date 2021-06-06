
from .dependencies import depmgr

class update (object):
    def __init__(self, context):
        self._ctx = context

    def __call__(self, args):
        self._ctx.ensure_working_directory_exists()
        mgr = depmgr(self._ctx)
        for dep in self._ctx._defs['project']['dependencies']:
            mgr.update(dep, args.force)
