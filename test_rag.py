"""Test RAG simplifié"""

from knowledge_base_enriched import EnrichedKnowledgeBase

print("Test KB avec RAG...\n")

kb = EnrichedKnowledgeBase()

# Test queries
tests = [
    "dans quelles villes etes vous localises ?",
    "restaurant proche de Paris",
    "menu vegetarien",
    "horaires ouverture"
]

for query in tests:
    print(f"\n{'='*60}")
    print(f"Q: {query}")
    print('='*60)
    
    results = kb.search(query, limit=3)
    print(f"Resultats: {len(results)}")
    
    for i, r in enumerate(results, 1):
        print(f"\n{i}. Type: {r['type']}")
        print(f"   Score: {r.get('score', 'N/A')}")
        # Eviter problemes encoding
        content = r.get('content', '')
        if len(content) > 150:
            content = content[:150]
        # Remplacer caracteres problematiques
        content = content.encode('ascii', errors='ignore').decode('ascii')
        print(f"   Contenu: {content}...")

print("\n\nTest termine!")
