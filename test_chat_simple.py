from ai_agent import AIAgent
import os
from dotenv import load_dotenv

load_dotenv()

agent = AIAgent(
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    website_url="https://bolkiri.fr"
)

print("=== Test 1: Restaurant dans le 91 ===")
resp1 = agent.chat("vous avez un resto dans le 91 ?")
print(resp1)

print("\n=== Test 2: Horaires ===")
try:
    resp2 = agent.chat("top, quelle adresse ? quels horaires ?")
    print(resp2)
except Exception as e:
    print(f"ERREUR: {e}")
    import traceback
    traceback.print_exc()

print("\n=== Test 3: Horaires direct ===")
try:
    resp3 = agent.chat("quels sont vos horaires à Corbeil ?")
    print(resp3)
except Exception as e:
    print(f"ERREUR: {e}")
    import traceback
    traceback.print_exc()
