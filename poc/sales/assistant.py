from core import database, nlp
import re

def handle_sales_conversation(prospect_id: str, message_text: str, channel: str = "WhatsApp") -> dict:
    """Process prospect chat message, track acquisition channel, and invoke country-aware LLM."""
    
    country_code = database.ACTIVE_COUNTRY
    cfg = database.COUNTRY_CONFIGS[country_code]
    
    if prospect_id not in database.PROSPECTS:
        database.PROSPECTS[prospect_id] = {
            "id": prospect_id,
            "country": country_code,
            "name": "Prospect Inconnu",
            "phone": "",
            "channel": channel,
            "vehicle": "",
            "need": "",
            "intention": "Froid ❄️",
            "document_uploaded": False,
            "document_name": "",
            "appointment": "",
            "conversation": [],
            "summary": f"Nouveau prospect {cfg['name']} en cours de qualification.",
            "next_action": "Attente qualification.",
            "created_at": "À l'instant"
        }
        
    prospect = database.PROSPECTS[prospect_id]
    prospect["channel"] = channel
    
    prospect["conversation"].append({"sender": "user", "text": message_text})
    
    msg_lower = message_text.lower()
    
    # 1. Improved Name Detection (e.g., "c'est Karim", "je suis Karim", "moi c'est Karim")
    name_found = re_search_name(message_text)
    if name_found:
        prospect["name"] = name_found
        
    phone_found = re_search_phone(message_text)
    if phone_found:
        prospect["phone"] = phone_found
        
    # 2. Intelligent Vehicle Field Maintenance (do not dump conversational sentences into vehicle name)
    if not prospect.get("vehicle") or "informations" in prospect.get("vehicle", "").lower() or "toujours" in prospect.get("vehicle", "").lower():
        vehicle_match = re.search(r'\b(toyota\s+\w+|peugeot\s+\w+|clio\s*\d*|bmw\s*\d*|mercedes\s*\w*|dacia\s*\w*|rav4|hyundai\s*\w*|nissan\s*\w*)\b', msg_lower)
        if vehicle_match:
            prospect["vehicle"] = vehicle_match.group(0).title()
        elif prospect.get("document_uploaded"):
            prospect["vehicle"] = "Mercedes Série Spéciale (CI-5099-AB2)"
            
    # 3. Match country-specific product catalog
    for prod in cfg["products"]:
        if any(w in msg_lower for w in prod["name"].lower().split()):
            prospect["need"] = prod["name"]
            break
            
    if not prospect["need"]:
        if "tous risques" in msg_lower or "neuf" in msg_lower or "neuve" in msg_lower:
            prospect["need"] = cfg["products"][-1]["name"]
        elif "tiers" in msg_lower or "occasion" in msg_lower:
            prospect["need"] = cfg["products"][0]["name"]

    # 4. Accurate Commercial Maturity (Intention) Promotion Rules:
    if prospect.get("document_uploaded") or prospect.get("appointment") or any(k in msg_lower for k in ["devis", "tarif", "prix", "combien", "simulation", "souscrire", "trois devis", "3 devis"]):
        prospect["intention"] = "Chaud 🔥"
    elif prospect.get("vehicle") or prospect.get("need"):
        prospect["intention"] = "Chaud 🔥"
    elif prospect.get("name") and prospect.get("name") != "Prospect Inconnu":
        prospect["intention"] = "Tiède ⏳"
    else:
        prospect["intention"] = "Froid ❄️"
            
    # Generate live LLM response with country context and prospect state memory
    history_tuples = prospect["conversation"][:-1]
    assistant_reply = nlp.generate_llm_response(history_tuples, message_text, country_code=country_code, prospect_data=prospect)
    
    prospect["conversation"].append({"sender": "assistant", "text": assistant_reply})
    
    update_lead_intelligence(prospect, cfg)
    
    return {
        "reply": assistant_reply,
        "prospect_state": prospect
    }

def re_search_name(text: str) -> str:
    text_lower = text.lower().strip()
    patterns = [
        r"c'est\s+([a-zà-ÿ]+)",
        r"je suis\s+([a-zà-ÿ]+)",
        r"je m'appelle\s+([a-zà-ÿ]+(?:\s+[a-zà-ÿ]+)?)",
        r"moi c'est\s+([a-zà-ÿ]+(?:\s+[a-zà-ÿ]+)?)",
        r"mon nom est\s+([a-zà-ÿ]+(?:\s+[a-zà-ÿ]+)?)"
    ]
    for pattern in patterns:
        match = re.search(pattern, text_lower)
        if match:
            found = match.group(1).title()
            if found.lower() not in ["un", "une", "le", "la", "des", "du", "de", "bien", "toujours"]:
                return found
    return ""

def re_search_phone(text: str) -> str:
    match = re.search(r'(\+?\d[\d\s-]{6,14}\d)', text)
    if match:
        return match.group(1).strip()
    return ""

def update_lead_intelligence(prospect: dict, cfg: dict):
    summary_parts = [f"Entity: {cfg['entity']} ({cfg['name']})."]
    if prospect["name"] != "Prospect Inconnu":
        summary_parts.append(f"Prospect: {prospect['name']}.")
    if prospect["channel"]:
        summary_parts.append(f"Canal: {prospect['channel']}.")
    if prospect["vehicle"]:
        summary_parts.append(f"Véhicule: {prospect['vehicle']}.")
    if prospect["need"]:
        summary_parts.append(f"Formule: {prospect['need']}.")
    if prospect["document_uploaded"]:
        summary_parts.append(f"Pièces: Validées.")
    if prospect.get("appointment"):
        summary_parts.append(f"RDV: {prospect['appointment']}.")
        
    prospect["summary"] = " ".join(summary_parts)
    
    if prospect.get("appointment"):
        prospect["next_action"] = f"Rendez-vous téléphonique planifié le {prospect['appointment']}."
    elif prospect["document_uploaded"] or prospect["intention"] == "Chaud 🔥":
        prospect["next_action"] = "Proposer un créneau de rendez-vous pour souscription."
    else:
        prospect["next_action"] = f"Demander l'upload du certificat d'immatriculation ({cfg['name']})."
