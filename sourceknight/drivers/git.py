from .base import basedriver

import git
import os
import logging

from ..utils import ensure_path_exists

class gitdriver (basedriver):
    def __init__(self, ctx, model):
        self._ctx = ctx
        self._model = model

    def check_update(self, current_model):
        return True

    def update(self, mgr):
        loc = os.path.join(self._ctx._path, '.sourceknight', 'cache', self._model.name)
        
        if os.path.isdir(loc):
            repo = git.Repo(loc)
            logging.info(' Pulling from {:s}'.format(repo.remote().url))
            repo.remote().pull()
        else:
            logging.info(' Cloning from {:s}'.format(self._model.params['repo']))
            #ensure_path_exists(loc)
            repo = git.Repo.clone_from(self._model.params['repo'], loc)

        # TODO: handle branches, tags, etc

        self._ctx._state.update(dependencies={
            self._model.name: self._model.state(location=os.path.relpath(loc, self._ctx._path), driver='git')
        })

