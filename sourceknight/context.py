import os
import yaml

try:
    from yaml import CLoader as yamlLoader
    from yaml import CDumper as yamlDumper
except ImportError:
    from yaml import Loader as yamlLoader
    from yaml import Dumper as yamlDumper

from .errors import skerror
from .state import state

class context (object):
    def __init__(self, path):
        self.path = path
        self._exists = False

    def ensure_working_directory_exists(self):
        if not self._exists:
            from sourceknight.utils import ensure_path_exists
            ensure_path_exists(os.path.join(self.path, '.sourceknight'))
            self._exists = True

    def __enter__(self):
        from sourceknight.utils import check_version
        # load project definitions
        try:
            path = os.path.join(self.path, 'sourceknight.yaml')
            with open(path, 'r') as fh:
                self.defs: dict = yaml.load(fh, Loader=yamlLoader)['project']
        except OSError:
            raise skerror("Project directory does not exist or does not contain sourceknight.yaml")
        except yaml.YAMLError as e:
            err_str = str(e)
            if hasattr(e, 'problem_mark'):
                err_str += " ({:s}:{:s})".format(e.problem_mark.line+1, e.problem_mark.column+1)
            raise skerror("Failed parsing sourceknight.yaml: {:s}".format(err_str))

        check_version(self.defs)

        # load or create state
        try:
            path = os.path.join(self.path, '.sourceknight', 'state.yaml')
            with open(path, 'r') as fh:
                self.state = state.from_yaml(self.defs, yaml.load(fh, Loader=yamlLoader))
            self._exists = True
        except OSError:
            self.state = state()
        except yaml.YAMLError:
            raise skerror("sourceknight state is corrupted, try removing the .sourceknight directory")\

        return self

    def __exit__(self, *exception):
        # dump state if updated
        if self.state and not self.state.clean():
            self.ensure_working_directory_exists()
            path = os.path.join(self.path, '.sourceknight', 'state.yaml')
            with open(path, 'w') as fh:
                yaml.dump(self.state.serialize(), fh)
