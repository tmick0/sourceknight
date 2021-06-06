
from .drivers import tardriver, gitdriver, filedriver
import logging

class dependency (object):
    def __init__(self):
        self.name = None
        self.type = None
        self.version = None
        self.params = {}

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

    def update(self, dep, force=False):
        new_model = dependency.from_yaml(dep)
        current_model = None
        try:
            current_model = dependency.from_yaml(self._ctx._state.dependencies[new_model.name])
        except KeyError:
            pass

        driver = drivers_by_name[new_model.type](self._ctx, new_model)
        if current_model is None:
            force = True

        if current_model is None:
            force = True
        else:
            if current_model.version is not None and current_model.version != new_model.version:
                force = True
            elif driver.check_update(current_model):
                force = True

        if force:
            logging.info("Updating `{}`".format(new_model.name))
            driver.update()
