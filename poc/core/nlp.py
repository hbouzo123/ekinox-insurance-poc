import os
import json
import urllib.request
import re
from core import config, database

KNOWLEDGE_DOCUMENTS_BY_COUNTRY = {
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
    
    # Remove markdown bold/italic asterisks & underscores
    cleaned = re.sub(r'[*_#]', '', text)
    
    # Remove duplicate parenthesis text like (Tiers) (Tiers)
    cleaned = re.sub(r'\(([^)]+)\)\s*\(\1\)', r'(\1)', cleaned)
    
    # Clean multiple spaces & normalize newlines
    cleaned = re.sub(r'[ \t]+', ' ', cleaned)
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned).strip()
    
    # Ensure proper sentence ending
    if cleaned and cleaned[-1] not in ".!?]😊🚘🛡️📊🗓️":
        cleaned += "."
        
    return cleaned

def detect_language_mode(user_message: str) -> str:
    """Detect whether user speaks French, Standard Arabic, or Maghrebi/Tunisian Derja."""
    text = user_message.strip()
    
    # Check for Arabic Script
    if re.search(r'[\u0600-\u06FF]', text):
        return "ARABIC"
        
    text_lower = text.lower()
    derja_keywords = [
        "aychik", "aaffia", "afia", "marhaba", "chneyya", "bahi", "behi", "labes", "aslema",
        "khouya", "shokran", "sahha", "yatik", "bch", "nحب", "kifech", "bchnekhou", "mrigal"
    ]
    if any(k in text_lower for k in derja_keywords):
        return "DERJA"
        
    return "FRENCH"

def search_knowledge_hub(query: str, country_code: str = "CI") -> str:
    """Search country-specific Knowledge Hub documents."""
    docs = KNOWLEDGE_DOCUMENTS_BY_COUNTRY.get(country_code, KNOWLEDGE_DOCUMENTS_BY_COUNTRY["CI"])
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

def generate_llm_response(conversation_history: list, user_message: str, country_code: str = "CI", prospect_data: dict = None) -> str:
    """Generate rapid, zero-freeze conversational response with prospect state memory and strict language mirroring."""
    
    cfg = database.COUNTRY_CONFIGS.get(country_code, database.COUNTRY_CONFIGS["CI"])
    doc_context = search_knowledge_hub(user_message, country_code)
    lang_mode = detect_language_mode(user_message)
    
    products_str = "\n".join([f"- {p['name']} : {p['desc']}" for p in cfg['products']])
    country_prep = "au" if country_code == "MA" else "en"
    
    prospect_info = ""
    if prospect_data:
        if prospect_data.get("name") and prospect_data.get("name") != "Prospect Inconnu":
            prospect_info += f"\n- Nom/Prénom du prospect : {prospect_data.get('name')}"
        if prospect_data.get("document_uploaded"):
            prospect_info += f"\n- Carte grise analysée pour : {prospect_data.get('vehicle', 'Mercedes Série Spéciale')}. Devis calculé !"
        elif prospect_data.get("vehicle"):
            prospect_info += f"\n- Modèle véhicule : {prospect_data.get('vehicle')}"

    system_prompt = (
        f"Tu es le Chargé de Clientèle Automobile SanlamAllianz {country_prep} {cfg['name']} ({cfg['entity']}).\n\n"
        f"RÈGLE ABSOLUE DE MIROIR LINGUISTIQUE (STRICT LANGUAGE MIRRORING) :\n"
        f"1. Si le message de l'utilisateur est en FRANÇAIS -> Tu dois répondre 100% en FRANÇAIS naturel et fluide.\n"
        f"2. Si le message est en ARABE LITTÉRAIRE (العربية الفصحى) -> Tu dois répondre 100% en ARABE LITTÉRAIRE (العربية الفصحى).\n"
        f"3. Si le message est en DIALECTE TUNISIEN / MAGHRÉBIN (Derja) -> Tu dois répondre 100% en DIALECTE TUNISIEN / MAGHRÉBIN (اللهجة التونسية/المغاربية) fluide et chaleureux !\n\n"
        f"RÈGLES DE STYLE :\n"
        f"- N'utilise AUCUN caractère de mise en forme markdown (PAS d'étoiles **, PAS de dièses #, PAS de parenthèses répétitives).\n"
        f"- Si le nom du prospect est connu ({prospect_data.get('name', '') if prospect_data else ''}), adresse-toi à lui naturellement.\n"
        f"- Sois concis et accueillant (40 à 75 mots).\n"
        f"- Termine toujours par 2 options d'action entre crochets simple `[Option 1]` `[Option 2]`.\n\n"
        f"OFFRES ET CONTEXTE :\n"
        f"- Monnaie : {cfg['currency']}\n"
        f"- Produits {cfg['entity']} :\n{products_str}\n"
        f"{prospect_info}\n"
    )
    
    if doc_context:
        system_prompt += f"\nBASE DE CONNAISSANCE :\n{doc_context}\n"
        
    messages = [{"role": "system", "content": system_prompt}]
    
    for msg in conversation_history[-6:]:
        role = "assistant" if msg["sender"] == "assistant" else "user"
        clean_text = clean_natural_text(msg["text"])
        messages.append({"role": role, "content": clean_text})
        
    messages.append({"role": "user", "content": user_message})
    
    # Try Fast Cloud LLM call with 6.0s timeout and 400 token limit
    if config.OLLAMA_API_KEY:
        for model_name in [config.DEFAULT_MODEL, config.FALLBACK_MODEL]:
            try:
                url = config.OLLAMA_API_URL
                payload = {
                    "model": model_name,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "num_predict": 400,
                        "temperature": 0.4
                    }
                }
                data = json.dumps(payload).encode('utf-8')
                req = urllib.request.Request(url, data=data, headers={
                    "Authorization": f"Bearer {config.OLLAMA_API_KEY}",
                    "Content-Type": "application/json"
                })
                resp = urllib.request.urlopen(req, timeout=6.0)
                result = json.loads(resp.read().decode('utf-8'))
                reply = result.get("message", {}).get("content", "").strip()
                if reply and len(reply) > 15:
                    return clean_natural_text(reply)
            except Exception as e:
                print(f"[LLM Core] Model {model_name} call exception ({e}). Trying next fallback...")
            
    return clean_natural_text(generate_instant_rag_response(user_message, cfg, prospect_data, lang_mode))

def generate_instant_rag_response(user_message: str, cfg: dict, prospect_data: dict = None, lang_mode: str = "FRENCH") -> str:
    """Instant 0.01s Knowledge Engine with dynamic language mirroring."""
    msg = user_message.lower()
    country_code = cfg.get("code", "CI")
    country_prep = "au" if country_code == "MA" else "en"
    products = cfg["products"]
    p1, p2, p3 = products[0], products[1], products[2]
    
    doc_uploaded = prospect_data.get("document_uploaded", False) if prospect_data else False
    vehicle_str = prospect_data.get("vehicle", "votre véhicule") if prospect_data else "votre véhicule"
    name_str = prospect_data.get("name", "") if prospect_data else ""
    
    # 1. ARABIC LANGUAGE MODE (Standard Arabic Script)
    if lang_mode == "ARABIC":
        name_prefix = f" يا {name_str}" if name_str and name_str != "Prospect Inconnu" else ""
        return (
            f"مرحباً بك{name_prefix} في **{cfg['entity']}** ! 🛡️\n"
            f"يسعدنا جداً تقديم أفضل عروض تأمين السيارات المناسبة لسيارتك {vehicle_str}.\n"
            f"نقدم لك ثلاث صيغ ممتازة: 1. التأمين الأساسي 2. التأمين المكتمل 3. التأمين الشامل للأخطار.\n\n"
            f"[الحصول على العرض]  [حجز موعد]"
        )

    # 2. TUNISIAN / MAGHREBI DERJA MODE (Derja / Dialect)
    if lang_mode == "DERJA":
        name_prefix = f" يا {name_str}" if name_str and name_str != "Prospect Inconnu" else ""
        return (
            f"Marhaba bik{name_prefix} ! Yatik el afia. Aychak, rani m3ak bech n'awnek fi koll chay.\n"
            f"Najjem n'essablek el tarif mte3 el karhabtek {vehicle_str} fi daqiqteyn fil formule li tnasbek.\n\n"
            f"[Obtenir mon devis]  [Prendre Rendez-vous]"
        )

    # 3. FRENCH LANGUAGE MODE (Standard French)
    greeting_name = f" {name_str}" if name_str and name_str != "Prospect Inconnu" else ""

    if any(k in msg for k in ["trois devis", "3 devis", "pour chaque formule", "combien ca coute", "combien ça me coûte", "prix pour chaque"]):
        if country_code == "CI":
            return (
                f"Avec plaisir{greeting_name} ! Voici l'estimation détaillée pour votre {vehicle_str} :\n\n"
                f"1. Auto Classique : 75 000 FCFA par an (Responsabilité Civile obligatoire CIMA et défense recours).\n"
                f"2. Auto Zen : 135 000 FCFA par an (Tiers amélioré avec protection contre le vol, l'incendie et le bris de glace).\n"
                f"3. Auto Platinum : 250 000 FCFA par an (Tous Risques intégral avec véhicule de remplacement et assistance 0 km).\n\n"
                f"Quelle formule correspond le mieux à votre budget ?\n\n"
                f"[Choisir Auto Zen]  [Choisir Auto Platinum]  [Prendre Rendez-vous]"
            )
        elif country_code == "MA":
            return (
                f"Avec plaisir{greeting_name} ! Voici le détail des tarifs Sanlam Maroc pour votre {vehicle_str} :\n\n"
                f"1. Assur Auto Pass : 2 400 DH par an (Responsabilité Civile et assistance de base).\n"
                f"2. Pack L Hemza : 4 200 DH par an (Tiers Plus avec vol, incendie et bris de glace sans franchise).\n"
                f"3. Assur Auto Intégrale : 7 800 DH par an (Tous Risques complet avec rachat de franchise).\n\n"
                f"Quelle formule préférez-vous ?\n\n"
                f"[Choisir Pack L Hemza]  [Choisir Assur Auto Intégrale]"
            )
        else:
            return (
                f"Voici vos trois devis personnalisés pour votre {vehicle_str} :\n\n"
                f"1. Auto Pack Teranga : 110 000 FCFA par an.\n"
                f"2. Auto Zen Teranga : 195 000 FCFA par an.\n"
                f"3. Tous Risques Avantage : 350 000 FCFA par an.\n\n"
                f"Laquelle souhaitez-vous retenir ?\n\n"
                f"[Choisir Auto Zen Teranga]  [Choisir Tous Risques Avantage]"
            )

    if any(k in msg for k in ["prix", "tarif", "cout", "coût", "combien", "simulation", "devis", "estimation", "obtenir mon tarif"]):
        if doc_uploaded or (prospect_data and prospect_data.get("vehicle")):
            return (
                f"Voici vos tarifs personnalisés pour votre {vehicle_str} :\n\n"
                f"1. {p1['name']} : {p1['desc']}.\n"
                f"2. {p2['name']} : {p2['desc']}.\n"
                f"3. {p3['name']} : {p3['desc']}.\n\n"
                f"Quelle formule souhaitez-vous retenir pour votre souscription ?\n\n"
                f"[{p2['name']}]  [{p3['name']}]  [Prendre Rendez-vous]"
            )
        else:
            return (
                f"Le tarif dépend du modèle et de la puissance fiscale de votre véhicule. "
                f"Pour obtenir le montant exact immédiatement, vous pouvez scanner votre carte grise directement dans ce chat.\n\n"
                f"[Scanner ma Carte Grise]  [Prendre RDV Conseiller]"
            )

    return (
        f"Chez {cfg['entity']} {country_prep} {cfg['name']}, nous proposons 3 niveaux de protection :\n"
        f"1. {p1['name']} : la couverture essentielle.\n"
        f"2. {p2['name']} : la formule équilibrée avec vol et bris de glace.\n"
        f"3. {p3['name']} : la protection tous risques intégrale.\n\n"
        f"Quelle formule souhaitez-vous découvrir ?\n\n"
        f"[{p2['name']}]  [{p3['name']}]  [Obtenir mon tarif]"
    )
