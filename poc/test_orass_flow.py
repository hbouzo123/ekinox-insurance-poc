import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from sales import assistant

print("=== TEST 1: Simulation Devis ORASS ===")
res1 = assistant.handle_sales_conversation("prospect-orass-1", "Bonjour, je veux un devis pour ma Peugeot 208", "WhatsApp")
print("Intention:", res1["prospect_state"]["intention"])
print("Summary:", res1["prospect_state"]["summary"])
print("IA Reply:\n", res1["reply"].encode('ascii', errors='backslashreplace').decode('ascii'))
print("-" * 50)

print("\n=== TEST 2: Souscription & Émission Police ORASS ===")
res2 = assistant.handle_sales_conversation("prospect-orass-1", "Je veux souscrire la formule Tous Risques et émettre ma police", "WhatsApp")
print("Police ORASS:", res2["prospect_state"].get("orass_policy_num"))
print("Next Action:", res2["prospect_state"]["next_action"])
print("IA Reply:\n", res2["reply"].encode('ascii', errors='backslashreplace').decode('ascii'))
