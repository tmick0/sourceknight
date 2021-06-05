from .context import context

class update (context):
    def __call__(self, args):
        print(args)
        print(self._defs)
