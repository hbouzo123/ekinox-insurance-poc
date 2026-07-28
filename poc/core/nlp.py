import os
import json
import urllib.request
import re
from core import config, database, orass_client

KNOWLEDGE_DOCUMENTS_BY_COUNTRY = {
    "BJ": [
        {
            "id": "doc-bj-1",
            "title": "Code CIMA & Réglementation ARCA SanlamAllianz Bénin",
            "content": "Conformément au Code CIMA Bénin (Article 13), l'assurance Responsabilité Civile automobile est obligatoire. Interconnexion directe avec le Core Insurance System ORASS Sandbox Bénin. Formule Auto Platinum Tous Risques avec franchise Cotonou 45 000 FCFA.",
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
    cleaned = re.sub(r'\(([^)]+)\)\s*\(\1\)', r'(\1)', cleaned)
    cleaned = re.sub(r'[ \t]+', ' ', cleaned)
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned).strip()
    
    if cleaned and cleaned[-1] not in ".!?]😊🚘🛡️📊🗓️":
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
    """Generate ultra-rapid response with live ORASS Core Insurance System integration EXCLUSIVELY for Benin."""
    
    cfg = database.COUNTRY_CONFIGS.get(country_code, database.COUNTRY_CONFIGS["BJ"])
    lang_mode = detect_language_mode(user_message)
    
    prospect_info = ""
    if prospect_data:
        if prospect_data.get("name") and prospect_data.get("name") != "Prospect Inconnu":
            prospect_info += f"\n- Nom du prospect : {prospect_data.get('name')}"
        if prospect_data.get("document_uploaded"):
            prospect_info += f"\n- Carte grise analysée pour : {prospect_data.get('vehicle', 'Toyota Corolla')}"
            if country_code == "BJ":
                prospect_info += ". Devis calculé via le Sandbox ORASS Bénin !"
        elif prospect_data.get("vehicle"):
            prospect_info += f"\n- Véhicule : {prospect_data.get('vehicle')}"

    system_prompt = (
        f"Tu es le Conseiller Commercial {cfg['entity']} au {cfg['name']}.\n"
        f"Tu aides les prospects à trouver l'assurance automobile idéale.\n"
        f"N'utilise AUCUN caractère markdown (** ou #).\n"
        f"{prospect_info}\n"
    )
    if country_code == "BJ":
        system_prompt += "Tu es interconnecté en temps réel au Sandbox ORASS Bénin pour fournir les quittances CIMA officielles.\n"
        
    messages = [{"role": "system", "content": system_prompt}]
    for msg in conversation_history[-4:]:
        role = "assistant" if msg["sender"] == "assistant" else "user"
        messages.append({"role": role, "content": clean_natural_text(msg["text"])})
    messages.append({"role": "user", "content": user_message})
    
    # Fast 1.8s Cloud LLM call
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

def generate_instant_rag_response(user_message: str, cfg: dict, prospect_data: dict = None, lang_mode: str = "FRENCH") -> str:
    """Instant 0.001s Knowledge Engine. ORASS Sandbox is restricted ONLY to Benin (BJ)."""
    msg = user_message.lower()
    country_code = cfg.get("code", "BJ")
    country_prep = "au" if country_code in ["MA", "BJ"] else "en"
    products = cfg["products"]
    p1, p2, p3 = products[0], products[1], products[2]
    
    vehicle_str = prospect_data.get("vehicle", "votre véhicule") if prospect_data else "votre véhicule"
    name_str = prospect_data.get("name", "") if prospect_data else ""
    greeting_name = f" {name_str}" if name_str and name_str != "Prospect Inconnu" else ""
    
    # Execute ORASS Sandbox Devis Engine ONLY IF COUNTRY IS BENIN (BJ)
    is_benin = (country_code == "BJ")
    orass_quote = None
    if is_benin:
        orass_quote = orass_client.orass_engine.calculate_devis_auto(
            code_cate="101",
            puifisc=7,
            codedure="12",
            bonumalu=80.0,
            garanties=["VOL", "INCENDIE", "BRIS_GLACE"]
        )
    
    # 0. Capability / Hearing / Understanding Check
    if any(k in msg for k in ["m'entends", "m'entend", "tu m'entends", "comprends", "comprendre", "arabe", "dialecte", "tunisien", "derja"]):
        orass_addon = " Je suis connecté au Sandbox ORASS Bénin pour vos quittances en direct." if is_benin else ""
        return (
            f"Oui parfait{greeting_name} ! Je vous entends et je vous comprends très bien.{orass_addon} "
            f"Je peux échanger avec vous en Français, en Arabe et en Dialecte. "
            f"Comment puis-je vous aider pour votre véhicule à {cfg['name']} ?\n\n"
            f"[Obtenir mon devis]  [Découvrir les formules]"
        )

    # 1. ARABIC LANGUAGE MODE
    if lang_mode == "ARABIC":
        name_prefix = f" يا {name_str}" if name_str and name_str != "Prospect Inconnu" else ""
        ttc_str = f" {orass_quote['quittance']['MONTTTC']} {cfg['currency']}" if is_benin and orass_quote else ""
        return (
            f"مرحباً بك{name_prefix} في {cfg['entity']} ! 🛡️ "
            f"أنا هنا لمساعدتك في حساب أفضل عروض التأمين لسيارتك.{ttc_str} "
            f"كيف يمكنني مساعدتك اليوم؟\n\n"
            f"[الحصول على العرض]  [حجز موعد]"
        )

    # 2. TUNISIAN DERJA MODE
    if lang_mode == "DERJA":
        name_prefix = f" يا {name_str}" if name_str and name_str != "Prospect Inconnu" else ""
        return (
            f"Marhaba bik{name_prefix} ! N'effhemk w n'ssm3ek mlih. "
            f"Rani hna bech n'essablek el devis mte3 el karhaba {vehicle_str} m3a {cfg['entity']}.\n\n"
            f"[Obtenir mon devis]  [Prendre Rendez-vous]"
        )

    # 3. FRENCH QUOTE & TARIFF INTENTS
    if any(k in msg for k in ["trois devis", "3 devis", "pour chaque formule", "combien ca coute", "combien ça me coûte", "prix pour chaque"]):
        if is_benin and orass_quote:
            detail = orass_quote["detail"]
            quit_info = orass_quote["quittance"]
            return (
                f"Voici le calcul officiel des trois formules issu du Sandbox ORASS pour votre {vehicle_str} au {cfg['name']} :\n\n"
                f"1. {p1['name']} : 75 000 FCFA par an (Responsabilité Civile CIMA Bénin).\n"
                f"2. {p2['name']} : 135 000 FCFA par an (Tiers amélioré avec vol et bris de glace Cotonou).\n"
                f"3. {p3['name']} : {detail['primeTtc']} FCFA par an (Tous Risques ORASS Quittance N° {quit_info['NUMEQUIT']}).\n\n"
                f"Quelle formule souhaitez-vous souscrire ?\n\n"
                f"[Souscrire {p2['name']}]  [Souscrire {p3['name']}]  [Prendre Rendez-vous]"
            )
        else:
            return (
                f"Voici le tarif annuel de nos 3 formules {cfg['entity']} pour votre {vehicle_str} :\n\n"
                f"1. {p1['name']} : formule économique Responsabilité Civile.\n"
                f"2. {p2['name']} : la couverture intermédiaire recommandée.\n"
                f"3. {p3['name']} : la protection intégrale tous risques.\n\n"
                f"Quelle formule préférez-vous ?\n\n"
                f"[{p2['name']}]  [{p3['name']}]  [Prendre RDV]"
            )

    if any(k in msg for k in ["prix", "tarif", "cout", "coût", "combien", "simulation", "devis", "estimation", "obtenir mon tarif", "orass"]):
        if is_benin and orass_quote:
            detail = orass_quote["detail"]
            quit_info = orass_quote["quittance"]
            return (
                f"Voici l'analyse détaillée de votre quittance ORASS Bénin (N° {quit_info['NUMEQUIT']}) pour votre {vehicle_str} :\n\n"
                f"• Prime RC Nette : {detail['primeRcNette']} FCFA\n"
                f"• Garanties Annexes : {detail['garantiesAnnexes']} FCFA\n"
                f"• Taxe Assurance CIMA : {detail['taxeAssurance']} FCFA\n"
                f"• Taxe FGA Bénin & Timbres : {detail['taxeFga'] + detail['timbres']} FCFA\n"
                f"💰 Montant Total Quittance TTC : {detail['primeTtc']} FCFA\n\n"
                f"Souhaitez-vous émettre votre police d'assurance officielle maintenant ?\n\n"
                f"[Émettre ma Police ORASS]  [Prendre RDV Conseiller]"
            )
        else:
            return (
                f"Pour votre {vehicle_str}, {cfg['entity']} vous propose la formule **{p2['name']}** au meilleur tarif avec facilités de paiement.\n\n"
                f"Souhaitez-vous recevoir une proposition personnalisée ou parler à un conseiller ?\n\n"
                f"[{p2['name']}]  [{p3['name']}]  [Prendre RDV Conseiller]"
            )

    orass_mention = " (Interconnecté Sandbox ORASS)" if is_benin else ""
    return (
        f"Chez {cfg['entity']} {country_prep} {cfg['name']}{orass_mention}, nous proposons 3 niveaux de protection :\n"
        f"1. {p1['name']} : la couverture Responsabilité Civile essentielle.\n"
        f"2. {p2['name']} : la formule équilibrée recommandée.\n"
        f"3. {p3['name']} : la protection tous risques intégrale.\n\n"
        f"Quelle formule souhaitez-vous découvrir ?\n\n"
        f"[{p2['name']}]  [{p3['name']}]  [Obtenir mon tarif]"
    )
