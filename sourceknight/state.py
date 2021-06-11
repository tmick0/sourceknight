
class state (object):
    def __init__(self):
        self._dict = {}
        self._dict['dependencies'] = {}
        self._dict['build'] = {}
        self._clean = True
    
    def clean(self):
        return self._clean

    def __getattr__(self, key):
        try:
            return self._dict[key]
        except KeyError:
            raise AttributeError(key)

    def update(self, **kwargs):
        def merge(dest, src):
            for k, v in src.items():
                if isinstance(v, dict) and k in dest:
                    merge(dest[k], v)
                else:
                    dest[k] = v
        merge(self._dict, kwargs)
        self._clean = False

    def serialize(self):
        return self._dict

    @classmethod
    def from_yaml(cls, defs, data):
        instance = cls()
        instance.update(**data)
        return instance
