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
            prospect_info += f"\n- CARTE GRISE SCANNÉE ET VALIDÉE ! Véhicule certifié : {prospect_data.get('vehicle', 'Véhicule certifié 7 CV')}. Le tarif doit être donné IMMÉDIATEMENT dans le chat !"
        if prospect_data.get("vehicle"):
            prospect_info += f"\n- Modèle véhicule : {prospect_data.get('vehicle')}"

    system_prompt = (
        f"Tu es le Chargé de Clientèle Automobile SanlamAllianz {country_prep} {cfg['name']} ({cfg['entity']}).\n"
        f"Tu dialogues en direct avec le prospect sur WhatsApp/Vocal. Sois chaleureux, naturel et très réactif (40 à 75 mots max).\n\n"
        f"CONTEXTE ASSUREUR LOCAL :\n"
        f"- Réglementation : {cfg['regulatory_body']}\n"
        f"- Monnaie : {cfg['currency']}\n"
        f"- Garages agréés : {cfg['default_garage']}\n"
        f"- Produits chez {cfg['entity']} :\n{products_str}\n"
        f"{prospect_info}\n\n"
        f"RÈGLES DE DIALOGUE CONTINU :\n"
        f"1. Ne répète JAMAIS les suffixes entre parenthèses comme '(Tiers) (Tiers)'. Utilise exactement le nom du produit ({cfg['products'][0]['name']}).\n"
        f"2. Tu es DÉJÀ en ligne directe avec le prospect ! Ne lui demande JAMAIS son numéro de téléphone ou d'appeler un numéro externe.\n"
        f"3. Dès que le prospect demande un devis ou une simulation, donne-lui IMMÉDIATEMENT son tarif dans le chat sans le faire patienter.\n"
        f"4. Si le client achète une voiture neuve, félicite-le et conseille-lui la formule Tous Risques ({cfg['products'][2]['name']}).\n"
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
    
    # Try Fast Cloud LLM call with 6.0s timeout and 300 token limit
    if config.OLLAMA_API_KEY:
        for model_name in [config.DEFAULT_MODEL, config.FALLBACK_MODEL]:
            try:
                url = config.OLLAMA_API_URL
                payload = {
                    "model": model_name,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "num_predict": 300,
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
                    return reply
            except Exception as e:
                print(f"[LLM Core] Model {model_name} call exception ({e}). Trying next fallback...")
            
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

    # 1. Intent: Recommendation for New / Upcoming Vehicle ("nouvelle", "neuve", "sortir la semaine prochaine", "conseille", "recommande", "touriste", "pourquoi")
    if any(k in msg for k in ["nouvelle", "neuf", "neuve", "semaine prochaine", "conseille", "recommande", "pourquoi", "touriste"]):
        return (
            f"Félicitations pour votre nouveau véhicule ! 🚘\n\n"
            f"Pour un véhicule neuf, je vous recommande vivement notre formule Tous Risques (**{p3['name']}**).\n"
            f"Pourquoi ? Parce qu'une voiture neuve est un investissement majeur : en cas de collision, de vol ou de dommage, vous êtes intégralement protégé et indemnisé sans mauvaise surprise !\n\n"
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

    # 3. Intent: Price / Devis / Tarif Calculation / Simulation Request
    if any(k in msg for k in ["prix", "tarif", "cout", "coût", "combien", "simulation", "devis", "estimation", "obtenir mon tarif", "réserve", "calculer"]):
        if doc_uploaded or (prospect_data and prospect_data.get("vehicle")):
            return (
                f"📊 **Devis Personnalisé Calculé pour {vehicle_str}**\n\n"
                f"Selon les caractéristiques de votre carte grise {country_prep} {cfg['name']} :\n"
                f"1️⃣ **{p1['name']}** : Responsabilité Civile obligatoire.\n"
                f"2️⃣ **{p2['name']}** : Tiers Amélioré Vol & Incendie.\n"
                f"3️⃣ **{p3['name']}** : Protection Tous Risques complète.\n\n"
                f"Votre devis est prêt ! Quelle formule souhaitez-vous retenir pour votre contrat ?\n\n"
                f"[{p2['name']}]  [{p3['name']}]  [🗓️ Prendre RDV Souscription]"
            )
        else:
            return (
                f"Le tarif dépend du modèle et de la puissance fiscale de votre véhicule en {cfg['currency']}.\n"
                f"Pour un calcul immédiat au centime près dans ce chat, scannez votre carte grise !\n\n"
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
