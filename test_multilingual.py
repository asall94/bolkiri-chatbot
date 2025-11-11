"""Test multilingue du chatbot Bolkiri"""

from ai_agent import AIAgent
import os
from dotenv import load_dotenv

load_dotenv()

print("Initialisation agent...")
agent = AIAgent(os.getenv('OPENAI_API_KEY'), 'https://bolkiri.fr')

# Tests multilingues
tests = [
    ("FR", "Vous etes presents dans le 78 ?"),
    ("VI", "Ban co nha hang o Paris khong?"),  # Avez-vous un restaurant à Paris ?
    ("VI", "Gio mo cua la may gio?"),  # Quels sont les horaires ?
    ("EN", "Do you have a restaurant in Paris?")
]

print("\n" + "="*70)
print("TESTS MULTILINGUES")
print("="*70)

for lang, question in tests:
    print(f"\n[{lang}] Question: {question}")
    print("-" * 70)
    
    try:
        response = agent.chat(question)
        print(f"Reponse ({len(response)} chars):")
        print(response[:300])
        if len(response) > 300:
            print("...")
    except Exception as e:
        print(f"ERREUR: {e}")
    
    print()

print("\n" + "="*70)
print("Tests termines!")
print("="*70)
