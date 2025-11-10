"""Test de la knowledge base corrigée"""

from knowledge_base_enriched import EnrichedKnowledgeBase

print("Chargement de la knowledge base...")
kb = EnrichedKnowledgeBase()

print(f"\nRestaurants chargés: {len(kb.restaurants)}")
print(f"Documents chargés: {len(kb.documents)}")

# Test recherche villes
print("\n" + "=" * 60)
print("TEST: 'dans quelles villes etes vous localises ?'")
print("=" * 60)
results = kb.search("dans quelles villes etes vous localises")
print(f"\nRésultats trouvés: {len(results)}")
for i, result in enumerate(results[:5], 1):
    print(f"\n{i}. Score: {result['score']}")
    print(f"   Type: {result['type']}")
    print(f"   Contenu: {result['content'][:200]}...")

# Test recherche restaurant spécifique
print("\n" + "=" * 60)
print("TEST: 'restaurant à Paris'")
print("=" * 60)
results = kb.search("restaurant à Paris")
print(f"\nRésultats trouvés: {len(results)}")
for i, result in enumerate(results[:3], 1):
    print(f"\n{i}. Score: {result['score']}")
    print(f"   Contenu: {result['content'][:200]}...")

print("\n" + "=" * 60)
print("LISTE DES VILLES:")
print("=" * 60)
for resto in kb.restaurants[:10]:
    print(f"- {resto.get('name', 'N/A')}")
