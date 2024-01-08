from magic_carpet.routers.router import NamedRouter 

class CascadeRouter(NamedRouter):
    def __init__(self, model_tiers: list[list[str]], **kwargs):
        super().__init__(**kwargs)
        self.model_tiers = [[self[key] for key in tier] for tier in model_tiers]
    
    def route(self, input):
        return self.model_tiers