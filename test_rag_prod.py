"""Test du RAG en production sur Render"""

import requests
import json

# URL production Render
RENDER_URL = "https://bolkiri-chatbot.onrender.com/chat"

def test_question(question):
    """Teste une question sur le chatbot production"""
    print(f"\n{'='*60}")
    print(f"Question: {question}")
    print('='*60)
    
    try:
        response = requests.post(
            RENDER_URL,
            json={"message": question},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Réponse ({len(data.get('response', ''))} chars):")
            print(data.get('response', 'Pas de réponse')[:300])
        else:
            print(f"❌ Erreur HTTP {response.status_code}")
            print(response.text[:200])
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

# Tests RAG
print("🧪 TEST RAG EN PRODUCTION")
print("Attendre que Render ait fini de déployer...")

test_question("Dans quelles villes êtes-vous localisés ?")
test_question("Restaurant proche de Paris")
test_question("Horaires à Bondy")
test_question("Comment vous joindre ?")
