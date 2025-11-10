# Vérification déploiement RAG sur Render

## 1. Logs Render - À vérifier

```
✅ "Base enrichie chargée: 20 restos, 1 items menu"
✅ "Génération des embeddings..."
✅ "Index FAISS créé avec 33 documents"
✅ "Cache embeddings sauvegardé"
```

Si erreur :
- ❌ "No module named 'faiss'" → requirements.txt pas pris en compte
- ❌ "OpenAI API key not found" → Vérifier variables d'environnement Render
- ❌ Memory error → Réduire batch_size dans rag_engine.py

## 2. Test chatbot production

### Test 1 : Recherche sémantique basique
```
Question : "dans quelles villes êtes-vous ?"
Attendu : Liste des 20 restaurants
```

### Test 2 : Synonymes (preuve RAG fonctionne)
```
Question : "restaurant proche de Paris"
Attendu : Paris 11, Nanterre, Pierrefitte, Montreuil, etc.
```

### Test 3 : Questions complexes
```
Question : "Je cherche un resto accessible en transport"
Attendu : Utilise infos des pages scrapées sur accès
```

## 3. Performance

- Temps réponse : <1s attendu
- Latence RAG : ~100ms (embedding) + ~5ms (FAISS)
- Total avec GPT : ~600-800ms

## 4. Cache embeddings

Vérifier que le fichier `embeddings_cache.pkl` est créé :
- Localisation : Racine du projet sur Render
- Taille : ~500KB-1MB
- Régénération : Seulement si JSON change

## 5. Commandes debug Render (si problème)

```bash
# Dans Shell Render
python -c "import faiss; print('FAISS OK')"
python -c "from rag_engine import RAGEngine; print('RAG OK')"
python -c "from knowledge_base_enriched import EnrichedKnowledgeBase; kb=EnrichedKnowledgeBase(); print(f'KB: {len(kb.restaurants)} restos')"
```
