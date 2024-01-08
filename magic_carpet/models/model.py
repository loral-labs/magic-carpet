import inspect
from abc import ABC, abstractmethod
from typing import Callable

class BaseModel(ABC):
    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, *args, **kwargs):
        raise NotImplementedError

    
class Model(BaseModel):
    def __init__(self, function: Callable = None, **kwargs):
        if function is not None:
            self.run = function

    def __call__(self, *args, **kwargs):
        return self.run(*args, **kwargs)
    
    def __eq__(self, other):
        return self.run == other.run
    
    def run(self, *args, **kwargs):
        raise NotImplementedError

class NamedModel(Model):
    def __init__(self, name: str = None, description: str = None, **kwargs):
        Model.__init__(self, **kwargs)
        self._name = name
        self._description = description

    def __repr__(self) -> str: 
        return self.name

    def info(self) -> str: 
        return f"NAME: {self.name}\nDESCRIPTION: {self.description}"
    
    def __eq__(self, other):
        return Model.__eq__(self, other) and repr(self) == repr(other)
    
    @property
    def name(self):
        if self._name is not None:
            return self._name
        return self.name_default()
    
    @name.setter
    def name(self, value):
        self._name = value

    @property
    def description(self):
        if self._description is not None:
            return self._description
        return self.description_default()
    
    @description.setter
    def description(self, value):
        self._description = value

    def name_default(self):
        return self.__class__.__name__ 
    
    def description_default(self):
        return "This model executes the following function code\n```\n" + inspect.getsource(self.run) + "\n```\n"
    
