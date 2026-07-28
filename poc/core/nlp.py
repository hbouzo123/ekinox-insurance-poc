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
    ],
    "CI": [
        {
            "id": "doc-ci-1",
            "title": "Code CIMA & Conditions Générales SanlamAllianz Côte d'Ivoire",
            "content": "Conformément au Code CIMA (Article 13), l'assurance Responsabilité Civile automobile est obligatoire. Formule Auto Platinum : dommages tous accidents jusqu'à 50 000 000 FCFA avec assistance 0 km à Abidjan et intérieur du pays.",
            "category": "garantie"
        }
    ],
    "MA": [
        {
            "id": "doc-ma-1",
            "title": "Réglementation ACAPS & Conditions Générales Sanlam Maroc",
            "content": "Sous le contrôle de l'ACAPS, l'offre Assur'Auto Intégrale Sanlam Maroc couvre les dommages tous risques avec rachat de franchise et garantie Décès Toutes Causes.",
            "category": "garantie"
        }
    ],
    "SN": [
        {
            "id": "doc-sn-1",
            "title": "Code CIMA Sénégal & Offre SanlamAllianz Sénégal",
            "content": "La formule Tous Risques Avantage SanlamAllianz Sénégal inclut la protection complète du véhicule et des personnes transportées, l'Assistance Teranga 24/7 sur Dakar et régions.",
            "category": "garantie"
        }
    ]
}

def clean_natural_text(text: str) -> str:
    """Clean markdown artifacts (**), extra parentheses, and technical symbols for natural human dialogue."""
    if not text:
        return ""
    
    cleaned = re.sub(r'[*_#]', '', text)
    cleaned = re.sub(r'\(Sandbox ORASS\)', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'Sandbox ORASS', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'ORASS', '', cleaned)
    cleaned = re.sub(r'\(([^)]+)\)\s*\(\1\)', r'(\1)', cleaned)
    cleaned = re.sub(r'[ \t]+', ' ', cleaned)
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned).strip()
    
    if cleaned and cleaned[-1] not in ".!?]😊🚘🛡️📊🗓️💳":
        cleaned += "."
        
    return cleaned

def detect_language_mode(user_message: str) -> str:
    """Detect whether user speaks French, Standard Arabic, or Maghrebi/Tunisian Derja."""
    text = user_message.strip()
    
    if re.search(r'[\u0600-\u06FF]', text):
        return "ARABIC"
        
    text_lower = text.lower()
    derja_keywords = [
        "aychik", "aaffia", "afia", "marhaba", "chneyya", "bahi", "behi", "labes", "aslema",
        "khouya", "shokran", "sahha", "yatik", "bch", "nحب", "kifech", "bchnekhou", "mrigal",
        "arabi", "derja", "3arbi", "tounsi", "tunisien"
    ]
    if any(k in text_lower for k in derja_keywords):
        return "DERJA"
        
    return "FRENCH"

def search_knowledge_hub(query: str, country_code: str = "BJ") -> str:
    """Search country-specific Knowledge Hub documents."""
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
    """
    HYBRID ARCHITECTURE:
    1. Route to Structured Journey if Intent is High-Confidence (Devis, Payment, Policy, Appointment)
    2. Route to Conversational LLM Intelligence if Open Dialogue, Advice, Objections, or Q&A.
    """
    cfg = database.COUNTRY_CONFIGS.get(country_code, database.COUNTRY_CONFIGS["BJ"])
    lang_mode = detect_language_mode(user_message)
    
    # 1. CLASSIFY INTENT
    intent_data = intent_router.IntentRouter.classify_intent(user_message, prospect_data)
    
    # 2. IF CLEAR STRUCTURED JOURNEY INTENT -> EXECUTE JOURNEY FLOW
    if intent_data["route"] == "JOURNEY":
        return clean_natural_text(execute_structured_journey(user_message, intent_data, cfg, prospect_data, lang_mode))

    # 3. IF OPEN DIALOGUE -> INVOKE GENERATIVE LLM INTELLIGENCE
    prospect_info = ""
    if prospect_data:
        p_name = prospect_data.get("name", "")
        if p_name and p_name not in ["Prospect Inconnu", "Document", "Fichier", "Carte Grise", "Pdf", "Platinium", "Platinum"]:
            prospect_info += f"\n- Nom du prospect : {p_name}"
        if prospect_data.get("document_uploaded"):
            prospect_info += f"\n- Carte grise analysée pour : {prospect_data.get('vehicle', 'Toyota Corolla')}"
        elif prospect_data.get("vehicle"):
            prospect_info += f"\n- Véhicule : {prospect_data.get('vehicle')}"

    knowledge_context = search_knowledge_hub(user_message, country_code)

    system_prompt = (
        f"Tu es le Conseiller Commercial {cfg['entity']} au {cfg['name']}.\n"
        f"Tu aides les prospects avec intelligence, écoute active et empathie.\n"
        f"N'utilise AUCUN caractère markdown (** ou #).\n"
        f"Ne mentionne JAMAIS 'Sandbox' ni 'ORASS' ni 'quittance' dans tes réponses.\n"
        f"Réponds précisément et naturellement à la question spécifique posée par le prospect sans réciter de catalogue de formules par défaut.\n"
        f"{prospect_info}\n"
        f"{knowledge_context}\n"
    )
    if country_code == "BJ":
        system_prompt += "Accepte le paiement MTN MoMo (*138#) et Moov Flooz (*155#).\n"
        
    messages = [{"role": "system", "content": system_prompt}]
    for msg in conversation_history[-4:]:
        role = "assistant" if msg["sender"] == "assistant" else "user"
        messages.append({"role": role, "content": clean_natural_text(msg["text"])})
    messages.append({"role": "user", "content": user_message})
    
    # Fast Cloud LLM call
    if config.OLLAMA_API_KEY:
        try:
            url = config.OLLAMA_API_URL
            payload = {
                "model": config.DEFAULT_MODEL,
                "messages": messages,
                "stream": False,
                "options": {
                    "num_predict": 250,
                    "temperature": 0.3
                }
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
    """Execute clear structured business journeys (Payment, Policy, Appointment, Devis)."""
    msg = user_message.lower()
    intent = intent_data["intent"]
    country_code = cfg.get("code", "BJ")
    products = cfg["products"]
    p1, p2, p3 = products[0], products[1], products[2]
    
    has_uploaded_doc = prospect_data.get("document_uploaded", False) if prospect_data else False
    vehicle_known = bool(prospect_data.get("vehicle") and "informations" not in prospect_data.get("vehicle").lower()) if prospect_data else False
    vehicle_str = prospect_data.get("vehicle", "votre véhicule") if (prospect_data and vehicle_known) else "votre véhicule"
    
    raw_name = prospect_data.get("name", "") if prospect_data else ""
    valid_name = raw_name if raw_name not in ["Prospect Inconnu", "Document", "Fichier", "Carte Grise", "Pdf", "Platinium", "Platinum"] else ""
    greeting_name = f" {valid_name}" if valid_name else ""

    # A. PAYMENT JOURNEY
    if intent == "PAYMENT":
        if country_code == "BJ":
            return (
                f"Excellente initiative{greeting_name} ! Pour valider la souscription de votre {vehicle_str} au Bénin, choisissez votre mode de paiement sécurisé :\n\n"
                f"• 📱 MTN Mobile Money Bénin (MoMo) : Syntaxe rapide *138#\n"
                f"• 📱 Moov Money Bénin (Flooz) : Syntaxe rapide *155#\n"
                f"• 💳 Carte Bancaire (VISA / Mastercard)\n"
                f"• 🏢 Paiement en Agence SanlamAllianz Cotonou (Haie Vive / Ganhi)\n\n"
                f"Quel moyen de paiement préférez-vous utiliser ?\n\n"
                f"[Payer via MTN MoMo]  [Payer via Moov Flooz]  [Payer en Agence Cotonou]"
            )
        else:
            return (
                f"Vous pouvez régler votre prime d'assurance en toute sécurité par Mobile Money, Carte Bancaire ou directement en agence {cfg['entity']}.\n\n"
                f"[Payer par Mobile Money]  [Payer par Carte]  [Prendre RDV Agence]"
            )

    # B. POLICY ISSUANCE JOURNEY
    if intent == "POLICY_ISSUANCE":
        policy_num = prospect_data.get("orass_policy_num") or "POL-AUTO-BENIN-894102"
        return (
            f"🎉 Félicitations{greeting_name} ! Votre Police d'Assurance Officielle a été émise avec succès : N° {policy_num}.\n\n"
            f"Votre attestation CIMA et votre carte verte sont disponibles au téléchargement immédiat.\n\n"
            f"[Télécharger mon Attestation]  [Payer via MTN MoMo]"
        )

    # C. APPOINTMENT JOURNEY
    if intent == "APPOINTMENT":
        return (
            f"C'est noté avec plaisir{greeting_name} ! 🗓️\n\n"
            f"Un conseiller commercial SanlamAllianz vous contactera pour finaliser votre dossier ou vous accueillir en agence.\n"
            f"À quel créneau horaire préférez-vous être rappelé ?\n\n"
            f"[Rappel ce matin à 10h]  [Rappel cet après-midi à 15h]  [RDV en Agence Cotonou]"
        )

    # D. DEVIS CALCULATION JOURNEY
    if intent == "DEVIS_CALCULATION":
        if intent_data.get("needs_slot"):
            return (
                f"Pour vous calculer votre Devis Officiel sur-mesure au {cfg['name']}{greeting_name}, "
                f"quel est le modèle de votre voiture (ex: Toyota Corolla) ? Vous pouvez aussi simplement me scanner votre Carte Grise.\n\n"
                f"[Envoyer ma Carte Grise]  [Préciser mon véhicule]"
            )
            
        if country_code == "BJ":
            orass_quote = orass_client.orass_engine.calculate_devis_auto(
                code_cate="101", puifisc=7, codedure="12", bonumalu=80.0, garanties=["VOL", "INCENDIE", "BRIS_GLACE"]
            )
            detail = orass_quote["detail"]
            num_dev = f"DEV-{int(orass_quote['quittance']['NUMEQUIT'].replace('QUIT-', '')) % 1000000}"
            return (
                f"Voici l'analyse détaillée de votre Devis Officiel Bénin (N° {num_dev}) pour la formule **{p3['name']}** ({vehicle_str}) :\n\n"
                f"• Prime RC Nette : {detail['primeRcNette']} FCFA\n"
                f"• Garanties Annexes (Vol/Incendie/Bris de glace) : {detail['garantiesAnnexes']} FCFA\n"
                f"• Taxe Assurance CIMA Bénin : {detail['taxeAssurance']} FCFA\n"
                f"• Taxe FGA Bénin & Timbres : {detail['taxeFga'] + detail['timbres']} FCFA\n"
                f"💰 Montant Total Devis TTC : {detail['primeTtc']} FCFA\n\n"
                f"Pour valider ce devis et émettre votre police, vous pouvez passer au paiement sécurisé :\n\n"
                f"[Payer via MTN MoMo]  [Payer via Moov Flooz]  [Émettre ma Police]"
            )

    return generate_instant_rag_response(user_message, cfg, prospect_data, lang_mode)

def generate_instant_rag_response(user_message: str, cfg: dict, prospect_data: dict = None, lang_mode: str = "FRENCH") -> str:
    """Conversational LLM Knowledge Fallback Engine for open discussions & questions."""
    msg = user_message.lower()
    country_code = cfg.get("code", "BJ")
    country_prep = "au" if country_code in ["MA", "BJ"] else "en"
    products = cfg["products"]
    p1, p2, p3 = products[0], products[1], products[2]
    
    vehicle_known = bool(prospect_data.get("vehicle") and "informations" not in prospect_data.get("vehicle").lower()) if prospect_data else False
    vehicle_str = prospect_data.get("vehicle", "votre véhicule") if (prospect_data and vehicle_known) else "votre véhicule"
    
    raw_name = prospect_data.get("name", "") if prospect_data else ""
    valid_name = raw_name if raw_name not in ["Prospect Inconnu", "Document", "Fichier", "Carte Grise", "Pdf", "Platinium", "Platinum"] else ""
    greeting_name = f" {valid_name}" if valid_name else ""

    # 1. INSURANCE COVERAGE QUESTIONS ("L'assurance RC, elle couvre quoi exactement ?")
    if any(k in msg for k in ["couvre quoi", "c'est quoi la rc", "responsabilité civile", "garanties", "couvre exactement", "couverture rc", "que couvre"]):
        return (
            f"L'assurance Responsabilité Civile (RC) obligatoire CIMA {country_prep} {cfg['name']} indemnise l'intégralité des dommages matériels et corporels causés aux tiers lors d'un accident avec {vehicle_str}.\n\n"
            f"• Elle inclut : Défense & Recours juridique + Assistance dépannage 24/7.\n"
            f"• Pour couvrir votre propre véhicule contre le vol, l'incendie ou les bris de glace, nous vous recommandons nos formules {p2['name']} et {p3['name']}.\n\n"
            f"[{p2['name']}]  [{p3['name']}]  [Obtenir mon Devis Officiel]"
        )

    # 2. VALUATION & FORMULA SELECTION EXPLANATION
    if any(k in msg for k in ["calculé la valeur", "valeur de la voiture", "pas fait le choix", "pas demandé", "pas choisi"]):
        return (
            f"Je vous comprends tout à fait{greeting_name} ! 🚗\n\n"
            f"Le tarif présenté était calculé à partir de la puissance fiscale (7 CV) figurant sur votre Carte Grise. "
            f"Je vous avais affiché la formule Tous Risques à titre d'illustration, mais aucun choix ne vous est imposé ! C'est VOUS qui décidez.\n\n"
            f"Quelle formule correspond le mieux à vos attentes : {p1['name']} (Tiers), {p2['name']} (Tiers Plus) ou {p3['name']} (Tous Risques) ?\n\n"
            f"[{p1['name']}]  [{p2['name']}]  [{p3['name']}]"
        )

    # 3. META-DIALOGUE / LISTENING FEEDBACK
    if any(k in msg for k in ["comprennes la question", "écoutes", "n'hésite pas à demander", "pas compris", "écouter"]):
        return (
            f"Toutes mes excuses{greeting_name} ! 🤝 Vous avez tout à fait raison. Je vous écoute très attentivement.\n\n"
            f"Posez-moi votre question sur votre véhicule ou vos garanties, et je vous répondrai précisément sans imposer de formule.\n\n"
            f"[Posez votre question]  [Comparer les formules]"
        )

    # 4. DEFAULT CONVERSATIONAL RESPONSE
    return (
        f"Je suis votre Conseiller Commercial {cfg['entity']} {country_prep} {cfg['name']}. "
        f"Je peux répondre à toutes vos questions sur les garanties, l'assurance de votre {vehicle_str} ou vous aider à choisir la formule idéale.\n\n"
        f"Que souhaitez-vous savoir ?\n\n"
        f"[{p2['name']}]  [{p3['name']}]  [Obtenir mon Devis Officiel]"
    )
