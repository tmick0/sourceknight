import argparse
import sys
import logging

from .context import context
from .update import update
from .status import status
from .unpack import unpack
from .compile import compile
from .build import build
from .errors import skerror

def main():
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    parser = argparse.ArgumentParser("sourceknight", description="simple dependency manager for sourcemod projects")
    parser.add_argument('-p,--path', dest="path", help="Path to the root of your project (directory containing sourceknight.yaml) - defaults to current directory", default=".")

    subparsers = parser.add_subparsers(dest='command')
    subparsers.required = True

    update.add_args(update.install(subparsers))
    status.add_args(status.install(subparsers))
    unpack.add_args(unpack.install(subparsers))
    compile.add_args(compile.install(subparsers))
    build.add_args(build.install(subparsers))

    args = parser.parse_args()

    command_map = {
        'update': update,
        'status': status,
        'unpack': unpack,
        'compile': compile,
        'build': build
    }

    try:
        try:
            command = command_map[args.command]
        except KeyError as e:
            raise skerror("Unknown command {:s}".format(args.command))
        with context(args.path) as ctx:
            command(ctx)(args)
    except skerror as e:
        logging.error(e)
        sys.exit(1)

    sys.exit(0)

