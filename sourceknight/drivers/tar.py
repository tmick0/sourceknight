from .base import basedriver
from ..utils import filemgr

import logging
import os


class tardriver (basedriver):
    def __init__(self, ctx, model):
        self._ctx = ctx
        self._model = model

    def cleanup(self):
        os.unlink(os.path.join(self._ctx._path, self._model.params['location']))

    def update(self, mgr):
        path = mgr.acquire(self._model.params['location'])
        mgr.release(path)
        self._ctx._state.update(dependencies={
            self._model.name: self._model.state(location=os.path.relpath(path, self._ctx._path), driver='tar')
        })
