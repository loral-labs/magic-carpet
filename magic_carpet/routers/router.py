from abc import ABC, abstractmethod
from typing import Callable, Tuple, Union
from magic_carpet.models.model import Model, NamedModel
from magic_carpet.models.model_containers import ModelContainer, ModelList, NamedModelDict 

class BaseRouter(ABC):
    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, *args, **kwargs):
        raise NotImplementedError

class Router(Model, BaseRouter):
    def __init__(self, models, container_type: type = ModelList, **kwargs):
        if not isinstance(models, ModelContainer):
            models = container_type(models=models, **kwargs)
        self.models = models

    def has_model(self, model: Union[Model, Callable]):
        return self.models.has_item(model)
    
    def add_model(self, model: Union[Model, Callable]):
        return self.models.add_item(model)

    def run(self, *args, return_metadata: bool = False, metadata_only: bool = False, **kwargs):
        selection = self.route(*args, **kwargs)
        metadata = None
        if isinstance(selection, Tuple):
            selection, metadata = selection
                
        if metadata_only:
            return metadata
        
        if not self.has_model(selection):
            raise ValueError(f"Selection {selection} not in models.")
        
        output = self.execute(selection, **metadata.get("exec_params", {}))
        if return_metadata:
            return output, metadata
        
        return output

    def execute(self, selection, **kwargs):
        return selection(**kwargs)
    
    def route(self, *args, **kwargs):
        raise NotImplementedError

class NamedRouter(NamedModel, Router):
    def __init__(self, *args, name: str = None, description: str = None, **kwargs):
        Router.__init__(self, *args, container_type=NamedModelDict, **kwargs)
        NamedModel.__init__(self, name=name, description=description)

    def name_default(self):
        return f"{self.__class__.__name__}([{', '.join([str(key) for key in iter(self.models)])}])"

    def description_default(self):
        return f"Router for {len(self.models)} models listed below\n[\n" \
                            + ",\n".join(["\t" + "\n\t".join(f"({i}) {name}: {self.models[name].description}".split("\n")) for i, name in enumerate(self.models)]) \
                            + "\n]"



