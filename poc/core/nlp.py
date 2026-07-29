import os
import json
import urllib.request
import re
from core import config, database, orass_client, intent_router

KNOWLEDGE_DOCUMENTS_BY_COUNTRY = {
    "BJ": [
        {
            "id": "doc-bj-1",
            "title": "Code CIMA & Réglementation ARCA SanlamAllianz Bénin",
            "content": "Conformément au Code CIMA Bénin (Article 13), l'assurance Responsabilité Civile automobile est obligatoire. Formule Auto Platinum Tous Risques avec franchise Cotonou 45 000 FCFA. Paiement par MTN MoMo (*138#) et Moov Flooz (*155#).",
            "category": "garantie"
        }
    ]
}

def clean_natural_text(text: str) -> str:
    if not text:
        return ""
    cleaned = re.sub(r'[*_#]', '', text)
    cleaned = re.sub(r'\(Sandbox ORASS\)', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'Sandbox ORASS', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'ORASS', '', cleaned)
    cleaned = re.sub(r'\(([^)]+)\)\s*\(\1\)', r'(\1)', cleaned)
    cleaned = re.sub(r'[ \t]+', ' ', cleaned)
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned).strip()
    if cleaned and cleaned[-1] not in ".!?]😊🚘🛡️📊🗓️💳📝🏢":
        cleaned += "."
    return cleaned

def detect_language_mode(user_message: str) -> str:
    text = user_message.strip()
    if re.search(r'[\u0600-\u06FF]', text):
        return "ARABIC"
    text_lower = text.lower()
    derja_keywords = ["marhaba", "chneyya", "bahi", "labes", "aslema", "khouya", "shokran"]
    if any(k in text_lower for k in derja_keywords):
        return "DERJA"
    return "FRENCH"

def search_knowledge_hub(query: str, country_code: str = "BJ") -> str:
    docs = KNOWLEDGE_DOCUMENTS_BY_COUNTRY.get(country_code, KNOWLEDGE_DOCUMENTS_BY_COUNTRY["BJ"])
    query_clean = query.lower()
    keywords = re.findall(r'\b\w{4,}\b', query_clean)
    if not keywords:
        keywords = query_clean.split()
    best_doc = None
    max_matches = 0
    for doc in docs:
        doc_text = (doc["title"] + " " + doc["content"]).lower()
        matches = sum(1 for kw in keywords if kw in doc_text)
        if matches > max_matches:
            max_matches = matches
            best_doc = doc
    if best_doc and max_matches > 0:
        return f"Information officielle : {best_doc['content']}"
    return ""

def generate_llm_response(conversation_history: list, user_message: str, country_code: str = "BJ", prospect_data: dict = None) -> str:
    cfg = database.COUNTRY_CONFIGS.get(country_code, database.COUNTRY_CONFIGS["BJ"])
    lang_mode = detect_language_mode(user_message)
    
    intent_data = intent_router.IntentRouter.classify_intent(user_message, prospect_data)
    
    if intent_data["route"] == "JOURNEY":
        return clean_natural_text(execute_structured_journey(user_message, intent_data, cfg, prospect_data, lang_mode))

    prospect_info = ""
    if prospect_data:
        p_name = prospect_data.get("name", "")
        if p_name and p_name not in ["Prospect Inconnu", "Document", "Fichier", "Carte Grise", "Pdf", "Platinium", "Platinum"]:
            prospect_info += f"\n- Nom du prospect : {p_name}"
        if prospect_data.get("city"):
            prospect_info += f"\n- Ville/Zone : {prospect_data.get('city')}"
        if prospect_data.get("document_uploaded"):
            prospect_info += f"\n- Carte grise analysée pour : {prospect_data.get('vehicle', 'Toyota Corolla')}"
        elif prospect_data.get("vehicle"):
            prospect_info += f"\n- Véhicule : {prospect_data.get('vehicle')}"

    knowledge_context = search_knowledge_hub(user_message, country_code)

    system_prompt = (
        f"Tu es le Conseiller Commercial Virtuel {cfg['entity']} au {cfg['name']}.\n"
        f"Tu accueilles les prospects avec bienveillance, politesse et écoute active.\n"
        f"N'utilise AUCUN caractère markdown (** ou #).\n"
        f"Ne mentionne JAMAIS 'Sandbox' ni 'ORASS' ni 'quittance' dans tes réponses.\n"
        f"Ne force JAMAIS le prospect à payer immédiatement : explique que les devis sont pré-validés et transmis à un conseiller humain.\n"
        f"{prospect_info}\n"
        f"{knowledge_context}\n"
    )
    
    messages = [{"role": "system", "content": system_prompt}]
    for msg in conversation_history[-4:]:
        role = "assistant" if msg["sender"] == "assistant" else "user"
        messages.append({"role": role, "content": clean_natural_text(msg["text"])})
    messages.append({"role": "user", "content": user_message})
    
    if config.OLLAMA_API_KEY:
        try:
            url = config.OLLAMA_API_URL
            payload = {
                "model": config.DEFAULT_MODEL,
                "messages": messages,
                "stream": False,
                "options": { "num_predict": 250, "temperature": 0.3 }
            }
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(url, data=data, headers={
                "Authorization": f"Bearer {config.OLLAMA_API_KEY}",
                "Content-Type": "application/json"
            })
            resp = urllib.request.urlopen(req, timeout=1.8)
            result = json.loads(resp.read().decode('utf-8'))
            reply = result.get("message", {}).get("content", "").strip()
            if reply and len(reply) > 10:
                return clean_natural_text(reply)
        except Exception as e:
            print(f"[Render Speed Engine] Cloud LLM fast fallback activated ({e}).")
            
    return clean_natural_text(generate_instant_rag_response(user_message, cfg, prospect_data, lang_mode))

def execute_structured_journey(user_message: str, intent_data: dict, cfg: dict, prospect_data: dict = None, lang_mode: str = "FRENCH") -> str:
    msg = user_message.lower()
    intent = intent_data["intent"]
    country_code = cfg.get("code", "BJ")
    products = cfg["products"]
    p1, p2, p3 = products[0], products[1], products[2]
    
    has_uploaded_doc = prospect_data.get("document_uploaded", False) if prospect_data else False
    vehicle_known = bool(prospect_data.get("vehicle") and "informations" not in prospect_data.get("vehicle").lower()) if prospect_data else False
    vehicle_str = prospect_data.get("vehicle", "votre véhicule") if (prospect_data and vehicle_known) else "votre véhicule"
    city_name = prospect_data.get("city", "Cotonou") if prospect_data else "Cotonou"
    
    raw_name = prospect_data.get("name", "") if prospect_data else ""
    valid_name = raw_name if raw_name not in ["Prospect Inconnu", "Document", "Fichier", "Carte Grise", "Pdf", "Platinium", "Platinum"] else ""
    greeting_name = f" {valid_name}" if valid_name else ""

    # A. INITIAL WELCOME & MUTUAL PRESENTATION
    if intent == "WELCOME_PRESENTATION":
        return (
            f"Bonjour ! 👋 Je suis votre Conseiller Commercial Virtuel SanlamAllianz {cfg['name']}. "
            f"C'est un plaisir de vous accueillir !\n\n"
            f"Pour mieux personnaliser vos simulations, comment vous appelez-vous et dans quelle ville habitez-vous (ex: Cotonou, Parakou, Calavi) ?\n\n"
            f"[📊 Simulation Rapide]  [📄 Envoyer ma Carte Grise]"
        )

    # B. ASSUMPTIONS ADJUSTMENT
    if intent == "ADJUST_ASSUMPTIONS":
        return (
            f"Avec plaisir{greeting_name} ! ⚙️ Vous pouvez ajuster les hypothèses de calcul de votre devis :\n\n"
            f"1. Ville / Zone : {city_name} (Zone A par défaut ou Zone B -15% à l'intérieur).\n"
            f"2. Antécédents : 0 sinistre (Bonus 20% par défaut).\n"
            f"3. Assiette de Valeur : Basée sur la puissance fiscale du véhicule.\n\n"
            f"Quelle hypothèse souhaitez-vous modifier ?\n\n"
            f"[Changer de Ville (ex: Parakou)]  [Déclarer un Sinistre]  [Obtenir mon Devis]"
        )

    # C. HUMAN ADVISOR VALIDATION (NO HARD PRESSURE TO PAY)
    if intent == "HUMAN_ADVISOR_VALIDATION":
        orass_quote = orass_client.orass_engine.calculate_devis_auto(city=city_name)
        risk = orass_quote.get("risk", {})
        
        # UNDERWRITING RISK SCORING REDIRECTION
        if risk.get("requires_agency_visit"):
            return (
                f"Merci pour votre confiance{greeting_name} ! 🏢\n\n"
                f"Compte tenu de votre profil spécifique et de vos antécédents, nous vous invitons chaleureusement à vous rendre dans l'agence SanlamAllianz de votre choix à Cotonou (Haie Vive / Ganhi) ou Parakou pour une étude personnalisée sur-mesure par un souscripteur dédié.\n\n"
                f"Nos conseillers en agence se feront un plaisir d'adapter l'offre à vos besoins exacts !"
            )
            
        num_dev = orass_quote["numdevis"]
        return (
            f"Votre Devis Officiel Bénin (N° {num_dev}) pour votre {vehicle_str} a été pré-validé avec succès ! 📝\n\n"
            f"Un Conseiller Commercial SanlamAllianz va vérifier votre dossier et vous contacter d'ici quelques minutes pour valider la souscription.\n\n"
            f"Comment préférez-vous échanger avec notre conseiller ?\n\n"
            f"[Rappel Téléphonique Conseiller]  [Récapitulatif par WhatsApp]  [Payer via MTN MoMo]"
        )

    # D. PAYMENT JOURNEY
    if intent == "PAYMENT":
        return (
            f"Excellente initiative{greeting_name} ! Votre dossier est pré-validé par le système.\n"
            f"Dès validation finale par votre conseiller, vous pourrez utiliser votre mode de paiement sécurisé au Bénin :\n\n"
            f"• 📱 MTN Mobile Money Bénin (MoMo) : Syntaxe rapide *138#\n"
            f"• 📱 Moov Money Bénin (Flooz) : Syntaxe rapide *155#\n"
            f"• 🏢 Paiement en Agence SanlamAllianz Cotonou / Parakou\n\n"
            f"[Valider avec mon Conseiller]  [Payer via MTN MoMo]  [Payer via Moov Flooz]"
        )

    # E. DEVIS CALCULATION JOURNEY WITH FULL ASSUMPTIONS DISCLOSURE
    if intent == "DEVIS_CALCULATION":
        if intent_data.get("needs_slot"):
            return (
                f"Pour vous calculer votre Devis Officiel sur-mesure au {cfg['name']}{greeting_name}, "
                f"quel est le modèle de votre voiture (ex: Toyota Corolla) ? Vous pouvez aussi me partager une photo de votre Carte Grise.\n\n"
                f"[Envoyer ma Carte Grise]  [Préciser mon véhicule]"
            )
            
        orass_quote = orass_client.orass_engine.calculate_devis_auto(city=city_name)
        detail = orass_quote["detail"]
        assump = orass_quote["assumptions"]
        num_dev = orass_quote["numdevis"]
        
        return (
            f"Voici l'analyse de votre Devis Officiel Bénin (N° {num_dev}) pour la formule **{p3['name']}** ({vehicle_str}) :\n\n"
            f"📋 **Hypothèses Actuarielles Utilisées :**\n"
            f"• Assiette de Valeur (Neuf/Vénale) : {assump['valeurNeufOrVenale']}\n"
            f"• Zone Géographique : {assump['zoneGeo']}\n"
            f"• Historique Antécédents : {assump['bonusMalus']}\n"
            f"• Usage du Véhicule : {assump['usage']}\n\n"
            f"💰 **Décomposition du Tarif CIMA Bénin :**\n"
            f"• Prime RC Nette : {detail['primeRcNette']:,} FCFA\n".replace(",", " ") +
            f"• Garanties Annexes (Vol/Incendie/Bris/Tous Risques) : {detail['garantiesAnnexes']:,} FCFA\n".replace(",", " ") +
            f"• Taxe Assurance CIMA Bénin : {detail['taxeAssurance']:,} FCFA\n".replace(",", " ") +
            f"• Taxe FGA Bénin & Timbres : {detail['taxeFga'] + detail['timbres']:,} FCFA\n".replace(",", " ") +
            f"💰 **Montant Total Devis TTC : {detail['primeTtc']:,} FCFA**\n\n".replace(",", " ") +
            f"💡 *Votre devis est pré-validé. Un conseiller SanlamAllianz le révisera avec vous avant tout paiement.*\n\n"
            f"[Ajuster les Hypothèses]  [Valider avec un Conseiller]  [Payer via MTN MoMo]"
        )

    return generate_instant_rag_response(user_message, cfg, prospect_data, lang_mode)

def generate_instant_rag_response(user_message: str, cfg: dict, prospect_data: dict = None, lang_mode: str = "FRENCH") -> str:
    msg = user_message.lower()
    country_code = cfg.get("code", "BJ")
    products = cfg["products"]
    p1, p2, p3 = products[0], products[1], products[2]
    
    vehicle_known = bool(prospect_data.get("vehicle") and "informations" not in prospect_data.get("vehicle").lower()) if prospect_data else False
    vehicle_str = prospect_data.get("vehicle", "votre véhicule") if (prospect_data and vehicle_known) else "votre véhicule"
    
    raw_name = prospect_data.get("name", "") if prospect_data else ""
    valid_name = raw_name if raw_name not in ["Prospect Inconnu", "Document", "Fichier", "Carte Grise", "Pdf", "Platinium", "Platinum"] else ""
    greeting_name = f" {valid_name}" if valid_name else ""

    # GREETINGS
    if any(k in msg for k in ["bonjour", "salut", "comment vas-tu", "comment t'appelles", "qui es-tu"]):
        return (
            f"Bonjour ! 👋 Je suis votre Conseiller Commercial Virtuel {cfg['entity']} au {cfg['name']}.\n\n"
            f"Je suis là pour vous accompagner, répondre à vos questions et établir vos devis officiels sur-mesure.\n\n"
            f"Comment puis-je vous aider aujourd'hui ?\n\n"
            f"[📊 Faire une simulation]  [📄 Envoyer ma Carte Grise]"
        )

    return (
        f"Je suis votre Conseiller Commercial Virtuel {cfg['entity']} au {cfg['name']}. "
        f"Je reste à votre entière disposition pour répondre à vos questions sur {vehicle_str} ou ajuster votre Devis Officiel.\n\n"
        f"[{p2['name']}]  [{p3['name']}]  [Obtenir mon Devis Officiel]"
    )
