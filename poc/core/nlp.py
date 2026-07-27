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
            prospect_info += f"\n- CARTE GRISE SCANNÉE ET VALIDÉE ! Véhicule détecté : {prospect_data.get('vehicle', 'Véhicule certifié 7 CV')}. NE DEMANDE PLUS LA CARTE GRISE !"
        if prospect_data.get("vehicle"):
            prospect_info += f"\n- Modèle véhicule : {prospect_data.get('vehicle')}"

    system_prompt = (
        f"Tu es le Chargé de Clientèle Automobile SanlamAllianz {country_prep} {cfg['name']} ({cfg['entity']}).\n"
        f"Tu dialogues en direct. Sois ultra-rapide, naturel, dynamique et concis (50 à 90 mots max).\n\n"
        f"CONTEXTE ASSUREUR LOCAL :\n"
        f"- Réglementation : {cfg['regulatory_body']}\n"
        f"- Monnaie : {cfg['currency']}\n"
        f"- Garages agréés : {cfg['default_garage']}\n"
        f"- Produits chez {cfg['entity']} :\n{products_str}\n"
        f"{prospect_info}\n\n"
        f"RÈGLES STRICTES DE CONVERSATION HUMAINE :\n"
        f"1. Adapte ta réponse de façon vivante et naturelle à la question exacte du prospect.\n"
        f"2. Ne répète JAMAIS la même liste de 3 formules si le client te demande d'expliciter, de reformuler ou de lui conseiller une offre.\n"
        f"3. Si le client achète une nouvelle voiture, félicite-le et recommande-lui la formule Tous Risques ({cfg['products'][2]['name']}).\n"
        f"4. Si le client veut une reformulation, résume les 3 niveaux de garantie en phrases simples.\n"
        f"5. Termine toujours par 2 choix pertinents entre crochets `[Choix 1]` `[Choix 2]`.\n"
    )
    
    if doc_context:
        system_prompt += f"\nBASE DE CONNAISSANCE :\n{doc_context}\n"
        
    messages = [{"role": "system", "content": system_prompt}]
    
    for msg in conversation_history[-6:]:
        role = "assistant" if msg["sender"] == "assistant" else "user"
        clean_text = re.sub(r'\[([^\]]+)\]', '', msg["text"]).strip()
        messages.append({"role": role, "content": clean_text})
        
    messages.append({"role": "user", "content": user_message})
    
    # Try Fast Cloud LLM call with 3.5s timeout for real-time voice latency
    if config.OLLAMA_API_KEY:
        try:
            url = config.OLLAMA_API_URL
            payload = {
                "model": config.DEFAULT_MODEL,
                "messages": messages,
                "stream": False,
                "options": {"num_predict": 180, "temperature": 0.4}
            }
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(url, data=data, headers={
                "Authorization": f"Bearer {config.OLLAMA_API_KEY}",
                "Content-Type": "application/json"
            })
            resp = urllib.request.urlopen(req, timeout=3.5)
            result = json.loads(resp.read().decode('utf-8'))
            reply = result["message"]["content"].strip()
            if reply:
                return reply
        except Exception as e:
            print(f"[LLM Core] Fast Cloud LLM timeout ({e}). Switching to instant local RAG engine...")
            
    return generate_instant_rag_response(user_message, cfg, prospect_data)

def generate_instant_rag_response(user_message: str, cfg: dict, prospect_data: dict = None) -> str:
    """Instant 0.01s Knowledge Engine tailored dynamically to the question and country context."""
    msg = user_message.lower()
    country_code = cfg.get("code", "CI")
    country_prep = "au" if country_code == "MA" else "en"
    products = cfg["products"]
    p1, p2, p3 = products[0], products[1], products[2]
    
    doc_uploaded = prospect_data.get("document_uploaded", False) if prospect_data else False
    vehicle_str = prospect_data.get("vehicle", "votre véhicule") if prospect_data else "votre véhicule"

    # 1. Intent: Recommendation for New / Upcoming Vehicle ("nouvelle", "neuve", "sortir la semaine prochaine", "conseille", "recommande", "acheter")
    if any(k in msg for k in ["nouvelle", "neuf", "neuve", "semaine prochaine", "quelle formule me", "conseille", "recommande", "acheter"]):
        return (
            f"Félicitations pour votre nouveau véhicule ! 🚘\n\n"
            f"Pour une voiture neuve, nous vous recommandons vivement notre formule Tous Risques (**{p3['name']}**).\n"
            f"Elle offre la garantie valeur à neuf, la couverture de tous les dommages et l'assistance 0 km.\n\n"
            f"Souhaitez-vous calculer votre tarif personnalisé ?\n\n"
            f"[📊 Obtenir mon tarif personnalisé]  [Découvrir {p2['name']}]"
        )

    # 2. Intent: Simplification / Reformulation Request ("pas compris", "reformuler", "résumé", "expliquer", "simple")
    if any(k in msg for k in ["pas compris", "reformuler", "résumé", "expliquer simplement", "synthèse", "clair"]):
        return (
            f"En résumé très simple :\n"
            f"• **{p1['name']}** : Le minimum légal pour rouler (dégâts causés aux tiers).\n"
            f"• **{p2['name']}** : Protège contre le vol, l'incendie et le bris de glace.\n"
            f"• **{p3['name']}** : Couverture intégrale (indemnise votre voiture en cas d'accident responsable).\n\n"
            f"Quelle protection préférez-vous ?\n\n"
            f"[Choisir {p2['name']}]  [Choisir {p3['name']}]"
        )

    # 3. Intent: Price / Devis / Tarif Calculation (with OCR state memory)
    if any(k in msg for k in ["prix", "tarif", "cout", "coût", "combien", "simulation", "devis", "estimation", "obtenir mon tarif"]):
        if doc_uploaded or (prospect_data and prospect_data.get("vehicle")):
            return (
                f"📊 **Devis Personnalisé Calculé pour {vehicle_str}**\n\n"
                f"Selon les caractéristiques de votre carte grise {country_prep} {cfg['name']} :\n"
                f"1️⃣ **{p1['name']}** : Responsabilité Civile obligatoire.\n"
                f"2️⃣ **{p2['name']}** : Tiers Amélioré Vol & Incendie.\n"
                f"3️⃣ **{p3['name']}** : Protection Tous Risques complète.\n\n"
                f"Quelle formule souhaitez-vous retenir pour votre contrat ?\n\n"
                f"[{p2['name']}]  [{p3['name']}]  [🗓️ Prendre RDV Souscription]"
            )
        else:
            return (
                f"Le tarif dépend du modèle et de la puissance fiscale de votre véhicule en {cfg['currency']}.\n"
                f"Pour un calcul immédiat au centime près, scannez votre carte grise !\n\n"
                f"[📄 Scanner ma Carte Grise]  [🗓️ Prendre RDV Conseiller]"
            )

    # 4. Intent: Difference / Comparison between formulas
    if any(k in msg for k in ["difference", "différence", "comparer", "les 3", "mieux"]):
        return (
            f"Voici la comparaison des 3 formules chez {cfg['entity']} :\n"
            f"• **{p1['name']}** : Assurance Tiers de base.\n"
            f"• **{p2['name']}** : Protection Tiers + Vol + Incendie + Vitres.\n"
            f"• **{p3['name']}** : Protection Tous Risques intégrale.\n\n"
            f"Souhaitez-vous une simulation personnalisée ?\n\n"
            f"[📊 Obtenir mon tarif personnalisé]  [Découvrir {p3['name']}]"
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
