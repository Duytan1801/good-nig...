import numpy as np
import pickle
import os

class VectorStore:
    def __init__(self, store_path="vector_store.pkl"):
        self.store_path = store_path
        self.embeddings = []
        self.texts = []
        
    def add(self, text, embedding):
        self.texts.append(text)
        self.embeddings.append(embedding)
    
    def search(self, query_embedding, top_k=3):
        if not self.embeddings:
            return []
        
        query_vec = np.array(query_embedding)
        similarities = []
        
        for i, emb in enumerate(self.embeddings):
            doc_vec = np.array(emb)
            similarity = np.dot(query_vec, doc_vec) / (np.linalg.norm(query_vec) * np.linalg.norm(doc_vec))
            similarities.append((similarity, i))
        
        similarities.sort(reverse=True)
        return [(self.texts[i], sim) for sim, i in similarities[:top_k]]
    
    def search_with_surrounding(self, query_embedding, top_k=3, window=2):
        if not self.embeddings:
            return []
        
        query_vec = np.array(query_embedding)
        similarities = []
        
        for i, emb in enumerate(self.embeddings):
            doc_vec = np.array(emb)
            similarity = np.dot(query_vec, doc_vec) / (np.linalg.norm(query_vec) * np.linalg.norm(doc_vec))
            similarities.append((similarity, i))
        
        similarities.sort(reverse=True)
        
        results = []
        for sim, idx in similarities[:top_k]:
            # Get surrounding dialogues
            start = max(0, idx - window)
            end = min(len(self.texts), idx + window + 1)
            surrounding = self.texts[start:end]
            results.append((surrounding, sim, idx))
        
        return results
    
    def save(self):
        with open(self.store_path, 'wb') as f:
            pickle.dump({'texts': self.texts, 'embeddings': self.embeddings}, f)
    
    def load(self):
        if os.path.exists(self.store_path):
            with open(self.store_path, 'rb') as f:
                data = pickle.load(f)
                self.texts = data['texts']
                self.embeddings = data['embeddings']
            return True
        return False
