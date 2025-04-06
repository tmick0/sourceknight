import logging
import os
import platform
import shutil
import subprocess

from .errors import skerror
from .utils import cd, ensure_path_exists

class compile (object):
    if platform.architecture()[0] == '64bit':
        _default_compiler = "/addons/sourcemod/scripting/spcomp64"
    else:
        _default_compiler = "/addons/sourcemod/scripting/spcomp"
    _default_workdir = "/addons/sourcemod/scripting/"

    def __init__(self, context):
        self._ctx = context

    @classmethod
    def install(cls, subparsers):
        return subparsers.add_parser('compile', help='Runs the build steps specified in the configuration')
    
    @classmethod
    def add_args(cls, parser):
        parser.add_argument('-o,--output-dir', dest='output', default=None, help='Specify directory to store compiled smx files (default from manifest, or current directory if not specified)')
        parser.add_argument('targets', nargs='*', help='List of specific targets to compile (by default, will compile all)')

    def __call__(self, args):
        self._ctx.ensure_working_directory_exists()

        all_targets = self._ctx.defs['targets']
        targets = args.targets
        if not len(targets):
            targets = all_targets
        elif any(t not in all_targets for t in targets):
            raise skerror("One or more of specified targets not defined: {}".format(', '.join(targets)))

        try:
            workdir = self._ctx.defs['workdir']
        except KeyError:
            workdir = self._default_workdir
        if workdir[0] == '/':
            workdir = workdir[1:]

        try:
            compiler = self._ctx.defs['compiler']
        except KeyError:
            compiler = self._default_compiler
        if compiler[0] == '/':
            compiler = compiler[1:]

        try:
            root = self._ctx.defs['root']
            if root[0] == '/':
                root = root[1:]
        except KeyError:
            root = None

        output = args.output
        if output is None:
            output = '.'
            try:
                output = self._ctx.defs['output']
                if output[0] == '/':
                    output = output[1:]
            except KeyError:
                pass

        buildroot = os.path.join(self._ctx.path, '.sourceknight', 'build')
        workdir = os.path.join(buildroot, workdir)
        compiler = os.path.abspath(os.path.join(buildroot, compiler))
        outdir = os.path.relpath(os.path.abspath(output), workdir)

        if root is not None:
            logging.info("Copying sources...")
            def copy_filter(directory, contents):
                return list(filter(lambda c: c[0] == '.', contents))
            shutil.copytree(str(os.path.join(self._ctx.path, root)), buildroot, dirs_exist_ok=True, ignore=copy_filter)

        with cd(workdir):
            ensure_path_exists(outdir)
            for t in targets:
                infile = '{:s}.sp'.format(t)
                outfile = os.path.join(outdir, '{:s}.smx'.format(t))
                logging.info("Building {}...".format(t))
                subprocess.run([compiler, infile, "-o{}".format(outfile)])
