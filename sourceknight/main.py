import argparse
import sys
import logging

from .context import context
from .update import update
from .status import status
from .unpack import unpack
from .compile import compile
from .errors import skerror

def main():
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    parser = argparse.ArgumentParser("sourceknight", description="simple dependency manager for sourcemod projects")
    parser.add_argument('-p,--path', dest="path", help="Path to the root of your project (directory containing sourceknight.yaml) - defaults to current directory", default=".")

    subparsers = parser.add_subparsers(dest='command')
    subparsers.required = True
    update.install(subparsers)
    status.install(subparsers)
    unpack.install(subparsers)
    compile.install(subparsers)

    args = parser.parse_args()

    command_map = {
        'update': update,
        'status': status,
        'unpack': unpack,
        'compile': compile
    }

    try:
        try:
            command = command_map[args.command]
        except KeyError as e:
            raise skerror("Unknown command {:s}".format(args.command))
        with context(args.path) as ctx:
            command(ctx)(args)
    except skerror as e:
        print(e)
        sys.exit(1)

    sys.exit(0)

