from .base import basedriver

class gitdriver (basedriver):
    def __init__(self, ctx, model):
        print(model.params)
