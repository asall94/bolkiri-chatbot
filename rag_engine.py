"""
Moteur RAG (Retrieval Augmented Generation) avec FAISS pour Bolkiri
Recherche sémantique vectorielle sur la base de connaissances
"""

import os
import json
import pickle
import hashlib
from typing import List, Dict, Tuple
import numpy as np
import faiss
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


class RAGEngine:
    """Moteur de recherche sémantique avec embeddings et FAISS"""
    
    def __init__(self, knowledge_file: str = "bolkiri_knowledge_industrial_2025.json", force_rebuild: bool = False):
        self.knowledge_file = knowledge_file
        self.embedding_dim = 1536  # Dimension OpenAI embeddings text-embedding-ada-002
        self.cache_file = "embeddings_cache.pkl"
        
        # Supprimer le cache si force_rebuild
        if force_rebuild and os.path.exists(self.cache_file):
            os.remove(self.cache_file)
            print("Cache embeddings supprimé (force_rebuild=True)")
        
        # Chargement des données
        self.data = self._load_knowledge()
        self.documents = self._prepare_documents()
        
        # Index FAISS
        self.index = None
        self.embeddings = None
        
        # Initialiser l'index
        self._build_or_load_index()
        
        print(f"RAG Engine ready: {len(self.documents)} documents indexes")
    
    def _load_knowledge(self) -> Dict:
        """Charge la base de connaissances JSON"""
        with open(self.knowledge_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _prepare_documents(self) -> List[Dict]:
        """Prépare tous les documents pour l'indexation"""
        documents = []
        
        # 1. Documents depuis les pages scrapées
        pages_categorie = self.data.get('pages_par_categorie', {})
        for category, pages in pages_categorie.items():
            for page in pages:
                if page.get('content'):
                    documents.append({
                        'id': f"page_{len(documents)}",
                        'type': 'page',
                        'category': category,
                        'title': page.get('title', ''),
                        'url': page.get('url', ''),
                        'text': page.get('content', ''),
                        'metadata': {
                            'category': category,
                            'url': page.get('url', '')
                        }
                    })
        
        # 2. Documents depuis les restaurants
        restaurants = self.data.get('restaurants', [])
        for resto in restaurants:
            # Extraire la ville du nom
            name = resto.get('name', '')
            ville = ''
            if name:
                parts = name.split()
                if len(parts) > 1:
                    ville = ' '.join(parts[1:]).replace('Street Food Viêt', '').strip()
            
            # Créer un texte riche pour chaque restaurant
            text_parts = [
                f"Restaurant {name}",
                f"Situé à {resto.get('adresse', '')}",
                f"Ville: {ville}" if ville else "",
                f"Téléphone: {resto.get('telephone', '')}",
                f"Email: {resto.get('email', '')}",
            ]
            
            # Ajouter horaires si disponibles
            horaires = resto.get('horaires', {})
            if horaires:
                text_parts.append("Horaires d'ouverture:")
                for jour, heures in horaires.items():
                    text_parts.append(f"{jour}: {heures}")
            
            # Ajouter services
            services = resto.get('services', [])
            if services:
                text_parts.append(f"Services: {', '.join(services)}")
            
            text = '\n'.join([p for p in text_parts if p])
            
            documents.append({
                'id': f"resto_{resto.get('name', len(documents))}",
                'type': 'restaurant',
                'category': 'restaurant',
                'title': name,
                'ville': ville,
                'text': text,
                'metadata': {
                    'adresse': resto.get('adresse', ''),
                    'telephone': resto.get('telephone', ''),
                    'email': resto.get('email', ''),
                    'ville': ville
                }
            })
        
        # 3. Informations générales
        infos_gen = self.data.get('informations_generales', {})
        if infos_gen:
            text_gen = f"Informations générales Bolkiri:\n{json.dumps(infos_gen, indent=2, ensure_ascii=False)}"
            documents.append({
                'id': 'info_generale',
                'type': 'info_generale',
                'category': 'general',
                'title': 'Informations générales',
                'text': text_gen,
                'metadata': infos_gen
            })
        
        return documents
    
    def _get_embedding(self, text: str) -> np.ndarray:
        """Génère un embedding OpenAI pour un texte"""
        response = client.embeddings.create(
            input=text,
            model="text-embedding-ada-002"
        )
        return np.array(response.data[0].embedding, dtype=np.float32)
    
    def _get_embeddings_batch(self, texts: List[str]) -> np.ndarray:
        """Génère des embeddings pour plusieurs textes en batch"""
        embeddings = []
        batch_size = 20  # OpenAI limite
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            print(f"  Batch {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1}...")
            response = client.embeddings.create(
                input=batch,
                model="text-embedding-ada-002"
            )
            batch_embeddings = [np.array(item.embedding, dtype=np.float32) 
                              for item in response.data]
            embeddings.extend(batch_embeddings)
        
        return np.array(embeddings)
    
    def _get_cache_key(self) -> str:
        """Génère une clé de cache basée sur le contenu JSON"""
        with open(self.knowledge_file, 'rb') as f:
            content = f.read()
        return hashlib.md5(content).hexdigest()
    
    def _build_or_load_index(self):
        """Construit l'index FAISS ou le charge depuis le cache"""
        cache_key = self._get_cache_key()
        
        # Essayer de charger depuis le cache
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'rb') as f:
                    cache_data = pickle.load(f)
                
                if cache_data.get('cache_key') == cache_key:
                    print("Chargement embeddings depuis cache...")
                    self.embeddings = cache_data['embeddings']
                    self.index = faiss.deserialize_index(cache_data['index'])
                    print(f"{len(self.documents)} embeddings charges depuis cache")
                    return
            except Exception as e:
                print(f"Erreur chargement cache: {e}")
        
        # Construire l'index depuis zéro
        print("Construction de l'index FAISS...")
        
        # Générer les embeddings
        texts = [doc['text'][:8000] for doc in self.documents]  # Limiter taille
        print(f"Génération de {len(texts)} embeddings...")
        self.embeddings = self._get_embeddings_batch(texts)
        
        # Créer l'index FAISS
        self.index = faiss.IndexFlatL2(self.embedding_dim)
        self.index.add(self.embeddings)
        
        # Sauvegarder dans le cache
        cache_data = {
            'cache_key': cache_key,
            'embeddings': self.embeddings,
            'index': faiss.serialize_index(self.index)
        }
        with open(self.cache_file, 'wb') as f:
            pickle.dump(cache_data, f)
        
        print(f"Index construit: {self.index.ntotal} vecteurs")
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Recherche sémantique dans la base de connaissances
        
        Args:
            query: Question de l'utilisateur
            top_k: Nombre de résultats à retourner
        
        Returns:
            Liste de documents pertinents avec scores
        """
        # Générer embedding de la query
        query_embedding = self._get_embedding(query)
        query_vector = np.array([query_embedding])
        
        # Rechercher dans FAISS
        distances, indices = self.index.search(query_vector, top_k)
        
        # Préparer les résultats
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx < len(self.documents):
                doc = self.documents[idx]
                
                # Score de similarité (inverse de la distance L2)
                # Distance L2 plus petite = plus similaire
                similarity_score = 1.0 / (1.0 + distance)
                
                results.append({
                    'type': doc['type'],
                    'category': doc['category'],
                    'title': doc['title'],
                    'content': doc['text'],
                    'metadata': doc.get('metadata', {}),
                    'score': float(similarity_score),
                    'distance': float(distance),
                    'data': doc
                })
        
        return results
    
    def get_context_for_llm(self, query: str, max_context_length: int = 4000) -> str:
        """
        Récupère le contexte optimal pour le LLM
        
        Args:
            query: Question de l'utilisateur
            max_context_length: Longueur maximale du contexte
        
        Returns:
            Contexte formaté pour le LLM
        """
        results = self.search(query, top_k=10)
        
        context_parts = []
        current_length = 0
        
        for result in results:
            # Formater le document
            doc_text = f"[{result['type'].upper()}] {result['title']}\n{result['content']}\n"
            doc_length = len(doc_text)
            
            if current_length + doc_length > max_context_length:
                # Tronquer si nécessaire
                remaining = max_context_length - current_length
                if remaining > 200:
                    context_parts.append(doc_text[:remaining] + "...")
                break
            
            context_parts.append(doc_text)
            current_length += doc_length
        
        if not context_parts:
            return "Aucune information trouvée dans la base de connaissances."
        
        return "\n---\n".join(context_parts)


# Pour test direct
if __name__ == "__main__":
    print("Test RAG Engine\n")
    
    rag = RAGEngine()
    
    # Tests
    test_queries = [
        "dans quelles villes etes vous localises ?",
        "restaurant à Paris",
        "horaires d'ouverture",
        "menu végétarien",
        "programme fidélité"
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print('='*60)
        
        results = rag.search(query, top_k=3)
        
        for i, result in enumerate(results, 1):
            print(f"\n{i}. [{result['type']}] {result['title']}")
            print(f"   Score: {result['score']:.3f} | Distance: {result['distance']:.3f}")
            print(f"   {result['content'][:200]}...")
