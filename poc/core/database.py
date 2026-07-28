# Country-Specific Catalogs & Localizations for SanlamAllianz

COUNTRY_CONFIGS = {
    "BJ": {
        "code": "BJ",
        "name": "Bénin",
        "flag": "🇧🇯",
        "entity": "SanlamAllianz Bénin",
        "currency": "FCFA",
        "currency_symbol": "FCFA",
        "regulatory_body": "Code CIMA Bénin & ARCA",
        "products": [
            {"id": "bj-p1", "name": "Auto Classique (Tiers)", "desc": "Responsabilité Civile obligatoire CIMA Bénin + Défense Recours", "recommended_for": "Occasion"},
            {"id": "bj-p2", "name": "Auto Zen (Tiers Amélioré)", "desc": "Tiers + Vol + Incendie + Bris de glace avec assistance Cotonou/Porto-Novo", "recommended_for": "Usage quotidien"},
            {"id": "bj-p3", "name": "Auto Platinum (Tous Risques)", "desc": "Couverture intégrale 0 km, dommages tous accidents et véhicule de remplacement", "recommended_for": "Véhicule Neuf"}
        ],
        "default_garage": "Réseau Auto Sanlam Cotonou - Avenue Jean-Paul II, Haie Vive",
        "standard_franchise": 45000
    },
    "CI": {
        "code": "CI",
        "name": "Côte d'Ivoire",
        "flag": "🇨🇮",
        "entity": "SanlamAllianz Côte d'Ivoire",
        "currency": "FCFA",
        "currency_symbol": "FCFA",
        "regulatory_body": "Code CIMA (Conférence Interafricaine des Marchés d'Assurances)",
        "products": [
            {"id": "ci-p1", "name": "Auto Classique (Tiers)", "desc": "Responsabilité Civile obligatoire CIMA + Défense & Recours", "recommended_for": "Occasion"},
            {"id": "ci-p2", "name": "Auto Zen (Tiers Amélioré)", "desc": "Tiers + Vol + Incendie + Bris de glace avec facilités de paiement", "recommended_for": "Usage quotidien"},
            {"id": "ci-p3", "name": "Auto Platinum (Tous Risques)", "desc": "Couverture intégrale 0 km, dommages tous accidents et véhicule de remplacement", "recommended_for": "Véhicule Neuf"}
        ],
        "default_garage": "Garage Central Abidjan - Boulevard de la République, Marcory",
        "standard_franchise": 50000
    },
    "MA": {
        "code": "MA",
        "name": "Maroc",
        "flag": "🇲🇦",
        "entity": "Sanlam Maroc",
        "currency": "MAD",
        "currency_symbol": "DH",
        "regulatory_body": "ACAPS (Autorité de Contrôle des Assurances et de la Prévoyance Sociale)",
        "products": [
            {"id": "ma-p1", "name": "Assur'Auto Pass (Tiers)", "desc": "Responsabilité Civile + Assistance 24/7 de base", "recommended_for": "Budget optimisé"},
            {"id": "ma-p2", "name": "Pack L'Hemza (Tiers Plus)", "desc": "RC + Collision + Vol/Incendie + Bris de glace sans franchise réseau", "recommended_for": "Usage ville"},
            {"id": "ma-p3", "name": "Assur'Auto Intégrale (Tous Risques)", "desc": "Tous risques avec rachat de franchise & garantie décès toutes causes", "recommended_for": "Véhicule Neuf"}
        ],
        "default_garage": "Réseau Auto Sanlam Casablanca - Bd Zerktouni, Maarif",
        "standard_franchise": 1500
    },
    "SN": {
        "code": "SN",
        "name": "Sénégal",
        "flag": "🇸🇳",
        "entity": "SanlamAllianz Sénégal",
        "currency": "FCFA",
        "currency_symbol": "FCFA",
        "regulatory_body": "Code CIMA Sénégal",
        "products": [
            {"id": "sn-p1", "name": "Auto Pack Teranga (Tiers)", "desc": "Responsabilité Civile obligatoire + Sécurité routière Teranga", "recommended_for": "Usage occasionnel"},
            {"id": "sn-p2", "name": "Auto Zen Teranga (Tiers Avantage)", "desc": "Tiers + Vol + Incendie + Bris de Glace + Défense Recours", "recommended_for": "Trajet quotidien"},
            {"id": "sn-p3", "name": "Tous Risques Avantage", "desc": "Dommages Tous Accidents + Assistance 24h/24 Dakar & Régions", "recommended_for": "Véhicule Neuf"}
        ],
        "default_garage": "Garage Cap-Vert Dakar - Route de Ouakam, Dakar",
        "standard_franchise": 40000
    }
}

# Country-Specific Mock Prospects Pipeline
PROSPECTS_BY_COUNTRY = {
    "BJ": {
        "lead-bj-1": {
            "id": "lead-bj-1",
            "country": "BJ",
            "name": "Koffi Bio Dossou",
            "phone": "+229 97 12 34 56",
            "channel": "WhatsApp",
            "vehicle": "Toyota Corolla (2023) - Cotonou",
            "need": "Auto Platinum (Tous Risques)",
            "intention": "Chaud 🔥",
            "document_uploaded": True,
            "document_name": "carte_grise_dossou.pdf",
            "appointment": "2026-07-29 à 11:00",
            "orass_policy_num": "POL-AUTO-BENIN-889102",
            "conversation": [
                {"sender": "user", "text": "Bonjour, je suis Dossou à Cotonou. Je veux assurer ma Toyota Corolla neuve immatriculée RB-1234-AB."},
                {"sender": "assistant", "text": "Bonjour M. Dossou ! Bienvenue chez SanlamAllianz Bénin. Votre Devis N° DEV-781920 a été calculé sous le Code CIMA. Votre police N° POL-AUTO-BENIN-889102 a été émise avec succès."}
            ],
            "summary": "Prospect Koffi Bio Dossou (Cotonou, Bénin), Toyota Corolla (RB-1234-AB). Police POL-AUTO-BENIN-889102 validée.",
            "next_action": "Télécharger l'attestation CIMA Bénin et la carte verte."
        }
    },
    "CI": {
        "lead-ci-1": {
            "id": "lead-ci-1",
            "country": "CI",
            "name": "Jean-Marc Kouassi",
            "phone": "+225 07 08 09 10 11",
            "channel": "WhatsApp",
            "vehicle": "Toyota Hilux (2023) - Usage Professionnel",
            "need": "Auto Platinum (Tous Risques)",
            "intention": "Chaud 🔥",
            "document_uploaded": True,
            "document_name": "carte_grise_kouassi.pdf",
            "appointment": "2026-07-25 à 14:30",
            "conversation": [
                {"sender": "user", "text": "Bonjour, je souhaite assurer mon pick-up Toyota Hilux neuf à Abidjan."},
                {"sender": "assistant", "text": "Bonjour M. Kouassi ! Pour votre Hilux neuf à Abidjan, nous vous recommandons notre formule Auto Platinum (Tous Risques) sous le Code CIMA."}
            ],
            "summary": "Prospect Jean-Marc Kouassi (Abidjan), Toyota Hilux neuf. Formule souscrite: Auto Platinum. Carte grise validée.",
            "next_action": "Rendez-vous téléphonique confirmé pour le 2026-07-25 à 14:30."
        }
    },
    "MA": {
        "lead-ma-1": {
            "id": "lead-ma-1",
            "country": "MA",
            "name": "Youssef Benjelloun",
            "phone": "+212 6 61 23 45 67",
            "channel": "Web Widget",
            "vehicle": "Renault Clio 5 (2023) - Casablanca",
            "need": "Assur'Auto Intégrale (Tous Risques)",
            "intention": "Chaud 🔥",
            "document_uploaded": True,
            "document_name": "carte_grise_benjelloun.pdf",
            "appointment": "2026-07-26 à 10:00",
            "conversation": [
                {"sender": "user", "text": "Salam, je cherche une assurance Tous Risques avec rachat de franchise sur Casablanca."}
            ],
            "summary": "Prospect Youssef Benjelloun (Casablanca), Renault Clio 5. Formule: Assur'Auto Intégrale. Carte grise validée.",
            "next_action": "Rendez-vous agence Casablanca confirmé pour le 2026-07-26 à 10:00."
        }
    },
    "SN": {
        "lead-sn-1": {
            "id": "lead-sn-1",
            "country": "SN",
            "name": "Moustapha Ndiaye",
            "phone": "+221 77 123 45 67",
            "channel": "WhatsApp",
            "vehicle": "Nissan Qashqai (2022) - Dakar",
            "need": "Tous Risques Avantage",
            "intention": "Chaud 🔥",
            "document_uploaded": True,
            "document_name": "carte_grise_ndiaye.pdf",
            "appointment": "2026-07-27 à 16:00",
            "conversation": [],
            "summary": "Prospect Moustapha Ndiaye (Dakar), Nissan Qashqai. Formule: Tous Risques Avantage. Carte grise validée.",
            "next_action": "Appel commercial prévu le 2026-07-27 à 16:00."
        }
    }
}

# Country-Specific Mock Claims
CLAIMS_BY_COUNTRY = {
    "BJ": {
        "claim-bj-101": {
            "id": "claim-bj-101",
            "country": "BJ",
            "insured_name": "Bio Gounou",
            "vehicle": "Toyota RAV4 (2022)",
            "date": "2026-07-20",
            "circumstances": "Collision déclarée au carrefour Étoile Cotonou.",
            "cost": 6200000, # FCFA
            "score": 82,
            "status": "Enquête",
            "expert_report": "Rapport d'expertise SanlamAllianz Bénin : Déformations non conformes au choc frontal sur l'Avenue Jean-Paul II Cotonou. Facture surévaluée du Garage Atlantique Cotonou.",
            "flags": [
                "Incohérence déclarative CIMA (Carrefour Étoile Cotonou)",
                "Prestataire suspect (Garage Atlantique Cotonou)",
                "Montant élevé (6.2M FCFA)"
            ],
            "explanation": "Score de risque de 82/100 sous réglementation CIMA Bénin.",
            "comments": []
        }
    },
    "CI": {
        "claim-ci-101": {
            "id": "claim-ci-101",
            "country": "CI",
            "insured_name": "Bakary Diarra",
            "vehicle": "Hyundai Tucson (2022)",
            "date": "2026-07-12",
            "circumstances": "Collision frontale simulée au carrefour de Treichville.",
            "cost": 8500000,
            "score": 85,
            "status": "Enquête",
            "expert_report": "Rapport expert : Les déformations sur la Hyundai Tucson à Abidjan ne correspondent pas à un choc statique.",
            "flags": ["Incohérence déclarative CIMA (Choc Treichville)"],
            "explanation": "Score de risque de 85/100.",
            "comments": []
        }
    },
    "MA": {
        "claim-ma-101": {
            "id": "claim-ma-101",
            "country": "MA",
            "insured_name": "Omar El Amrani",
            "vehicle": "BMW Série 3 (2021)",
            "date": "2026-07-10",
            "circumstances": "Choc arrière dans un parking à Casablanca Maarif.",
            "cost": 125000,
            "score": 88,
            "status": "Enquête",
            "expert_report": "Rapport d'expertise Sanlam Maroc : Déformations dynamiques sur voie publique déguisées en choc parking Maarif.",
            "flags": ["Incohérence déclarative ACAPS (Casablanca)"],
            "explanation": "Score de risque élevé de 88/100.",
            "comments": []
        }
    },
    "SN": {
        "claim-sn-101": {
            "id": "claim-sn-101",
            "country": "SN",
            "insured_name": "Ousmane Sow",
            "vehicle": "Peugeot 301 (2020)",
            "date": "2026-07-14",
            "circumstances": "Vol de véhicule déclaré à Dakar Corniche.",
            "cost": 9200000,
            "score": 78,
            "status": "Enquête",
            "expert_report": "Rapport expert Dakar : Vol déclaré 12 jours seulement après la souscription du contrat CIMA.",
            "flags": ["Sinistralité précoce CIMA"],
            "explanation": "Score de 78/100.",
            "comments": []
        }
    }
}

# Global State Containers
ACTIVE_COUNTRY = "BJ"
PROSPECTS = dict(PROSPECTS_BY_COUNTRY["BJ"])
CLAIMS = dict(CLAIMS_BY_COUNTRY["BJ"])

NETWORK_DATA = {
    "nodes": [
        {"id": "claim-101", "label": "Sinistre #101 Cotonou", "group": "claim", "title": "Dossier sous alerte"},
        {"id": "user-marc", "label": "Assuré Bénin", "group": "insured", "title": "Profil sous surveillance"},
        {"id": "garage-prestige", "label": "Garage Atlantique Cotonou", "group": "garage", "title": "Garagiste sous alerte"},
        {"id": "phone-shared", "label": "Tél +229 Partagé", "group": "phone", "title": "Lien réseau décelé"}
    ],
    "edges": [
        {"from": "claim-101", "to": "user-marc", "label": "Déclaré par"},
        {"from": "claim-101", "to": "garage-prestige", "label": "Réparateur facturé"},
        {"from": "user-marc", "to": "phone-shared", "label": "Contact identique"}
    ]
}

def set_active_country(country_code: str):
    """Switch global active country (BJ, CI, MA, SN)."""
    global ACTIVE_COUNTRY, PROSPECTS, CLAIMS
    if country_code in COUNTRY_CONFIGS:
        ACTIVE_COUNTRY = country_code
        PROSPECTS.clear()
        PROSPECTS.update(PROSPECTS_BY_COUNTRY.get(country_code, {}))
        CLAIMS.clear()
        CLAIMS.update(CLAIMS_BY_COUNTRY.get(country_code, {}))
        print(f"[Database Core] Switched active country context to: {country_code} ({COUNTRY_CONFIGS[country_code]['name']})")
        return COUNTRY_CONFIGS[country_code]
    return COUNTRY_CONFIGS["BJ"]
