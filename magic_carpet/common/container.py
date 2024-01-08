class BaseContainer:
    def __init__(self, objects: list = [], **kwargs):
        self.objects = objects
    
    def __contains__(self, object):
        return self.has_object(object)
    
    def __add__(self, other):
        try:
            self.objects = (self.objects + other.objects)
        except:
            raise TypeError(f"Cannot add containers because cannot add {type(self.objects)} to {type(other.objects)}.")
        return self
    
    def __iter__(self):
        return iter(self.objects)
    
    @property
    def objects(self):
        if not hasattr(self, "_objects"):
            raise AttributeError("Container has no objects.")
        return self._objects
    
    @objects.setter
    def objects(self, objects: list):
        self.clear()
        for object in objects:
            self.add_object(object)

    @objects.deleter
    def objects(self):
        del self._objects
    
    def has_object(self, object):
        raise NotImplementedError

    def add_object(self, object):
        raise NotImplementedError
    
    def clear(self):
        raise NotImplementedError
    
class SetContainer(BaseContainer):
    def has_object(self, object):
        return (object in self._objects)
    
    def add_object(self, object):
        self._objects.add(object)

    def clear(self):
        self._objects = set([])

class FormatContainer(BaseContainer):
    def format(self, object):
        return object
    
    def has_object(self, object):
        return self.has(self.format(object))

    def add_object(self, object):
        return self.add(self.format(object))

    def has(self, object):
        raise NotImplementedError

    def add(self, object):
        raise NotImplementedError
    
class KeyedContainer(FormatContainer):
    def __len__(self):
        return len(self.objects)
    
    def __getitem__(self, key):
        try:
            return self.objects[key]
        except KeyError:
            raise KeyError(f"Container has no object at key {key}.")
    
    def __setitem__(self, key, object):
        self.objects[key] = self.format(object)
    
    def __delitem__(self, key):
        del self.objects[key]
    
    def has(self, object):
        return (self.get_key(object) in self)
    
    def keys(self):
        raise NotImplementedError
    
    def values(self):
        return [self[key] for key in self]
    
    def get_key(self, object):
        object = self.format(object)
        try:
            return self.extract_key(object)
        except NotImplementedError:
            if not (object in self.values()):
                return None
            return self.keys()[self.values().index(object)]
    
    def extract_key(self, object):
        raise NotImplementedError
    
class ListContainer(KeyedContainer):
    def keys(self):
        return list(range(len(self._objects)))
    
    def add(self, object):
        self._objects.append(object)

    def clear(self):
        self._objects = []

class DictContainer(KeyedContainer):
    def __init__(self, *args, key_attr, **kwargs):
        self.key_attr = key_attr
        KeyedContainer.__init__(self, *args, **kwargs)

    def __contains__(self, key):
        return (key in self.keys())

    def __iter__(self):
        return iter(self.keys())
        
    def keys(self):
        return list(self._objects.keys())
    
    def items(self):
        return list(zip(self.keys(), self.values()))
    
    def extract_key(self, object):
        if not hasattr(object, self.key_attr):
            raise AttributeError(f"Item {object} has no attribute {self.key_attr}.")
        return getattr(object, self.key_attr)
    
    def add(self, object):
        self._objects[self.extract_key(object)] = object

    def clear(self):
        self._objects = {}

    

    


