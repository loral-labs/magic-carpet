from typing import Callable, Union
from magic_carpet.common.container import BaseContainer, DictContainer, SetContainer, ListContainer, KeyedContainer
from magic_carpet.evaluators.evaluator import Evaluator, NamedEvaluator

class EvalContainer(Evaluator, BaseContainer):
    def __init__(self, evaluators: list[Union[Evaluator, Callable]] = [], **kwargs):
        BaseContainer.__init__(self, objects=evaluators, **kwargs)

    def run(self, *args, **kwargs):
        return [evaluator(*args, **kwargs) for evaluator in self]
    
class EvalSet(EvalContainer, SetContainer):
    pass

class KeyedEvalContainer(EvalContainer, KeyedContainer):
    def format(self, evaluator: Union[Evaluator, Callable]):
        if not isinstance(evaluator, Evaluator):
            if not isinstance(evaluator, Callable):
                raise ValueError(f"Evaluator {evaluator} is not callable.")
            evaluator = Evaluator(evaluator)
        return evaluator
    
    def run(self, *args, keys=None, **kwargs):
        if keys is None:
            keys = self.keys
        return {key: self[key](*args, **kwargs) for key in keys}

class EvalList(KeyedEvalContainer, ListContainer):
    pass

class KeyedNamedEvalContainer(KeyedEvalContainer):
    def format(self, evaluator: Union[NamedEvaluator, dict]):
        if not isinstance(evaluator, NamedEvaluator):
            if not isinstance(evaluator, dict):
                raise ValueError(f"Evaluator {evaluator} is not a dict.")
            evaluator = NamedEvaluator(**evaluator)
        return evaluator

class NamedEvalDict(KeyedNamedEvalContainer, DictContainer):
    def __init__(self, *args, key_attr="name", **kwargs):
        DictContainer.__init__(self, key_attr=key_attr, **kwargs)
        KeyedNamedEvalContainer.__init__(self, *args, **kwargs)
