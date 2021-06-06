
class basedriver (object):
    def __init__(self, **parms):
        pass

    def check_update(self, current):
        return True

    def update(self):
        raise NotImplementedError()
