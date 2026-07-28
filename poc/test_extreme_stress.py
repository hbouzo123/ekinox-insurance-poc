import urllib.request
import urllib.parse
import json

base_url = "http://127.0.0.1:8000/api/sales/chat"
prospect_id = "test-extreme-stress"

edge_cases = [
    ("1. Hésitation & Paiement Mensuel", "Finalement je ne veux plus l'Auto Platinum, je préfère l'Auto Zen. Est-ce que je peux payer par mois en 4 fois ?"),
    ("2. Assistance Panne Autoroute", "J'ai une panne de batterie sur l'autoroute du Nord près de Yamoussoukro, est-ce que votre assistance intervient gratuitement ?"),
    ("3. Déménagement Multi-Pays", "Au fait je déménage à Casablanca au Maroc le mois prochain, est-ce que mon contrat Sanlam reste valable chez Sanlam Maroc ?"),
    ("4. Modification de RDV", "En fait à 17h je ne suis plus disponible, est-ce qu'on peut reporter le rendez-vous à demain 10h en agence ?"),
    ("5. Rachat de Franchise Bris de Glace", "Pour le bris de glace, est-ce qu'il y a une franchise à ma charge si je vais chez votre garage agréé ?")
]

print("=== DEBUT DU STRESS-TEST CLIENT EXTREME ET EDGE CASES ===\n")

for label, prompt in edge_cases:
    data = urllib.parse.urlencode({'prospect_id': prospect_id, 'message': prompt, 'channel': 'WhatsApp'}).encode('utf-8')
    try:
        resp = urllib.request.urlopen(urllib.request.Request(base_url, data=data))
        res = json.loads(resp.read().decode('utf-8'))
        reply = res['reply']
        clean_reply = reply.encode('ascii', errors='backslashreplace').decode('ascii')
        print(f"CLIENT [{label}] : {prompt}")
        print(f"IA REPLY :\n{clean_reply}\n")
    except Exception as e:
        print(f"EXCEPTION sur {label} : {e}")
    print("=" * 65)
