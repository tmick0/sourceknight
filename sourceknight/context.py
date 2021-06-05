import os
import yaml

try:
    from yaml import CLoader as yamlLoader
except:
    from yaml import Loader as yamlLoader

from .errors import skerror

class context (object):
    def __init__(self, path):
        try:
            path = os.path.join(path, 'sourceknight.yaml')
            with open(path, 'r') as fh:
                self._defs = yaml.load(fh, Loader=yamlLoader)
        except OSError:
            raise skerror("Project directory does not exist or does not contain sourceknight.yaml")
        except yaml.YAMLError as e:
            err_str = str(e)
            if hasattr(e, 'problem_mark'):
                err_str += " ({:s}:{:s})".format(e.problem_mark.line+1, e.problem_mark.column+1)
            raise skerror("Failed parsing sourceknight.yaml: {:s}".format(err_str))
