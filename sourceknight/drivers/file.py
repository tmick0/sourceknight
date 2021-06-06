from .base import basedriver

class filedriver (basedriver):
    def __init__(self, ctx, model):
        print(model.params)

    