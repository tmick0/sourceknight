
class basedriver (object):
    def __init__(self, ctx, model):
        self.ctx = ctx
        self.model = model

    def check_update(self, current):
        if current is None:
            return True
        if current.version is None:
            return True
        if current.version != self.model.version:
            return True
        return False

    def update(self, fmgr):
        raise NotImplementedError()

    def unpack(self, fmgr, locations):
        raise NotImplementedError()

    def cleanup(self):
        pass
