import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from sales import assistant, routes
from core import database

database.set_active_country("BJ")
pid = "transcript-test-v2-product"

print("=== TEST 1: Qualification Initiale par l'IA ===")
res1 = assistant.handle_sales_conversation(pid, "Bonjour je veux une assurance auto pour ma Toyota Corolla à Cotonou", "WhatsApp")
print("Réponse IA:\n", res1["reply"].encode('ascii', errors='backslashreplace').decode('ascii'))
print("-" * 50)

print("\n=== TEST 2: Prise en Main Directe par l'Agent Commercial (Human Take-Over) ===")
res2 = routes.agent_takeover(prospect_id=pid, agent_name="Koffi Conseiller SanlamAllianz", message="Bonjour ! Je prends la main sur votre dossier pour vous offrir un accompagnement VIP.")
print("Message transmis par l'Agent:\n", res2["reply"].encode('ascii', errors='backslashreplace').decode('ascii'))
print("Statut Take-over:", res2["prospect_state"].get("is_human_takeover"))
print("-" * 50)

print("\n=== TEST 3: Geste Commercial 1-Clic (Remise de 5%) ===")
res3 = routes.apply_commercial_discount(prospect_id=pid, discount_pct=5)
print("Nouveau Tarif Remisé TTC:", res3["new_price_ttc"])
print("Prochaine action prospect:", res3["prospect_state"]["next_action"].encode('ascii', errors='backslashreplace').decode('ascii'))
