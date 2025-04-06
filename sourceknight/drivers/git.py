from .base import basedriver

import git
import os
import logging

from sourceknight.utils import extract_and_copy, filemgr

class gitdriver (basedriver):
    def __init__(self, ctx, model):
        super().__init__(ctx, model)

    def check_update(self, current_model):
        return True

    def update(self, mgr):
        loc = str(os.path.join(self.ctx.path, '.sourceknight', 'cache', self.model.name))

        fetched = False
        if os.path.isdir(loc):
            repo = git.Repo(loc)
        else:
            logging.info(' Cloning from {:s}'.format(self.model.params['repo']))
            repo = git.Repo.clone_from(self.model.params['repo'], loc)
            fetched = True

        try:
            if self.model.version is None:
                if not fetched:
                    logging.info(' Pulling from {:s}'.format(repo.remote().url))
                    repo.remote().pull()
                self.model.version = repo.head.commit.hexsha
            else:
                if not fetched:
                    logging.info(' Fetching from {:s}'.format(repo.remote().url))
                    repo.remote().fetch()
                repo.head.reset(self.model.version, working_tree=True)

            self.ctx.state.update(dependencies={
                self.model.name: self.model.state(location=os.path.relpath(loc, self.ctx.path), driver=self.model.type)
            })
        finally:
            repo.close()

    def unpack(self, mgr, locations):
        with filemgr(self.ctx, 'cache') as tmp:
            extract_and_copy(self, locations, mgr, tmp)