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
    
    # Remove duplicate parenthesis text like (Tiers) (Tiers) or (Tous Risques) (Tous Risques)
    cleaned = re.sub(r'\(([^)]+)\)\s*\(\1\)', r'(\1)', cleaned)
    
    # Clean multiple spaces & normalize newlines
    cleaned = re.sub(r'[ \t]+', ' ', cleaned)
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned).strip()
    
    # Ensure proper sentence ending
    if cleaned and cleaned[-1] not in ".!?]😊🚘🛡️📊🗓️":
        cleaned += "."
        
    return cleaned

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
    """Generate rapid, zero-freeze conversational response with prospect state memory."""
    
    cfg = database.COUNTRY_CONFIGS.get(country_code, database.COUNTRY_CONFIGS["CI"])
    doc_context = search_knowledge_hub(user_message, country_code)
    
    products_str = "\n".join([f"- {p['name']} : {p['desc']}" for p in cfg['products']])
    country_prep = "au" if country_code == "MA" else "en"
    
    prospect_info = ""
    if prospect_data:
        if prospect_data.get("name") and prospect_data.get("name") != "Prospect Inconnu":
            prospect_info += f"\n- Prénom prospect : {prospect_data.get('name')}"
        if prospect_data.get("document_uploaded"):
            prospect_info += f"\n- Carte grise analysée pour : {prospect_data.get('vehicle', 'Mercedes Série Spéciale')}. Devis calculé !"
        elif prospect_data.get("vehicle"):
            prospect_info += f"\n- Modèle véhicule : {prospect_data.get('vehicle')}"

    system_prompt = (
        f"Tu es le Chargé de Clientèle Automobile SanlamAllianz {country_prep} {cfg['name']} ({cfg['entity']}).\n"
        f"Tu dialogues naturellement sur WhatsApp et au téléphone avec votre prospect.\n\n"
        f"DIRECTIVES RIGOUREUSES DE STYLE PARLÉ ET FLUIDE :\n"
        f"1. Rédige un français naturel, fluide, chaleureux et direct. N'utilise AUCUN caractère spécial de mise en forme (PAS d'étoiles **, PAS de dièses #, PAS de parenthèses superflues).\n"
        f"2. Ne répète jamais les mêmes termes à la suite. Écris simplement le nom des formules : Auto Classique, Auto Zen, Auto Platinum.\n"
        f"3. Présente les devis sous forme de phrases claires et agréables à lire et à entendre à voix haute.\n"
        f"4. Sois concis et accueillant (50 à 80 mots maximum).\n"
        f"5. Termine toujours par 2 propositions de choix entre crochets simple `[Choix 1]` `[Choix 2]`.\n\n"
        f"CONTEXTE OFFRES ET GARANTIES :\n"
        f"- Monnaie : {cfg['currency']}\n"
        f"- Garages agréés : {cfg['default_garage']}\n"
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
            
    return clean_natural_text(generate_instant_rag_response(user_message, cfg, prospect_data))

def generate_instant_rag_response(user_message: str, cfg: dict, prospect_data: dict = None) -> str:
    """Instant 0.01s Knowledge Engine tailored dynamically to the question and country context."""
    msg = user_message.lower()
    country_code = cfg.get("code", "CI")
    country_prep = "au" if country_code == "MA" else "en"
    products = cfg["products"]
    p1, p2, p3 = products[0], products[1], products[2]
    
    doc_uploaded = prospect_data.get("document_uploaded", False) if prospect_data else False
    vehicle_str = prospect_data.get("vehicle", "votre véhicule") if prospect_data else "votre véhicule"
    name_str = prospect_data.get("name", "") if prospect_data else ""
    greeting_name = f" M. {name_str}" if name_str and name_str != "Prospect Inconnu" else ""

    # 1. Intent: Price / Devis / Tarif Calculation Request for all 3 formulas
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

    # 2. Intent: International Coverage across 27 countries
    if any(k in msg for k in ["26", "28", "27", "étranger", "etranger", "couverture", "réseau", "reseau"]):
        return (
            f"Bonne nouvelle{greeting_name} ! Votre contrat {cfg['entity']} inclut la garantie Panafricaine. "
            f"Vous êtes parfaitement couvert dans l'ensemble des 27 pays du réseau SanlamAllianz. "
            f"En cas de déplacement, votre assistance reste active sans interruption.\n\n"
            f"[Obtenir mon devis]  [Prendre RDV Conseiller]"
        )

    # 3. Intent: Explicit Relocation across countries
    if any(k in msg for k in ["déménage", "demenage", "transfert de contrat", "changement de pays"]):
        return (
            f"En tant que premier groupe d'assurance Panafricain, {cfg['entity']} facilite votre mobilité. "
            f"Votre contrat peut être transféré directement vers notre filiale locale sans aucune pénalité.\n\n"
            f"[Valider le transfert pays]  [Garder mon contrat actuel]"
        )

    # 4. Intent: Competitor Switch
    if any(k in msg for k in ["concurrent", "autre assureur", "actuellement assuré", "déjà assuré", "chez quelqu'un d'autre"]):
        return (
            f"Bienvenue chez {cfg['entity']} ! "
            f"Nous gérons gratuitement la résiliation auprès de votre ancien assureur et nous reprenons 100% de votre bonus d'ancienneté.\n\n"
            f"[Calculer mon tarif avec Bonus]  [Scanner ma Carte Grise]"
        )

    # 5. Intent: Single Price / Devis / Tarif Request
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

    # Default Dynamic Orientation Response
    return (
        f"Chez {cfg['entity']} {country_prep} {cfg['name']}, nous proposons 3 niveaux de protection :\n"
        f"1. {p1['name']} : la couverture essentielle.\n"
        f"2. {p2['name']} : la formule équilibrée avec vol et bris de glace.\n"
        f"3. {p3['name']} : la protection tous risques intégrale.\n\n"
        f"Quelle formule souhaitez-vous découvrir ?\n\n"
        f"[{p2['name']}]  [{p3['name']}]  [Obtenir mon tarif]"
    )
