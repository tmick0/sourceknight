
from .drivers import tardriver, gitdriver, filedriver
import logging

class dependency (object):
    def __init__(self):
        self.name = None
        self.type = None
        self.version = None
        self.params = {}

    def state(self, **kwargs):
        d = {
            'name': self.name,
            'version': self.version
        }
        d.update(kwargs)
        return d

    @classmethod
    def from_yaml(cls, data):
        o = cls()
        def unpack(name=None, type=None, version=None, **kwargs):
            o.name = name
            o.type = type
            o.version = version
            o.params.update(kwargs)
        unpack(**data)
        return o


drivers_by_name = {
    'tar': tardriver,
    'git': gitdriver,
    'file': filedriver
}


class depmgr (object):
    def __init__(self, ctx):
        self._ctx = ctx

    def unpack(self, dep, locations, fmgr, force=False):
        d = dependency.from_yaml(dep)
        current_model = None
        try:
            current_model = dependency.from_yaml(self._ctx._state.build[d.name])
        except KeyError:
            pass

        unpack = False
        if force:
            unpack = True
        elif d.version is None:
            unpack = True
        elif current_model is None:
            unpack = True
        elif d.version != current_model.version:
            unpack = True
        
        if unpack:
            logging.info("Unpacking {:s}...".format(d.name))
            drivers_by_name[d.params['driver']](self._ctx, d).unpack(fmgr, locations)
        else:
            logging.info("Already up to date: {}".format(d.name))

    def update(self, dep, fmgr, force=False):
        new_model = dependency.from_yaml(dep)
        current_model = None
        try:
            current_model = dependency.from_yaml(self._ctx._state.dependencies[new_model.name])
        except KeyError:
            pass

        driver = drivers_by_name[new_model.type](self._ctx, new_model)

        if force or driver.check_update(current_model):
            logging.info("Updating: {}".format(new_model.name))
            if current_model is not None:
                drivers_by_name[current_model.params['driver']](self._ctx, current_model).cleanup()
            driver.update(fmgr)
        else:
            logging.info("Already up to date: {}".format(new_model.name))
