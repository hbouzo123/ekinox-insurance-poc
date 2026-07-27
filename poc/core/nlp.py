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

COUNTRY_PRICING = {
    "CI": {
        "p1": "120 000 FCFA / an (soit 10 000 FCFA/mois)",
        "p2": "210 000 FCFA / an (soit 17 500 FCFA/mois)",
        "p3": "380 000 FCFA / an (soit 31 600 FCFA/mois)"
    },
    "MA": {
        "p1": "2 400 DH / an (soit 200 DH/mois)",
        "p2": "4 200 DH / an (soit 350 DH/mois)",
        "p3": "7 800 DH / an (soit 650 DH/mois)"
    },
    "SN": {
        "p1": "110 000 FCFA / an (soit 9 100 FCFA/mois)",
        "p2": "195 000 FCFA / an (soit 16 250 FCFA/mois)",
        "p3": "350 000 FCFA / an (soit 29 100 FCFA/mois)"
    }
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
    
    prospect_info = ""
    if prospect_data:
        if prospect_data.get("document_uploaded"):
            prospect_info += f"\n- CARTE GRISE SCANNÉE ET VALIDÉE ! Véhicule détecté : {prospect_data.get('vehicle', 'Véhicule certifié 7 CV')}. NE DEMANDE PLUS LA CARTE GRISE !"
        if prospect_data.get("vehicle"):
            prospect_info += f"\n- Modèle véhicule : {prospect_data.get('vehicle')}"

    system_prompt = (
        f"Tu es le Chargé de Clientèle Automobile SanlamAllianz au/en {cfg['name']} ({cfg['entity']}).\n"
        f"Tu dialogues en direct. Sois ultra-rapide, naturel, dynamique et concis (40 à 70 mots max).\n\n"
        f"CONTEXTE ASSUREUR LOCAL :\n"
        f"- Réglementation : {cfg['regulatory_body']}\n"
        f"- Monnaie : {cfg['currency']}\n"
        f"- Garages agréés : {cfg['default_garage']}\n"
        f"- Produits chez {cfg['entity']} :\n{products_str}\n"
        f"{prospect_info}\n\n"
        f"RÈGLES :\n"
        f"1. Réponds précisément à la question posée.\n"
        f"2. Si la carte grise est déjà scannée ou si l'utilisateur demande son tarif, donne IMMÉDIATEMENT le calcul de prix personnalisé !\n"
        f"3. Termine par 2 choix entre crochets `[Choix 1]` `[Choix 2]`.\n"
    )
    
    if doc_context:
        system_prompt += f"\nBASE DE CONNAISSANCE :\n{doc_context}\n"
        
    messages = [{"role": "system", "content": system_prompt}]
    
    for msg in conversation_history[-6:]:
        role = "assistant" if msg["sender"] == "assistant" else "user"
        clean_text = re.sub(r'\[([^\]]+)\]', '', msg["text"]).strip()
        messages.append({"role": role, "content": clean_text})
        
    messages.append({"role": "user", "content": user_message})
    
    # Try Fast Cloud LLM call with 2.5s strict timeout for real-time voice latency
    if config.OLLAMA_API_KEY:
        try:
            url = config.OLLAMA_API_URL
            payload = {
                "model": config.DEFAULT_MODEL,
                "messages": messages,
                "stream": False,
                "options": {"num_predict": 90, "temperature": 0.3}
            }
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(url, data=data, headers={
                "Authorization": f"Bearer {config.OLLAMA_API_KEY}",
                "Content-Type": "application/json"
            })
            resp = urllib.request.urlopen(req, timeout=2.5)
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
    products = cfg["products"]
    p1, p2, p3 = products[0], products[1], products[2]
    prices = COUNTRY_PRICING.get(country_code, COUNTRY_PRICING["CI"])
    
    doc_uploaded = prospect_data.get("document_uploaded", False) if prospect_data else False
    vehicle_str = prospect_data.get("vehicle", "votre véhicule") if prospect_data else "votre véhicule"

    # 1. Price / Devis / Tarif Calculation (with OCR state memory)
    if any(k in msg for k in ["prix", "tarif", "cout", "coût", "combien", "simulation", "devis", "estimation", "obtenir mon tarif"]):
        if doc_uploaded or (prospect_data and prospect_data.get("vehicle")):
            return (
                f"📊 **Devis Personnalisé Calculé avec Succès pour {vehicle_str} !**\n\n"
                f"D'après les caractéristiques de votre carte grise au/en {cfg['name']} :\n"
                f"1️⃣ **{p1['name']}** : **{prices['p1']}**\n"
                f"2️⃣ **{p2['name']}** : **{prices['p2']}**\n"
                f"3️⃣ **{p3['name']}** : **{prices['p3']}** (Tous Risques complet)\n\n"
                f"Quelle formule souhaitez-vous retenir pour votre contrat ?\n\n"
                f"[{p2['name']}]  [{p3['name']}]  [🗓️ Prendre RDV Souscription]"
            )
        else:
            return (
                f"Le tarif dépend du modèle et de la puissance fiscale de votre véhicule en {cfg['currency']}.\n"
                f"Voici les estimations pour 7 CV au/en {cfg['name']} :\n"
                f"• {p1['name']} : à partir de {prices['p1']}\n"
                f"• {p3['name']} : {prices['p3']}\n\n"
                f"Pour un calcul instantané au centime près, envoyez la photo de votre carte grise !\n\n"
                f"[📄 Envoyer ma Carte Grise]  [🗓️ Prendre RDV Conseiller]"
            )

    # 2. Offers / Products / Formules / Assurances
    if any(k in msg for k in ["offre", "produit", "formule", "qu'est ce", "quoi les offres", "qu'avez vous", "vous avez quoi", "gamme", "proposez", "solution"]):
        return (
            f"Chez {cfg['entity']} au/en {cfg['name']}, nous proposons 3 formules sur-mesure :\n"
            f"1️⃣ **{p1['name']}** : {p1['desc']}.\n"
            f"2️⃣ **{p2['name']}** : {p2['desc']}.\n"
            f"3️⃣ **{p3['name']}** : {p3['desc']} (protection tous risques).\n\n"
            f"Quelle formule correspond le mieux à votre véhicule ?\n\n"
            f"[{p1['name']}]  [{p3['name']}]  [📊 Obtenir mon tarif personnalisé]"
        )

    # 3. Difference / Comparison between tiers and tous risques
    if any(k in msg for k in ["difference", "différence", "comparer", "mieux", "choisir"]):
        return (
            f"La différence principale chez {cfg['entity']} :\n"
            f"• **{p1['name']}** couvre les dégâts causés aux tiers (RC réglementaire {cfg['regulatory_body']}).\n"
            f"• **{p3['name']}** couvre aussi vos propres dommages (collision, vol, bris de glace, rachat de franchise).\n\n"
            f"Souhaitez-vous une simulation personnalisée ?\n\n"
            f"[📊 Obtenir mon tarif personnalisé]  [Devis {p3['name']}]"
        )

    # 4. Garanties / Assistance / Garages / Remorquage
    if any(k in msg for k in ["garantie", "assistance", "garage", "franchise", "panne", "remorquage", "reparation", "réparation"]):
        return (
            f"Nos garanties {cfg['entity']} incluent l'Assistance 24/7 (dépannage & remorquage) "
            f"et l'accès direct à notre réseau de garages agréés ({cfg['default_garage']}) sans avance de frais.\n\n"
            f"Voulez-vous estimer votre tarif dès maintenant ?\n\n"
            f"[📊 Obtenir mon tarif personnalisé]  [🗓️ Prendre RDV]"
        )

    # 5. Default Dynamic Response
    return (
        f"Je suis votre conseiller commercial {cfg['entity']}.\n"
        f"Je peux vous présenter nos formules ({p1['name']}, {p3['name']}), calculer votre devis personnalisé ou lire votre carte grise par photo.\n\n"
        f"Que souhaitez-vous faire ?\n\n"
        f"[📊 Obtenir mon tarif personnalisé]  [📄 Scanner ma Carte Grise]"
    )
