from ai_agent import AIAgent
import os
from dotenv import load_dotenv
import signal
import sys

def timeout_handler(signum, frame):
    raise TimeoutError("Timeout")

load_dotenv()

agent = AIAgent(
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    website_url="https://bolkiri.fr"
)

print("Q1: Restaurant dans le 91")
resp1 = agent.chat("vous avez un resto dans le 91 ?")
print(resp1[:100])

print("\n\nQ2: Horaires (avec timeout 30s)")
try:
    # Timeout de 30 secondes
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(30)
    
    resp2 = agent.chat("top, quelle adresse ? quels horaires ?")
    signal.alarm(0)  # Annuler le timeout
    print(resp2)
except TimeoutError:
    print("TIMEOUT: La requête a pris plus de 30 secondes")
except Exception as e:
    print(f"ERREUR: {e}")
