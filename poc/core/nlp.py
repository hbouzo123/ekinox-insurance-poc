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
            "content": "Conformément au Code CIMA (Article 13), l'assurance Responsabilité Civile automobile est obligatoire. Notre formule Auto Platinum couvre les dommages tous accidents jusqu'à 50 000 000 FCFA avec assistance 0 km à Abidjan et à l'intérieur du pays. Franchise fixe de 50 000 FCFA.",
            "category": "garantie"
        }
    ],
    "MA": [
        {
            "id": "doc-ma-1",
            "title": "Réglementation ACAPS & Conditions Générales Sanlam Maroc",
            "content": "Sous le contrôle de l'ACAPS, l'offre Assur'Auto Intégrale Sanlam Maroc couvre les dommages tous risques avec l'option exclusive de Rachat de Franchise (0 DH de reste à charge en garage agréé Sanlam à Casablanca/Rabat) et la Garantie Décès Toutes Causes.",
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
        return f"[Source Contractuelle: {best_doc['title']}]\n{best_doc['content']}"
    return ""

def generate_llm_response(conversation_history: list, user_message: str, country_code: str = "CI") -> str:
    """Generate live response from Ollama Cloud API formatted specifically for Option A (WhatsApp Flash)."""
    
    cfg = database.COUNTRY_CONFIGS.get(country_code, database.COUNTRY_CONFIGS["CI"])
    doc_context = search_knowledge_hub(user_message, country_code)
    
    products_str = ", ".join([f"{p['name']} ({p['desc']})" for p in cfg['products']])
    
    system_prompt = (
        f"Tu es l'assistant commercial Assurance Auto SanlamAllianz au/en {cfg['name']}. "
        f"Tu dialogues sur WhatsApp. Monnaie : {cfg['currency']}. Réglementation : {cfg['regulatory_body']}. "
        f"Produits disponibles : {products_str}.\n\n"
        f"### CHARTE UX STRICTE WHATSAPP FLASH :\n"
        f"1. **RÉPONSE ULTRA-COURTE (MAX 100-120 MOTS)** : Élimine la théorie et les explications longues. Va droit à la valeur client.\n"
        f"2. **MISE EN VALEUR DE LA CARTE GRISE** : Si le client a un doute ou veut aller vite, propose-lui d'envoyer la photo de sa carte grise.\n"
        f"3. **ALIGNEMENT STRICT TEXTE ↔ BOUTONS** : Propose toujours 2 ou 3 choix clairs en toute fin de message entre crochets `[Bouton]`. Chaque bouton doit correspondre exactement aux choix mentionnés dans le message.\n\n"
    )
    if doc_context:
        system_prompt += f"CONTEXTE CONTRACTUEL LOCAL :\n{doc_context}\n\n"
        
    messages = [{"role": "system", "content": system_prompt}]
    
    for msg in conversation_history[-6:]:
        role = "assistant" if msg["sender"] == "assistant" else "user"
        messages.append({"role": role, "content": msg["text"]})
        
    messages.append({"role": "user", "content": user_message})
    
    if config.OLLAMA_API_KEY:
        try:
            url = config.OLLAMA_API_URL
            payload = {
                "model": config.DEFAULT_MODEL,
                "messages": messages,
                "stream": False,
                "options": {"temperature": 0.3, "top_p": 0.9}
            }
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(url, data=data, headers={
                "Authorization": f"Bearer {config.OLLAMA_API_KEY}",
                "Content-Type": "application/json"
            })
            resp = urllib.request.urlopen(req, timeout=10)
            result = json.loads(resp.read().decode('utf-8'))
            reply = result["message"]["content"].strip()
            if reply:
                return reply
        except Exception as e:
            print(f"[LLM Core] Ollama Primary failed: {e}. Trying fallback...")
            try:
                payload["model"] = config.FALLBACK_MODEL
                data = json.dumps(payload).encode('utf-8')
                req = urllib.request.Request(url, data=data, headers={
                    "Authorization": f"Bearer {config.OLLAMA_API_KEY}",
                    "Content-Type": "application/json"
                })
                resp = urllib.request.urlopen(req, timeout=10)
                result = json.loads(resp.read().decode('utf-8'))
                reply = result["message"]["content"].strip()
                if reply:
                    return reply
            except Exception as e2:
                print(f"[LLM Core] Fallback failed: {e2}")
                
    return generate_simulated_response(conversation_history, user_message, cfg)

def generate_simulated_response(history: list, user_message: str, cfg: dict) -> str:
    msg = user_message.lower()
    if "bonjour" in msg or "salut" in msg or "salam" in msg:
        return (
            f"Bonjour ! 👋 Je suis votre assistant Assurance Auto SanlamAllianz.\n\n"
            f"Je peux calculer votre tarif en 2 minutes ou analyser votre carte grise par photo.\n\n"
            f"Que souhaitez-vous faire ?\n\n"
            f"[📊 Faire une simulation rapide]  [📄 Envoyer ma Carte Grise]  [🗓️ Prendre RDV / Être rappelé]"
        )
    return (
        f"Merci ! Chez {cfg['entity']}, nous vous proposons des formules adaptées en {cfg['currency']}.\n\n"
        f"Que préférez-vous ?\n\n"
        f"[📊 Obtenir mon Devis]  [📄 Envoyer ma Carte Grise]"
    )
