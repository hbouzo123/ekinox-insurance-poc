import urllib.request
import urllib.parse
import json

base_url = "http://127.0.0.1:8000/api/sales/chat"
prospect_id = "test-dialogue-quality"

prompts = [
    ("1. Achat voiture", "Je vais acheter une voiture et je veux savoir quels sont les offres."),
    ("2. Demande de reformulation", "Je n'ai pas compris ce que tu peux reformuler ça tout ça."),
    ("3. Nouvelle voiture semaine prochaine", "Ça y est au fait, je vais acheter une nouvelle voiture qui va sortir la semaine prochaine, est-ce que tu peux me dire quelle formule me convient ?"),
    ("4. Comparaison des 3 offres", "Quelle est la différence entre les 3 offres ?")
]

print("=== TEST DE QUALITE ET FLUIDITE CONVERSATIONNELLE (4 SCENARIOS) ===\n")

for label, p in prompts:
    data = urllib.parse.urlencode({'prospect_id': prospect_id, 'message': p, 'channel': 'WhatsApp'}).encode('utf-8')
    resp = urllib.request.urlopen(urllib.request.Request(base_url, data=data))
    res = json.loads(resp.read().decode('utf-8'))
    reply = res['reply']
    print(f"USER ({label}) : {p}")
    clean_reply = reply.encode('ascii', errors='backslashreplace').decode('ascii')
    print(f"IA REPLY :\n{clean_reply}\n")
    print("-" * 60)
