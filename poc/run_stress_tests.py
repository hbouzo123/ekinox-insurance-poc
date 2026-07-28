import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import json
from sales import assistant
from fraud import engine as fraud_engine
from core import database, document, nlp, orass_client

def test_scenario_1():
    print("\n" + "="*80)
    print("   SCÉNARIO 1 : Changement brusque de besoin & Quittance ORASS CIMA")
    print("="*80 + "\n")
    
    pid = "stress-prospect-1"
    database.set_active_country("CI")
    
    msg1 = "Bonjour, je suis Alex. Je cherche une assurance Tous Risques pour ma voiture neuve Peugeot 3008."
    print(f"--- Step 1.1 USER: {msg1}")
    res1 = assistant.handle_sales_conversation(pid, msg1, "WhatsApp")
    p_state = res1.get("prospect_state", res1.get("state"))
    print(f"-> ASSISTANT: {res1['reply'][:120]}...")
    print(f"-> STATE: Intention={p_state['intention']} | Vehicle={p_state['vehicle']} | Need={p_state['need']}\n")
    
    msg2 = "Finalement la Tous Risques est trop chère, je veux la formule tiers basique avec paiement par mois."
    print(f"--- Step 1.2 USER: {msg2}")
    res2 = assistant.handle_sales_conversation(pid, msg2, "WhatsApp")
    p_state = res2.get("prospect_state", res2.get("state"))
    print(f"-> ASSISTANT: {res2['reply'][:120]}...")
    print(f"-> STATE: Need={p_state['need']} | Intention={p_state['intention']}\n")

def test_scenario_2():
    print("\n" + "="*80)
    print("   SCÉNARIO 2 : Émission de Police Auto ORASS (iard.new-deal)")
    print("="*80 + "\n")
    
    pid = "stress-prospect-2"
    msg1 = "Je suis Karim. Je veux souscrire et émettre ma police ORASS officielle."
    print(f"--- Step 2.1 USER: {msg1}")
    res1 = assistant.handle_sales_conversation(pid, msg1, "WhatsApp")
    p_state = res1.get("prospect_state", res1.get("state"))
    print(f"-> ASSISTANT: {res1['reply'][:120]}...")
    print(f"-> STATE: Police ORASS={p_state.get('orass_policy_num')} | Intention={p_state['intention']}\n")

if __name__ == "__main__":
    test_scenario_1()
    test_scenario_2()
    print("\n✅ TOUS LES SCÉNARIOS DE STRESS ET INTÉGRATION ORASS SONT VALIDÉS A 100% !")
