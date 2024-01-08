from typing import Callable
import pandas as pd
from openai import OpenAI
from magic_carpet.routers.router import NamedRouter
import faiss
import numpy as np
import os


def openai_embedder(df, model="text-embedding-ada-002", api_key=os.getenv("OPENAI_API_KEY"), **kwargs):
    client = OpenAI(
        # This is the default and can be omitted
        api_key=api_key,
    )
    # convert df to list of strings assuming that df is just a series of Strings 
    return [d.embedding for d in client.embeddings.create(input = df.values.tolist(), model=model).data]

class NNRouter(NamedRouter):
    def __init__(
            self, 
            data: pd.DataFrame, 
            input_col: str = "prompt", 
            model_cols: list[str] = None, 
            minimize: bool = True, 
            embedder: Callable = openai_embedder, 
            k: int = 10, 
            embedder_kwargs: dict = {}, 
            **kwargs
        ):
        super().__init__(**kwargs)
        self.data = data
        self.input_col = input_col
        self.model_cols = [col for col in data.columns if col != input_col] if model_cols is None else model_cols
        for col in self.model_cols:
            if col not in self:
                raise ValueError(f"Model {col} not found in router's models but is in the data.")
        self.minimize = minimize
        if minimize:
            self.data["best_model"] = self.data[model_cols].idxmin(axis=1)
        else:
            self.data["best_model"] = self.data[model_cols].idxmax(axis=1)

        self.embedder = embedder
        self.k = k
        vectors = np.array(self.embedder(self.data[input_col], **embedder_kwargs)).astype(np.float32)
        self.d = vectors.shape[1]
        self.index = faiss.IndexFlatIP(self.d)
        self.index.add(vectors)

    def route(self, input: str, **kwargs):
        input_embedding = np.array(self.embedder(pd.Series(input), **kwargs)).astype(np.float32)
        _, indices = self.index.search(input_embedding, self.k)
        nn_df = self.data.iloc[indices[0]]
        return self[nn_df.best_model.mode()[0]], {"nn_idxs": indices[0], "model_counts": nn_df.best_model.value_counts().to_dict()}



def test():
    names = ["TrueModel", "FalseModel"]
    model_fns = [lambda x: 'A', lambda x: 'B']
    prompts = [
            "If John has one apple and Sarah has three apples, then Sarah has fewer apples than John?\nA: True\nB: False", 
            "Earth has exactly one moon.\nA: True\nB: False", 
            "Jupiter is the 5th farthest planet from the sun.\nA: True\nB: False",
            "Jimmy gets one apple from his friend Sally and three oranges from his friend John. Assuming Jimmy had no fruit to start, he now has exactly 5 fruits.\nA: True\nB: False"
            ]
    true_rankings = [1, 0, 0, 1]
    false_rankings = [0, 1, 1, 0]
    assert len(prompts) == len(true_rankings) == len(false_rankings)
    # if os.path.exists("tmp.csv"):
    #     os.remove("tmp.csv")
    data=pd.DataFrame({
        "prompt": prompts, 
        "TrueModel": true_rankings, 
        "FalseModel": false_rankings,
    })

    router = NNRouter([{"name": name, "func": model_fn} for name, model_fn in zip(names, model_fns)], data=data, k=3)
    
    questions = [
        "If John has four apples and Sarah has three apples, then Sarah has more apples than John?\nA: True\nB: False",
        "Mercury has fewer moons than Saturn.\nA: True\nB: False",
    ]
    for q in questions:
        print(f"Question: {q}\nAnswer: {router(q)}")
    # os.remove("tmp.csv")

if __name__ == "__main__":
    test()