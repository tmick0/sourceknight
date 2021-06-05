import argparse
import sys

from .update import update
from .errors import skerror

def main():
    parser = argparse.ArgumentParser("sourceknight", description="simple dependency manager for sourcemod projects")
    parser.add_argument('-p,--path', dest="path", help="Path to the root of your project (directory containing sourceknight.yaml) - defaults to current directory", default=".")

    subparsers = parser.add_subparsers(dest='command')
    subparsers.required = True
    update_parser = subparsers.add_parser('update', help='Fetch or update dependencies')
    update_parser.add_argument('-f,--force', dest='force', action='store_true', help="Force updating all dependencies, even if they are believed to be up to date")

    args = parser.parse_args()

    command_map = {
        'update': update
    }

    context_args = [args.path]

    try:
        try:
            command = command_map[args.command]
        except KeyError as e:
            raise skerror("Unknown command {:s}".format(args.command))

        command(args.path)(args)

    except skerror as e:
        print(e)
        sys.exit(1)

    sys.exit(0)

