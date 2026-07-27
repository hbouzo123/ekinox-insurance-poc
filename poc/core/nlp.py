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
            "content": "Conformément au Code CIMA (Article 13), l'assurance Responsabilité Civile automobile est obligatoire. Formule Auto Platinum : dommages tous accidents jusqu'à 50 000 000 FCFA avec assistance 0 km à Abidjan et intérieur du pays. Franchise fixe de 50 000 FCFA.",
            "category": "garantie"
        }
    ],
    "MA": [
        {
            "id": "doc-ma-1",
            "title": "Réglementation ACAPS & Conditions Générales Sanlam Maroc",
            "content": "Sous le contrôle de l'ACAPS, l'offre Assur'Auto Intégrale Sanlam Maroc couvre les dommages tous risques avec rachat de franchise (0 DH reste à charge en garage agréé Sanlam à Casablanca/Rabat) et garantie Décès Toutes Causes.",
            "category": "garantie"
        }
    ],
    "SN": [
        {
            "id": "doc-sn-1",
            "title": "Code CIMA Sénégal & Offre SanlamAllianz Sénégal",
            "content": "La formule Tous Risques Avantage SanlamAllianz Sénégal inclut la protection complète du véhicule et des personnes transportées, l'Assistance Teranga 24/7 sur Dakar et régions. Franchise fixe de 40 000 FCFA.",
            "category": "garantie"
        }
    ]
}

def sanitize_response(text: str) -> str:
    """Ensure response never ends mid-sentence."""
    if not text:
        return text
    text = text.strip()
    # Check if text ends cleanly with punctuation or brackets
    if text[-1] in ".!?]😊🚘🛡️📊🗓️":
        return text
    
    # Otherwise find last sentence ending punctuation
    last_punct = max(text.rfind('.'), text.rfind('!'), text.rfind('?'))
    if last_punct > 20:
        return text[:last_punct + 1]
    return text + "."

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
        return f"[Document Contractuel Officiel: {best_doc['title']}]\n{best_doc['content']}"
    return ""

def generate_llm_response(conversation_history: list, user_message: str, country_code: str = "CI", prospect_data: dict = None) -> str:
    """Generate rapid, zero-freeze conversational response with prospect state memory."""
    
    cfg = database.COUNTRY_CONFIGS.get(country_code, database.COUNTRY_CONFIGS["CI"])
    doc_context = search_knowledge_hub(user_message, country_code)
    
    products_str = "\n".join([f"- {p['name']} : {p['desc']}" for p in cfg['products']])
    country_prep = "au" if country_code == "MA" else "en"
    
    prospect_info = ""
    if prospect_data:
        if prospect_data.get("document_uploaded"):
            prospect_info += f"\n- CARTE GRISE SCANNÉE ET VALIDÉE ! Véhicule certifié : {prospect_data.get('vehicle', 'Mercedes Série Spéciale (CI-5099-AB2)')}. Le devis est déjà calculé !"
        if prospect_data.get("vehicle"):
            prospect_info += f"\n- Modèle véhicule : {prospect_data.get('vehicle')}"
        if prospect_data.get("appointment"):
            prospect_info += f"\n- Rendez-vous fixé : {prospect_data.get('appointment')}"

    system_prompt = (
        f"TU ES EXCLUSIVEMENT LE CHARGÉ DE CLIENTÈLE SANLAMALLIANZ {country_prep.upper()} {cfg['name'].upper()} ({cfg['entity']}).\n"
        f"LE PAYS ACTIF SELECTIONNÉ EST LE/LA {cfg['name'].upper()} ({cfg['code']}). NE CONFONDS JAMAIS AVEC UN AUTRE PAYS !\n"
        f"Toutes tes réponses doivent concerner la filiale {cfg['entity']} au/en {cfg['name']} avec les formules locales ({products_str}) en {cfg['currency']}.\n\n"
        f"CONTEXTE ASSUREUR LOCAL :\n"
        f"- Réglementation : {cfg['regulatory_body']}\n"
        f"- Monnaie : {cfg['currency']}\n"
        f"- Garages agréés : {cfg['default_garage']}\n"
        f"- Couverture internationale Panafricaine : Activée dans les 27 pays du réseau SanlamAllianz.\n"
        f"- Produits chez {cfg['entity']} :\n{products_str}\n"
        f"{prospect_info}\n\n"
        f"RÈGLES DE DIALOGUE CONTINU :\n"
        f"1. Reste 100% fidèle au pays actif ({cfg['name']}). Ne dis JAMAIS que tu es spécialisé pour un autre pays.\n"
        f"2. Ne coupe JAMAIS tes phrases au milieu ! Termine TOUJOURS par un point final.\n"
        f"3. Si le client pose une question sur la couverture dans les 27 pays du groupe, réponds-lui avec enthousiasme que la Carte Verte / Réseau Panafricain SanlamAllianz couvre ses déplacements dans tous les pays du réseau sans interruption !\n"
        f"4. Termine toujours par 2 choix pertinents entre crochets `[Choix 1]` `[Choix 2]`.\n"
    )
    
    if doc_context:
        system_prompt += f"\nBASE DE CONNAISSANCE :\n{doc_context}\n"
        
    messages = [{"role": "system", "content": system_prompt}]
    
    for msg in conversation_history[-6:]:
        role = "assistant" if msg["sender"] == "assistant" else "user"
        clean_text = re.sub(r'\[([^\]]+)\]', '', msg["text"]).strip()
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
                        "temperature": 0.5
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
                    return sanitize_response(reply)
            except Exception as e:
                print(f"[LLM Core] Model {model_name} call exception ({e}). Trying next fallback...")
            
    return sanitize_response(generate_instant_rag_response(user_message, cfg, prospect_data))

def generate_instant_rag_response(user_message: str, cfg: dict, prospect_data: dict = None) -> str:
    """Instant 0.01s Knowledge Engine tailored dynamically to the question and country context."""
    msg = user_message.lower()
    country_code = cfg.get("code", "CI")
    country_prep = "au" if country_code == "MA" else "en"
    products = cfg["products"]
    p1, p2, p3 = products[0], products[1], products[2]
    
    doc_uploaded = prospect_data.get("document_uploaded", False) if prospect_data else False
    vehicle_str = prospect_data.get("vehicle", "votre véhicule") if prospect_data else "votre véhicule"

    # 1. Intent: Panafrican International Coverage across 27 countries ("26", "28", "27", "pays", "étranger", "reseau", "réseau", "couverture")
    if any(k in msg for k in ["26", "28", "27", "étranger", "etranger", "couverture", "réseau", "reseau"]):
        return (
            f"Bonne nouvelle ! 🌍 Votre contrat **{cfg['entity']}** inclut l'extension de garantie Panafricaine.\n"
            f"Vous êtes parfaitement couvert dans l'ensemble des 27 pays où le groupe SanlamAllianz est présent ! En cas de déplacement, votre assistance et vos garanties restent valables sans interruption.\n\n"
            f"Souhaitez-vous obtenir votre devis personnalisé ou une attestation internationale ?\n\n"
            f"[📊 Obtenir mon devis]  [🗓️ Prendre RDV Conseiller]"
        )

    # 2. Intent: Explicit Relocation across countries ("déménage", "demenage", "transfert de contrat", "changement de pays")
    if any(k in msg for k in ["déménage", "demenage", "transfert de contrat", "changement de pays"]):
        return (
            f"Bonne nouvelle ! 🌍 En tant que premier groupe d'assurance Panafricain, **{cfg['entity']}** facilite votre mobilité.\n"
            f"Votre contrat peut être transféré directement vers notre filiale locale sans pénalité ni perte d'ancienneté !\n\n"
            f"Souhaitez-vous que notre pôle International prépare le transfert de votre dossier ?\n\n"
            f"[🌍 Valider le transfert pays]  [📄 Garder mon contrat {cfg['name']}]"
        )

    # 3. Intent: Competitor Switch / Already Insured elsewhere ("concurrent", "autre assureur", "actuellement assuré", "déjà assuré")
    if any(k in msg for k in ["concurrent", "autre assureur", "actuellement assuré", "déjà assuré", "chez quelqu'un d'autre"]):
        return (
            f"Bienvenue chez **{cfg['entity']}** {country_prep} {cfg['name']} ! 🛡️\n\n"
            f"Nous gérons intégralement la résiliation de votre ancien contrat auprès de votre assureur actuel sans frais ni interruption de garantie.\n"
            f"De plus, nous reprenons 100% de votre Bonus d'ancienneté avec une réduction préférentielle !\n\n"
            f"Souhaitez-vous découvrir votre tarif avec votre bonus conservé ?\n\n"
            f"[📊 Calculer mon tarif avec Bonus]  [📄 Scanner ma Carte Grise]"
        )

    # Default Dynamic Orientation Response
    return (
        f"Chez **{cfg['entity']}** {country_prep} {cfg['name']}, nous proposons 3 niveaux de protection :\n"
        f"1️⃣ **{p1['name']}**\n"
        f"2️⃣ **{p2['name']}**\n"
        f"3️⃣ **{p3['name']}**\n\n"
        f"Quelle formule souhaitez-vous découvrir ?\n\n"
        f"[{p1['name']}]  [{p3['name']}]  [📊 Obtenir mon tarif personnalisé]"
    )
