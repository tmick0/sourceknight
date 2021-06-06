from .base import basedriver
from ..utils import filemgr

import logging


class tardriver (basedriver):
    def __init__(self, ctx, model):
        self._ctx = ctx
        self._model = model

    def update(self):
        with filemgr(self._ctx) as mgr:
            path = mgr.acquire(self._model.params['location'])
            print(path)
            with open(path, 'rb') as fh:
                print(len(fh.read()))
            