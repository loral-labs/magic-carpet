from typing import Callable, Union
from magic_carpet.common.container import BaseContainer, DictContainer, SetContainer, ListContainer, KeyedContainer
from magic_carpet.models.model import Model, NamedModel

class ModelContainer(Model, BaseContainer):
    def __init__(self, models: list[Union[Model, Callable]] = [], **kwargs):
        BaseContainer.__init__(self, objects=models, **kwargs)

    def run(self, *args, **kwargs):
        return [model(*args, **kwargs) for model in self]
    
class ModelSet(ModelContainer, SetContainer):
    pass

class KeyedModelContainer(ModelContainer, KeyedContainer):
    def format(self, model: Union[Model, Callable]):
        if not isinstance(model, Model):
            if not isinstance(model, Callable):
                raise ValueError(f"Model {model} is not callable.")
            model = Model(model)
        return model
    
    def run(self, *args, keys=None, **kwargs):
        if keys is None:
            keys = self.keys
        return {key: self[key](*args, **kwargs) for key in keys}

class ModelList(KeyedModelContainer, ListContainer):
    pass

class KeyedNamedModelContainer(KeyedModelContainer):
    def format(self, model: Union[NamedModel, dict]):
        if not isinstance(model, NamedModel):
            if not isinstance(model, dict):
                raise ValueError(f"Model {model} is not a dict.")
            model = NamedModel(**model)
        return model

class NamedModelDict(KeyedNamedModelContainer, DictContainer):
    def __init__(self, *args, key_attr="name", **kwargs):
        DictContainer.__init__(self, key_attr=key_attr, **kwargs)
        KeyedNamedModelContainer.__init__(self, *args, **kwargs)
