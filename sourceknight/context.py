import os
import yaml

try:
    from yaml import CLoader as yamlLoader
    from yaml import CDumper as yamlDumper
except:
    from yaml import Loader as yamlLoader
    from yaml import Dumper as yamlDumper

from .errors import skerror
from .state import state
from .utils import ensure_path_exists, check_version

class context (object):
    def __init__(self, path):
        self._path = path
        self._exists = False

    def ensure_working_directory_exists(self):
        if not self._exists:
            ensure_path_exists(os.path.join(self._path, '.sourceknight'))
            self._exists = True

    def __enter__(self):
        # load project definitions
        try:
            path = os.path.join(self._path, 'sourceknight.yaml')
            with open(path, 'r') as fh:
                self._defs = yaml.load(fh, Loader=yamlLoader)
        except OSError:
            raise skerror("Project directory does not exist or does not contain sourceknight.yaml")
        except yaml.YAMLError as e:
            err_str = str(e)
            if hasattr(e, 'problem_mark'):
                err_str += " ({:s}:{:s})".format(e.problem_mark.line+1, e.problem_mark.column+1)
            raise skerror("Failed parsing sourceknight.yaml: {:s}".format(err_str))

        check_version(self._defs)

        # load or create state
        try:
            path = os.path.join(self._path, '.sourceknight', 'state.yaml')
            with open(path, 'r') as fh:
                self._state = state.from_yaml(self._defs, yaml.load(fh, Loader=yamlLoader))
            self._exists = True
        except OSError:
            self._state = state()
        except yaml.YAMLError as e:
            raise skerror("sourceknight state is corrupted, try removing the .sourceknight directory")\

        return self

    def __exit__(self, *exception):
        # dump state if updated
        if self._state and not self._state.clean():
            self.ensure_working_directory_exists()
            path = os.path.join(self._path, '.sourceknight', 'state.yaml')
            with open(path, 'w') as fh:
                yaml.dump(self._state.serialize(), fh)
