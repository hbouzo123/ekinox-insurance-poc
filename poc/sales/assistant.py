from core import database, nlp, orass_client
import re

FRENCH_STOP_WORDS = {
    "avec", "et", "en", "de", "du", "des", "le", "la", "les", "un", "une",
    "pour", "sur", "dans", "par", "pas", "oui", "non", "ici", "bien", "toujours",
    "voiture", "auto", "devis", "tarif", "prix", "bonjour", "salut", "quand", "quel",
    "quelle", "quelques", "chose", "merci", "voilà", "voila", "c'est", "fait", "est",
    "suis", "sommes", "êtes", "sont", "nous", "vous", "ils", "elles", "mon", "ma", "mes",
    "ton", "ta", "tes", "son", "sa", "ses", "notre", "votre", "leur", "ce", "cette", "ces",
    "famille", "est-ce", "que", "tu", "peux", "arrives", "me", "comprendre", "arabe", "culture",
    "document", "fichier", "carte", "grise", "pdf", "prospect", "inconnu", "platinium", "platinum", "tiers", "zen"
}

INVALID_NAMES = {
    "document", "fichier", "carte", "grise", "pdf", "prospect", "inconnu", "bonjour", "salut",
    "oui", "non", "merci", "platinium", "platinum", "tiers", "zen", "formule", "auto", "devis", "tarif",
    "cotonou", "parakou", "calavi", "porto-novo", "natitingou", "bohicon", "djougou"
}

BENIN_CITIES = ["cotonou", "parakou", "calavi", "porto-novo", "natitingou", "bohicon", "djougou", "kandi", "lokossa", "ouidah"]

def handle_sales_conversation(prospect_id: str, message_text: str, channel: str = "WhatsApp") -> dict:
    country_code = database.ACTIVE_COUNTRY
    cfg = database.COUNTRY_CONFIGS[country_code]
    
    if prospect_id not in database.PROSPECTS:
        database.PROSPECTS[prospect_id] = {
            "id": prospect_id,
            "country": country_code,
            "name": "Prospect Inconnu",
            "phone": "",
            "city": "Cotonou",
            "channel": channel,
            "vehicle": "",
            "need": "",
            "intention": "Froid ❄️",
            "risk_level": "STANDARD",
            "document_uploaded": False,
            "document_name": "",
            "appointment": "",
            "orass_policy_num": "",
            "conversation": [],
            "summary": f"Nouveau prospect {cfg['name']} en cours de qualification.",
            "next_action": "Accueil et qualification bienveillante.",
            "created_at": "À l'instant"
        }
        
    prospect = database.PROSPECTS[prospect_id]
    prospect["channel"] = channel
    
    prospect["conversation"].append({"sender": "user", "text": message_text})
    msg_lower = message_text.lower()
    
    # 1. City / Zone Extraction
    for city in BENIN_CITIES:
        if city in msg_lower:
            prospect["city"] = city.title()
            break

    # 2. Dynamic Name Extraction
    name_found = extract_dynamic_name(message_text)
    if name_found and prospect["name"] == "Prospect Inconnu" and name_found.lower() not in INVALID_NAMES:
        prospect["name"] = name_found
        
    phone_found = re_search_phone(message_text)
    if phone_found:
        prospect["phone"] = phone_found
        
    # 3. Vehicle Extraction
    if not prospect.get("vehicle") or any(w in prospect.get("vehicle", "").lower() for w in ["informations", "toujours", "demande"]):
        vehicle_match = re.search(r'\b(toyota\s+\w+|peugeot\s+\w+|clio\s*\d*|bmw\s*\d*|mercedes\s*\w*|dacia\s*\w*|rav4|hyundai\s*\w*|nissan\s*\w*)\b', msg_lower)
        if vehicle_match:
            prospect["vehicle"] = vehicle_match.group(0).title()
        elif prospect.get("document_uploaded"):
            prospect["vehicle"] = "Toyota Corolla (RB-1234-AB)" if country_code == "BJ" else "Mercedes Série Spéciale"
            
    # 4. Ordinal Formula Queries
    if any(k in msg_lower for k in ["3e", "3ème", "3eme", "troisième", "troisieme", "la 3", "formule 3"]):
        prospect["need"] = cfg["products"][-1]["name"]
    elif any(k in msg_lower for k in ["2e", "2ème", "2eme", "deuxième", "deuxieme", "la 2", "formule 2"]):
        prospect["need"] = cfg["products"][1]["name"]
    elif any(k in msg_lower for k in ["1ere", "1ère", "première", "premiere", "la 1", "formule 1"]):
        prospect["need"] = cfg["products"][0]["name"]

    # 5. Underwriting Risk Calculation
    sinistres = 2 if "2 sinistres" in msg_lower or "deux sinistres" in msg_lower else (1 if "1 sinistre" in msg_lower or "un sinistre" in msg_lower else 0)
    risk_data = orass_client.orass_engine.calculate_risk_score(sinistres_2ans=sinistres, city=prospect.get("city", "Cotonou"))
    prospect["risk_level"] = risk_data["level"]

    # 6. Trigger Human Advisor Validation
    if country_code == "BJ" and any(k in msg_lower for k in ["souscrire", "émettre", "emettre", "valider la police", "confirmer la souscription"]):
        if not prospect.get("orass_policy_num"):
            v_name = prospect.get("vehicle") or "Toyota Corolla"
            v_parts = v_name.split()
            marque = v_parts[0] if v_parts else "Toyota"
            modele = " ".join(v_parts[1:]) if len(v_parts) > 1 else "Corolla"
            
            p_name = prospect.get("name") if prospect.get("name") not in INVALID_NAMES else "Koffi"
            p_parts = p_name.split()
            nom_assure = p_parts[0] if p_parts else "Prospect"
            prenom_assure = p_parts[-1] if len(p_parts) > 1 else "Dossou"
            
            orass_deal = orass_client.orass_engine.validate_new_deal_auto(
                assure_nom=nom_assure,
                assure_prenom=prenom_assure,
                marque=marque,
                modele=modele,
                immatriculation="RB-1234-AB"
            )
            prospect["orass_policy_num"] = orass_deal.get("numepoli", "POL-AUTO-BENIN-894102")
            prospect["intention"] = "Chaud 🔥"

    if not prospect["need"]:
        for prod in cfg["products"]:
            if any(w in msg_lower for w in prod["name"].lower().split()):
                prospect["need"] = prod["name"]
                break
            
    if not prospect["need"]:
        if "tous risques" in msg_lower or "neuf" in msg_lower or "neuve" in msg_lower or "platinum" in msg_lower:
            prospect["need"] = cfg["products"][-1]["name"]
        elif "tiers" in msg_lower or "occasion" in msg_lower:
            prospect["need"] = cfg["products"][0]["name"]

    if prospect.get("orass_policy_num") or prospect.get("document_uploaded") or prospect.get("appointment") or any(k in msg_lower for k in ["devis", "tarif", "prix", "combien", "simulation", "souscrire"]):
        prospect["intention"] = "Chaud 🔥"
    elif prospect.get("vehicle") or prospect.get("need"):
        prospect["intention"] = "Chaud 🔥"
    elif prospect.get("name") and prospect.get("name").lower() not in INVALID_NAMES:
        prospect["intention"] = "Tiède ⏳"
    else:
        prospect["intention"] = "Froid ❄️"
            
    history_tuples = prospect["conversation"][:-1]
    assistant_reply = nlp.generate_llm_response(history_tuples, message_text, country_code=country_code, prospect_data=prospect)
    
    prospect["conversation"].append({"sender": "assistant", "text": assistant_reply})
    update_lead_intelligence(prospect, cfg)
    
    return {
        "reply": assistant_reply,
        "prospect_state": prospect
    }

def extract_dynamic_name(text: str) -> str:
    text_clean = text.strip()
    patterns = [
        r"(?:je m'appelle|moi c'est|mon nom est|mon prénom est|je suis|c'est)\s+([a-zA-Z]{2,20}(?:\s+[a-zA-Z]{2,20})?)",
        r"\b([A-Z][a-z]{2,15}(?:\s+[A-Z][a-z]{2,15})?)\b"
    ]
    for pattern in patterns:
        match = re.search(pattern, text_clean)
        if match:
            candidate = match.group(1).strip().title()
            candidate_words = candidate.lower().split()
            if not any(w in FRENCH_STOP_WORDS for w in candidate_words) and candidate.lower() not in INVALID_NAMES and len(candidate) >= 3:
                return candidate
    words = [w for w in re.findall(r'\b[a-zA-Z]{3,20}\b', text_clean) if w.lower() not in FRENCH_STOP_WORDS and w.lower() not in INVALID_NAMES]
    if len(words) == 1:
        return words[0].title()
    return ""

def re_search_phone(text: str) -> str:
    match = re.search(r'(\+?\d[\d\s-]{6,14}\d)', text)
    if match:
        return match.group(1).strip()
    return ""

def update_lead_intelligence(prospect: dict, cfg: dict):
    summary_parts = [f"Entity: {cfg['entity']} ({cfg['name']})."]
    p_name = prospect.get("name", "")
    if p_name and p_name.lower() not in INVALID_NAMES:
        summary_parts.append(f"Prospect: {p_name}.")
    if prospect.get("city"):
        summary_parts.append(f"Ville: {prospect['city']}.")
    if prospect["vehicle"]:
        summary_parts.append(f"Véhicule: {prospect['vehicle']}.")
    if prospect["need"]:
        summary_parts.append(f"Formule: {prospect['need']}.")
    if prospect.get("risk_level"):
        summary_parts.append(f"Risque: {prospect['risk_level']}.")
    if prospect.get("orass_policy_num"):
        summary_parts.append(f"Police Pré-validée: {prospect['orass_policy_num']}.")
        
    prospect["summary"] = " ".join(summary_parts)
    
    if prospect.get("risk_level") == "ELEVE":
        prospect["next_action"] = "Inviter le prospect en agence (Cotonou / Parakou) pour étude de souscription."
    elif prospect.get("orass_policy_num"):
        prospect["next_action"] = "Devis pré-validé. Prise de contact par un conseiller commercial sous 15 min."
    elif prospect["document_uploaded"] or prospect["intention"] == "Chaud 🔥":
        prospect["next_action"] = "Devis pré-validé. Proposer la validation par un conseiller."
    else:
        prospect["next_action"] = f"Qualification de la ville et du véhicule ({cfg['name']})."
