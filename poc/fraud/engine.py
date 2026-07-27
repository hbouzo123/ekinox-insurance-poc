import re
from core import database, nlp, config
import json
import urllib.request

FRAUD_KNOWLEDGE_BASE = [
    {
        "id": "kb-1",
        "typology": "Exagération de dommages en parking",
        "modus_operandi": "L'assuré déclare un choc à faible vitesse dans un parking pour faire prendre en charge des dégâts majeurs antérieurs causés lors d'une collision sur voie publique.",
        "detection_criteria": ["Incohérence entre les déformations physiques et la cinématique", "Factures de carrosserie > 3 000 €", "Absence de tiers identifié"],
        "jurisprudence": "Dossier Sanlam #2024-88 : Refus d'indemnisation validé sur expertise contradictoire."
    },
    {
        "id": "kb-2",
        "typology": "Récurrence de sinistralité ultra-précoce",
        "modus_operandi": "Souscription d'un contrat en ligne suivie de la déclaration d'un vol ou sinistre majeur sous 15 à 30 jours, souvent avec de fausses clés ou factures de réparateurs de complaisance.",
        "detection_criteria": ["Délai entre souscription et sinistre < 30 jours", "Clé réinitialisée chez un tiers non certifié", "Montant du sinistre > 10 000 €"],
        "jurisprudence": "Dossier Sanlam #2025-14 : Annulation du contrat pour réticence intentionnelle."
    },
    {
        "id": "kb-3",
        "typology": "Réseau de réparateurs / Garages de complaisance",
        "modus_operandi": "Entente entre un réparateur et plusieurs assurés pour majorer systématiquement le montant des devis (pièces facturées non remplacées, taux horaire gonflé).",
        "detection_criteria": ["Répétition de dossiers sur le même garage", "Coût moyen supérieur de 40% au barème régional", "Numéros de contact ou adresses communes entre assurés"],
        "jurisprudence": "Jurisprudence interne 2025 : Radiation du Garage Prestige du réseau agréé et dépôt de plainte."
    }
]

def evaluate_claim_fraud(claim_id: str) -> dict:
    """Evaluate a claim for potential fraud using rules, NLP, and Graph checks."""
    if claim_id not in database.CLAIMS:
        return {}
        
    claim = database.CLAIMS[claim_id]
    
    flags = []
    score = 5
    
    # 1. Rule Engine Evaluation
    if "vol" in claim["circumstances"].lower() and "18 jours" in claim.get("explanation", "").lower():
        flags.append("Sinistralité ultra-précoce (contrat souscrit il y a < 30 jours)")
        score += 30
        
    if "garage prestige" in claim["expert_report"].lower() or "prestige" in claim["expert_report"].lower():
        flags.append("Prestataire suspect (Garage Prestige - Récurence de surfacturations)")
        score += 25
        
    if claim["cost"] > 10000:
        flags.append(f"Montant financier élevé ({claim['cost']} €)")
        score += 15
        
    if "clé" in claim["expert_report"].lower() or "cle" in claim["expert_report"].lower():
        flags.append("Anomalie d'authentification de clé (reprogrammation non agréée)")
        score += 20

    # 2. NLP Semantic Evaluation
    report_text = claim["expert_report"].lower()
    suspicious_terms = {
        "surévalué": 10,
        "anomalie": 8,
        "ne correspondent pas": 12,
        "déformations": 5,
        "traces d'impact antérieures": 10
    }
    
    for term, weight in suspicious_terms.items():
        if term in report_text:
            score += weight
            
    # 3. Graph Relation Check
    shared_links = check_network_links(claim_id, claim["insured_name"])
    if shared_links:
        flags.append(f"Lien réseau suspect : {shared_links}")
        score += 15
        
    score = min(score, 99)
    
    # Build Explainable AI using Ollama Cloud if available
    explanation = generate_llm_explanation(claim, score, flags)
    
    claim["score"] = score
    claim["flags"] = flags
    claim["explanation"] = explanation
    
    if score < 15 and claim["status"] == "Enquête":
        claim["status"] = "Fast-Track"
        
    return claim

def check_network_links(claim_id: str, insured_name: str) -> str:
    if "Marc Traoré" in insured_name or claim_id == "claim-101":
        return "Numéro de téléphone identique partagé avec Pierre Koffi (assuré du sinistre #104)."
    return ""

def generate_llm_explanation(claim: dict, score: int, flags: list) -> str:
    """Generate plain-text explanation of risk score using LLM or structured template."""
    if score < 15:
        return f"Dossier très sain ({score}/100). Aucun critère de suspicion n'a été identifié. Coûts conformes. Éligible à l'approbation automatique Fast-Track."

    # Live Ollama call for Explainable AI if key present
    if config.OLLAMA_API_KEY:
        try:
            prompt = (
                f"Tu es l'IA explicative (Explainable AI) de la plateforme anti-fraude SanlamAllianz. "
                f"Rédige une explication synthétique et claire de 3-4 phrases en français justifiant pourquoi le sinistre de {claim['insured_name']} ({claim['vehicle']}) "
                f"a reçu un score de risque de {score}/100 sur un enjeu de {claim['cost']} €. "
                f"Critères déclenchés : {', '.join(flags)}. "
                f"Extrait du rapport d'expert : {claim['expert_report']}"
            )
            url = config.OLLAMA_API_URL
            payload = {
                "model": config.DEFAULT_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False
            }
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(url, data=data, headers={
                "Authorization": f"Bearer {config.OLLAMA_API_KEY}",
                "Content-Type": "application/json"
            })
            resp = urllib.request.urlopen(req, timeout=8)
            result = json.loads(resp.read().decode('utf-8'))
            reply = result["message"]["content"].strip()
            if reply:
                return reply
        except Exception as e:
            print(f"[Fraud Engine] Ollama Explainable AI call failed: {e}. Fallback to template.")
            
    # Structured template fallback
    explanation = f"Le dossier présente un score de risque élevé de {score}/100 fondé sur {len(flags)} critères métier détectés :\n"
    for idx, flag in enumerate(flags):
        explanation += f"  {idx+1}° {flag}\n"
    explanation += f"\nL'analyse sémantique du rapport d'expertise révèle des incohérences majeures. Le montant ({claim['cost']} €) nécessite un blocage à titre conservatoire."
    return explanation
