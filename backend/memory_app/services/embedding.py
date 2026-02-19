import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")


def get_embedding(text):
    return model.encode(text).tolist()


def cosine_similarity(vec1, vec2):
    v1 = np.array(vec1)
    v2 = np.array(vec2)
    # return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
    
    v1 = v1 / np.linalg.norm(v1)
    v2 = v2 / np.linalg.norm(v2)

    return np.dot(v1, v2)