from abc import ABC, abstractmethod
import inspect
from typing import Callable 

class BaseEvaluator(ABC):
    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, *args, **kwargs):
        raise NotImplementedError
    
class Evaluator(BaseEvaluator):
    def __init__(self, function: Callable = None, **kwargs):
        if function is not None:
            self.evaluate = function

    def __call__(self, *args, **kwargs):
        return self.evaluate(*args, **kwargs)
    
    def __eq__(self, other):
        return self.evaluate == other.evaluate
    
    def evaluate(self, *args, **kwargs):
        raise NotImplementedError
    
class NamedEvaluator(Evaluator):
    def __init__(self, name: str = None, description: str = None, **kwargs):
        Evaluator.__init__(self, **kwargs)
        self.name = name
        self.description = description
    def __str__(self) -> str: 
        return self.name

    def __repr__(self) -> str: 
        return f"NAME: {self.name}\nDESCRIPTION: {self.description}"
    
    def __eq__(self, other):
        return Evaluator.__eq__(self, other) and repr(self) == repr(other)
    
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
        return "This evaluator executes the following function code\n```\n" + inspect.getsource(self.evaluate) + "\n```\n"
    


        