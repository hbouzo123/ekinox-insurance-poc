import sys
from core.nlp import generate_llm_response

history = []

prompts = [
    ("MA", "Bonjour, je voudrais en savoir plus sur les 3 formules d'assurance auto de SanlamAllianz."),
    ("MA", "Quelle est la différence entre Assur'Auto Pass et Assur'Auto Intégrale ?"),
    ("MA", "Quels sont vos garages agréés à Casablanca et quelles sont vos garanties d'assistance ?")
]

print("=== TEST CONVERSATION NATURELLE 100% PURE IA (DEEPSEEK-V4-FLASH) ===\n")

for country, msg in prompts:
    print(f"USER ({country}): {msg}")
    reply = generate_llm_response(history, msg, country_code=country)
    history.append({"sender": "user", "text": msg})
    history.append({"sender": "assistant", "text": reply})
    
    clean_reply = reply.encode('ascii', errors='backslashreplace').decode('ascii')
    print(f"IA CONSEILLER: {clean_reply}\n" + "-"*60 + "\n")
