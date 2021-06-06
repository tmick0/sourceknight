
class state (object):
    def __init__(self, defs):
        self._dict = {}
        self._dict['project'] = defs
        self._dict['dependencies'] = {}
        self._clean = True
    
    def clean(self):
        return self._clean

    def __getattr__(self, key):
        try:
            return self._dict[key]
        except KeyError:
            raise AttributeError(key)

    def update(self, **kwargs):
        self._dict.update(kwargs)
        self._clean = False

    def serialize(self):
        return self._dict

    @classmethod
    def from_yaml(cls, defs, data):
        instance = cls(defs)
        instance._dict.update(data)
        return instance
