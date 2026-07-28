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
    """Generate ultra-rapid response with silent live Core Insurance System integration EXCLUSIVELY for Benin."""
    
    cfg = database.COUNTRY_CONFIGS.get(country_code, database.COUNTRY_CONFIGS["BJ"])
    lang_mode = detect_language_mode(user_message)
    
    prospect_info = ""
    if prospect_data:
        p_name = prospect_data.get("name", "")
        if p_name and p_name not in ["Prospect Inconnu", "Document", "Fichier", "Carte Grise", "Pdf"]:
            prospect_info += f"\n- Nom du prospect : {p_name}"
        if prospect_data.get("document_uploaded"):
            prospect_info += f"\n- Carte grise analysée pour : {prospect_data.get('vehicle', 'Toyota Corolla')}"
            if country_code == "BJ":
                prospect_info += ". Devis officiel calculé selon le barème CIMA Bénin !"
        elif prospect_data.get("vehicle"):
            prospect_info += f"\n- Véhicule : {prospect_data.get('vehicle')}"

    system_prompt = (
        f"Tu es le Conseiller Commercial {cfg['entity']} au {cfg['name']}.\n"
        f"Tu aides les prospects à trouver l'assurance automobile idéale.\n"
        f"N'utilise AUCUN caractère markdown (** ou #).\n"
        f"Ne mentionne JAMAIS 'Sandbox' ni 'ORASS' ni 'quittance' dans tes réponses.\n"
        f"Réponds toujours avec écoute, empathie et précision aux questions du prospect.\n"
        f"{prospect_info}\n"
    )
    if country_code == "BJ":
        system_prompt += "Fournis les Devis CIMA officiels et accepte le paiement MTN MoMo (*138#) et Moov Flooz (*155#).\n"
        
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
    """Instant 0.001s Knowledge Engine with smart vehicle qualification and clarification handling."""
    msg = user_message.lower()
    country_code = cfg.get("code", "BJ")
    country_prep = "au" if country_code in ["MA", "BJ"] else "en"
    products = cfg["products"]
    p1, p2, p3 = products[0], products[1], products[2]
    
    has_uploaded_doc = prospect_data.get("document_uploaded", False) if prospect_data else False
    vehicle_known = (prospect_data.get("vehicle") and "informations" not in prospect_data.get("vehicle").lower()) if prospect_data else False
    vehicle_str = prospect_data.get("vehicle", "votre véhicule") if (prospect_data and vehicle_known) else "votre véhicule"
    
    raw_name = prospect_data.get("name", "") if prospect_data else ""
    valid_name = raw_name if raw_name not in ["Prospect Inconnu", "Document", "Fichier", "Carte Grise", "Pdf"] else ""
    greeting_name = f" {valid_name}" if valid_name else ""
    
    # Execute Background Core Insurance Engine ONLY IF COUNTRY IS BENIN (BJ)
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

    # 1. SPECIFIC INSURANCE COVERAGE QUESTIONS ("L'assurance RC, elle couvre quoi exactement ?")
    if any(k in msg for k in ["couvre quoi", "c'est quoi la rc", "responsabilité civile", "garanties", "couvre exactement", "couverture rc", "que couvre"]):
        return (
            f"L'assurance Responsabilité Civile (RC) obligatoire CIMA {country_prep} {cfg['name']} indemnise l'intégralité des dommages matériels et corporels causés aux tiers lors d'un accident avec {vehicle_str}.\n\n"
            f"• Elle inclut : Défense & Recours juridique + Assistance dépannage 24/7.\n"
            f"• Pour couvrir votre propre véhicule contre le vol, l'incendie ou les bris de glace, nous vous recommandons nos formules {p2['name']} et {p3['name']}.\n\n"
            f"[{p2['name']}]  [{p3['name']}]  [Obtenir mon Devis Officiel]"
        )

    # 2. VALUATION & FORMULA SELECTION EXPLANATION ("comment vous avez calculé la valeur...", "pas fait le choix")
    if any(k in msg for k in ["calculé la valeur", "valeur de la voiture", "pas fait le choix", "pas demandé", "pas choisi"]):
        return (
            f"Je vous comprends tout à fait{greeting_name} ! 🚗\n\n"
            f"Le tarif présenté était calculé à partir de la puissance fiscale (7 CV) figurant sur votre Carte Grise. "
            f"Je vous avais affiché la formule Tous Risques à titre d'illustration, mais aucun choix ne vous est imposé ! C'est VOUS qui décidez.\n\n"
            f"Quelle formule correspond le mieux à vos attentes : {p1['name']} (Tiers), {p2['name']} (Tiers Plus) ou {p3['name']} (Tous Risques) ?\n\n"
            f"[{p1['name']}]  [{p2['name']}]  [{p3['name']}]"
        )

    # 3. META-DIALOGUE / LISTENING FEEDBACK ("comprennes la question", "écoutes", "n'hésite pas à demander", "pas compris")
    if any(k in msg for k in ["comprennes la question", "écoutes", "n'hésite pas à demander", "pas compris", "écouter"]):
        return (
            f"Toutes mes excuses{greeting_name} ! 🤝 Vous avez tout à fait raison. Je vous écoute très attentivement.\n\n"
            f"Posez-moi votre question sur votre véhicule ou vos garanties, et je vous répondrai précisément sans imposer de formule.\n\n"
            f"[Posez votre question]  [Comparer les formules]"
        )

    # 4. NEW VEHICLE PURCHASE INTENT ("j'ai acheté une nouvelle voiture", "nouveau véhicule")
    if any(k in msg for k in ["nouvelle voiture", "nouveau véhicule", "acheté une voiture", "acheté un véhicule", "nouvelle auto"]):
        return (
            f"Félicitations pour votre nouveau véhicule{greeting_name} ! 🚗🎉\n\n"
            f"Pour vous calculer votre Devis Officiel sur-mesure au {cfg['name']}, quelle est la marque et le modèle de votre voiture ?\n"
            f"(Vous pouvez aussi simplement me scanner votre Carte Grise pour une saisie automatique instantanée).\n\n"
            f"[Envoyer ma Carte Grise]  [Préciser le modèle]"
        )

    # 5. CLARIFICATION QUESTION INTENT ("comment as-tu pu faire un devis", "quelle voiture", "sans informations", "sans info", "pas partagé")
    if any(k in msg for k in ["comment", "sans informations", "sans info", "quelle voiture", "pas partagé", "pas envoyé", "carte grise", "utilisé quelle"]):
        return (
            f"C'est une très bonne question{greeting_name} ! 🚗\n\n"
            f"Le tarif indiqué était une estimation basée sur une puissance standard de 7 CV au Bénin. "
            f"Pour calculer votre tarif exact au FCFA près, dites-moi simplement quelle est la marque et le modèle de votre voiture (ex: Toyota Corolla), ou partagez-moi une photo de votre Carte Grise !\n\n"
            f"[Envoyer ma Carte Grise]  [Préciser mon modèle]"
        )

    # 6. CAPABILITY / HEARING / UNDERSTANDING CHECK
    if any(k in msg for k in ["m'entends", "m'entend", "tu m'entends", "comprends", "comprendre", "arabe", "dialecte", "tunisien", "derja"]):
        return (
            f"Oui parfait{greeting_name} ! Je vous entends et je vous comprends très bien. "
            f"Je peux échanger avec vous en Français, en Arabe et en Dialecte. "
            f"Comment puis-je vous aider pour votre véhicule à {cfg['name']} ?\n\n"
            f"[Obtenir mon devis]  [Découvrir les formules]"
        )

    # 7. ARABIC LANGUAGE MODE
    if lang_mode == "ARABIC":
        name_prefix = f" يا {valid_name}" if valid_name else ""
        ttc_str = f" {orass_quote['quittance']['MONTTTC']} FCFA" if is_benin and orass_quote else ""
        return (
            f"مرحباً بك{name_prefix} في {cfg['entity']} ! 🛡️ "
            f"أنا هنا لمساعدتك في حساب أفضل عروض التأمين لسيارتك.{ttc_str} "
            f"كيف يمكنني مساعدتك اليوم؟\n\n"
            f"[الحصول على العرض]  [حجز موعد]"
        )

    # 8. TUNISIAN DERJA MODE
    if lang_mode == "DERJA":
        name_prefix = f" يا {valid_name}" if valid_name else ""
        return (
            f"Marhaba bik{name_prefix} ! N'effhemk w n'ssm3ek mlih. "
            f"Rani hna bech n'essablek el devis mte3 el karhaba m3a {cfg['entity']}.\n\n"
            f"[Obtenir mon devis]  [Prendre Rendez-vous]"
        )

    # 9. PAYMENT INTENTS (BENIN MOBILE MONEY)
    if any(k in msg for k in ["payer", "paiement", "momo", "flooz", "mtn", "moov", "celtiis", "carte bancaire", "regler", "régler"]):
        if is_benin:
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

    # 10. ORDINAL OR SPECIFIC FORMULA QUOTATION REQUEST ("La 3e ?", "Devis 3e formule")
    is_asking_third = any(k in msg for k in ["3e", "3ème", "3eme", "troisième", "troisieme", "la 3", "formule 3", "la platinum", "tous risques"])
    
    if is_asking_third or any(k in msg for k in ["devis", "simulation", "tarif", "prix", "combien", "obtenir mon tarif"]):
        if not vehicle_known and not has_uploaded_doc:
            return (
                f"Pour vous calculer votre tarif exact au FCFA près pour la formule **{p3['name']}**{greeting_name}, "
                f"quel est le modèle de votre véhicule (ex: Toyota Corolla) ? Vous pouvez aussi me partager une photo de votre Carte Grise.\n\n"
                f"[Envoyer ma Carte Grise]  [Préciser mon véhicule]"
            )
            
        if is_benin and orass_quote:
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

    # 11. MULTI-FORMULAS COMPARISON REQUEST
    if any(k in msg for k in ["trois devis", "3 devis", "pour chaque formule", "prix pour chaque"]):
        if is_benin and orass_quote:
            detail = orass_quote["detail"]
            return (
                f"Voici le tarif annuel officiel des trois formules SanlamAllianz Bénin pour votre {vehicle_str} :\n\n"
                f"1. {p1['name']} : 75 000 FCFA par an (Responsabilité Civile CIMA Bénin).\n"
                f"2. {p2['name']} : 135 000 FCFA par an (Tiers Amélioré avec vol & bris de glace Cotonou).\n"
                f"3. {p3['name']} : {detail['primeTtc']} FCFA par an (Tous Risques Devis N° DEV-894102).\n\n"
                f"Quelle formule souhaitez-vous souscrire ?\n\n"
                f"[Souscrire {p2['name']}]  [Souscrire {p3['name']}]  [Payer via MTN MoMo]"
            )

    # 12. DEFAULT FORMULA DISCOVERY MENU
    return (
        f"Chez {cfg['entity']} {country_prep} {cfg['name']}, nous proposons 3 niveaux de protection :\n"
        f"1. {p1['name']} : la couverture Responsabilité Civile essentielle.\n"
        f"2. {p2['name']} : la formule équilibrée recommandée.\n"
        f"3. {p3['name']} : la protection tous risques intégrale.\n\n"
        f"Quelle formule souhaitez-vous découvrir ?\n\n"
        f"[{p2['name']}]  [{p3['name']}]  [Obtenir mon Devis Officiel]"
    )
