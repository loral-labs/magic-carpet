import pandas as pd
from openai import OpenAI
from magic_carpet.routers.router import Router
import numpy as np
import os
from sklearn.decomposition import PCA



def openai_embedder(df, model="text-embedding-ada-002", api_key=os.getenv("OPENAI_API_KEY"), **kwargs):
    client = OpenAI(
        # This is the default and can be omitted
        api_key=api_key,
    )
    # convert df to list of strings assuming that df is just a series of Strings 
    return [d.embedding for d in client.embeddings.create(input = df.values.tolist(), model=model).data]

class ModelMapRouter(Router):
    def __init__(self, model_cols: list[str], embedder=openai_embedder, model_dim=384, **kwargs):
        super().__init__(**kwargs)
        self.train_df["best_model"] = self.train_df[model_cols].idxmin(axis=1)
        self.embedder = embedder
        self.model_dim = model_dim

        self.model_embeds = {}
        self.pcas = {}
        self.model_embed_info = {}
        self.create_model_maps()

    def model_projection(self, model, vectors):
        pca = self.pcas[model]
        coefs = pca.transform(vectors)
        return vectors - (coefs.reshape(*coefs.shape, 1) * pca.components_.reshape(1, *pca.components_.shape)).sum(axis=1)
    
    def projection_distance(self, model, vectors):
        model_embedding = self.model_embeds[model]
        return np.linalg.norm(model_embedding.reshape(1, *model_embedding.shape) - self.model_projection(model, vectors), axis=1)
    
    def normalized_projection_distance(self, model, vectors):
        assert (model in self.model_embed_info)
        return (self.projection_distance(model, vectors) - self.model_embed_info[model]["mean"]) / max(self.model_embed_info[model]["std"], 1e-10)

    def create_model_maps(self):
        assert ("best_model" in self.train_df.columns)
        for model, group in self.train_df.groupby("best_model"):
            group_embeds = np.array(self.embedder(group.prompt)).astype(np.float32)
            pca = PCA(n_components=group_embeds.shape[1] - self.model_dim)
            pca.fit(group_embeds)
            self.pcas[model] = pca
            self.model_embeds[model] = self.model_projection(model, group_embeds).mean(axis=0)
            group_proj_dists = self.projection_distance(model, group_embeds)
            self.model_embed_info[model] = {
                "mean": group_proj_dists.mean(),
                "std": group_proj_dists.std()
            }

    def route(self, input: str, **kwargs):
        input_embedding = np.array(self.embedder(pd.Series(input), **kwargs)).astype(np.float32)
        model_z_scores = {model: self.normalized_projection_distance(model, input_embedding) for model in self.model_embeds}
        return self[min(model_z_scores, key=model_z_scores.get)], {"model_scores": model_z_scores}



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

    router = ModelMapRouter([{"name": name, "func": model_fn} for name, model_fn in zip(names, model_fns)], data=data, model_dim=1535)
    
    questions = [
        "If John has four apples and Sarah has three apples, then Sarah has more apples than John?\nA: True\nB: False",
        "Mercury has fewer moons than Saturn.\nA: True\nB: False",
    ]
    for q in questions:
        print(f"Question: {q}\nAnswer: {router(q)}")
    # os.remove("tmp.csv")

if __name__ == "__main__":
    test()