import re

class IntentRouter:
    """
    Hybrid Architecture:
    1. Intent Classification & Journey Routing
    2. High-confidence Structured Journeys (Devis, Payment, Policy, Appointment, Assumptions, City/Zone)
    3. Low-confidence or Open Dialogue -> Full LLM Conversational Intelligence
    """

    @staticmethod
    def classify_intent(message_text: str, prospect_data: dict = None) -> dict:
        text = message_text.strip()
        msg_lower = text.lower()
        
        has_doc = prospect_data.get("document_uploaded", False) if prospect_data else False
        vehicle_known = bool(prospect_data.get("vehicle") and "informations" not in prospect_data.get("vehicle").lower()) if prospect_data else False

        # 0. Initial Greeting & Identity Presentation Intent
        if any(k in msg_lower for k in ["bonjour", "salut", "coucou", "hello", "présenter", "presenter", "qui es-tu", "comment t'appelles-tu"]):
            return {
                "route": "JOURNEY",
                "intent": "WELCOME_PRESENTATION",
                "confidence": 0.95,
                "reason": "Initial greeting & mutual presentation"
            }

        # 1. Assumption Adjustment Intent ("modifier les hypothèses", "changer la ville", "changer la valeur")
        if any(k in msg_lower for k in ["hypothèse", "hypothese", "modifier la ville", "changer la ville", "modifier la valeur", "changer la valeur", "changer sinistre", "ajuster le devis"]):
            return {
                "route": "JOURNEY",
                "intent": "ADJUST_ASSUMPTIONS",
                "confidence": 0.95,
                "reason": "Interactive devis assumption modification"
            }

        # 2. City / Zone Intent (Parakou, Cotonou, Natitingou, Bohicon, Djougou, Porto-Novo, Calavi)
        if any(k in msg_lower for k in ["parakou", "cotonou", "natitingou", "bohicon", "djougou", "porto-novo", "calavi"]):
            return {
                "route": "JOURNEY",
                "intent": "CITY_ZONE_SELECTION",
                "confidence": 0.90,
                "reason": "City & zone geographical selection"
            }

        # 3. Mobile Money Payment (Benin / Local)
        if any(k in msg_lower for k in ["payer", "paiement", "momo", "flooz", "mtn", "moov", "celtiis", "carte bancaire", "regler", "régler"]):
            return {
                "route": "JOURNEY",
                "intent": "PAYMENT",
                "confidence": 0.95,
                "reason": "Explicit payment request"
            }

        # 4. Human Advisor Validation Trigger
        if any(k in msg_lower for k in ["émettre la police", "emettre la police", "valider la police", "confirmer la souscription", "souscrire maintenant", "valider le devis"]):
            return {
                "route": "JOURNEY",
                "intent": "HUMAN_ADVISOR_VALIDATION",
                "confidence": 0.95,
                "reason": "Human advisor validation trigger"
            }

        # 5. Appointment Scheduling
        if any(k in msg_lower for k in ["rendez-vous", "rdv", "rappeler", "appel conseiller", "rencontrer", "agence"]):
            return {
                "route": "JOURNEY",
                "intent": "APPOINTMENT",
                "confidence": 0.90,
                "reason": "Explicit appointment request"
            }

        # 6. Document Upload / OCR Carte Grise
        if any(k in msg_lower for k in ["carte grise", "scan", "scanner", "envoyer photo", "justificatif"]):
            return {
                "route": "JOURNEY",
                "intent": "OCR_CARTE_GRISE",
                "confidence": 0.90,
                "reason": "Explicit document / carte grise request"
            }

        # 7. Quotation / Tarif Request
        is_asking_tariff = any(k in msg_lower for k in ["3e", "3ème", "3eme", "troisième", "la 3", "formule 3", "obtenir mon devis", "calculer devis", "tarif personnalisé", "combien coûte"])
        if is_asking_tariff:
            return {
                "route": "JOURNEY",
                "intent": "DEVIS_CALCULATION",
                "confidence": 0.90 if (has_doc or vehicle_known) else 0.70,
                "needs_slot": not (has_doc or vehicle_known),
                "reason": "Tariff calculation request"
            }

        # 8. Open Dialogue & Reasoning -> Directed to LLM Engine
        return {
            "route": "LLM_INTELLIGENCE",
            "intent": "OPEN_CONVERSATION",
            "confidence": 0.85,
            "reason": "Open question, advice, or general conversation -> LLM reasoning"
        }
