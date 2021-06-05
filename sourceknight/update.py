
class update (object):
    def __init__(self, context):
        self._ctx = context

    def __call__(self, args):
        self._ctx.ensure_working_directory_exists()

        print(args)
        print(self._ctx._defs)
        print(self._ctx._state.serialize())

        for dep in self._ctx._defs['project']['dependencies']:
            print(dep)
