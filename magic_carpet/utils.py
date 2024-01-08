from collections import defaultdict
from typing import Callable, Tuple, Union
import numpy as np

from magic_carpet.evaluators.eval_containers import KeyedEvalContainer, EvalList
from magic_carpet.evaluators.evaluator import Evaluator
from magic_carpet.models.model import Model
from magic_carpet.models.model_containers import KeyedModelContainer, ModelList

def generate(requests: list[dict], model_container: KeyedModelContainer, eval_container: KeyedEvalContainer, batch_generation: bool = False):
    for req in requests:
        if not isinstance(req, dict):
            raise TypeError(f"Request {req} is not a dict.")
        
        if not "models" in req:
            raise ValueError(f"Request {req} does not contain a model.")
        for model_id in req["models"]:
            if not (model_id in model_container):
                raise ValueError(f"Request {req} contains a model {model_id} not found in model_container.")
        
        if not "inputs" in req:
            raise ValueError(f"Request {req} does not contain inputs.")
        if not isinstance(req["inputs"], list):
            raise TypeError(f"Request {req} must have a list of inputs.")
        if len(req["inputs"]) > 0 and (not isinstance(req["inputs"][0], str)):
            raise TypeError(f"Request {req} must have a list of strings as inputs.")
        
        if not "evaluators" in req:
            req["evaluators"] = []
        for eval_id in req["evaluators"]:
            if not (eval_id in eval_container):
                raise ValueError(f"Request {req} contains an evaluator {eval_id} not found in eval_container.")

    generations = defaultdict(list)
    for req in requests:
        inputs = req["inputs"]
        if batch_generation:
            responses = model_container(inputs, keys=req["models"])
        else:
            responses = defaultdict(list)
            for input in inputs:
                model_responses = model_container(input, keys=req["models"])
                for model_id in model_responses:
                    responses[model_id].append(model_responses[model_id])
                    
        responses_per_input = defaultdict(dict)
        for model_id, responses in responses.items():
            for input, response in zip(inputs, responses):
                responses_per_input[input][model_id] = response
        
        for input, responses in responses_per_input.items():
            for model_id in responses:
                response = responses[model_id]
                scores = [{"name": str(eval_id), "score": score} for eval_id, score in eval_container(input, response, keys=req["evaluators"]).items()]
                generations[input].append({
                    "model": str(model_id),
                    "response": response,
                    "scores": scores
                })

    return [{"input": k, "generations": v} for k, v in generations.items()]

def make_request(inputs: list[str], models: list[Union[Model, Callable]], evaluators: list[Union[Evaluator, Callable]] = [], model_container: KeyedModelContainer = None, eval_container: KeyedEvalContainer = None):
    if model_container is None:
        model_container = ModelList(models)
    if eval_container is None:
        eval_container = EvalList(evaluators)

    for model in models:
        if not model_container.has(model):
            model_container.add(model)
    for evaluator in evaluators:
        if not eval_container.has(evaluator):
            eval_container.add(evaluator)

    request = {
        "models": [model_container.get_key(model) for model in models],
        "inputs": inputs,
        "evaluators": [eval_container.get_key(evaluator) for evaluator in evaluators]
    }

    return request, model_container, eval_container

def make_requests(request_tuples: list[Tuple]):
    model_container = ModelList()
    eval_container = EvalList()
    requests = []
    for req_tuple in request_tuples:
        request, model_container, eval_container = make_request(*req_tuple, model_container=model_container, eval_container=eval_container)
        requests.append(request)
    return requests, model_container, eval_container


