from .base import basedriver

import git
import os
import logging
import shutil

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
            repo = git.Repo.clone_from(self._model.params['repo'], loc)

        # TODO: handle branches, tags, etc
        if self._model.version is None:
            self._model.version = repo.head.commit.hexsha
        self._ctx._state.update(dependencies={
            self._model.name: self._model.state(location=os.path.relpath(loc, self._ctx._path), driver='git')
        })

    def unpack(self, mgr, locations):
        for l in locations:
            if l['source'][0] == '/':
                l['source'] = l['source'][1:]
            if l['dest'][0] == '/':
                l['dest'] = l['dest'][1:]
            logging.info(" Extracting {} to {}".format(l['source'], l['dest']))
            src = os.path.join(self._ctx._path, self._model.params['location'], l['source'])
            dst = os.path.join(mgr._path, l['dest'])
            if os.path.isdir(src):
                ensure_path_exists(dst)
                shutil.copytree(src, dst, dirs_exist_ok=True)
            else:
                ensure_path_exists(os.path.dirname(dst))
                shutil.copyfile(src, dst)
        self._ctx._state.update(build={
            self._model.name: self._model.state(driver='git')
        })
