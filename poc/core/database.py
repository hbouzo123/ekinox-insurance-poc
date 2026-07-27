# Country-Specific Catalogs & Localizations for SanlamAllianz

COUNTRY_CONFIGS = {
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
                {"sender": "assistant", "text": "Bonjour M. Kouassi ! Pour votre Hilux neuf à Abidjan, nous vous recommandons notre formule **Auto Platinum (Tous Risques)** sous le Code CIMA. Elle inclut la protection dommages tous accidents et l'assistance 0 km H24."}
            ],
            "summary": "Prospect Jean-Marc Kouassi (Abidjan), Toyota Hilux neuf. Formule souscrite: Auto Platinum. Carte grise validée.",
            "next_action": "Rendez-vous téléphonique confirmé pour le 2026-07-25 à 14:30."
        },
        "lead-ci-2": {
            "id": "lead-ci-2",
            "country": "CI",
            "name": "Awa Traoré",
            "phone": "+225 05 01 02 03 04",
            "channel": "Meta Ads",
            "vehicle": "Peugeot 208 (2021) - Trajets Cocody",
            "need": "Auto Zen (Tiers Amélioré)",
            "intention": "Tiède ⏳",
            "document_uploaded": False,
            "document_name": "",
            "appointment": "",
            "conversation": [
                {"sender": "user", "text": "Bonjour, quel est le prix pour une Peugeot 208 ?"}
            ],
            "summary": "Prospect Awa Traoré (Cocody), Peugeot 208. Recommandation: Auto Zen.",
            "next_action": "Relancer par SMS pour l'upload du justificatif d'identité."
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
                {"sender": "user", "text": "Salam, je cherche une assurance Tous Risques avec rachat de franchise sur Casablanca."},
                {"sender": "assistant", "text": "Salam M. Benjelloun ! Notre formule **Assur'Auto Intégrale** Sanlam Maroc est parfaitement adaptée. Elle inclut l'option Rachat de Franchise et la garantie décès toutes causes conforme aux directives ACAPS."}
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
            "conversation": [
                {"sender": "user", "text": "Na redef ! Devis pour Nissan Qashqai sur Dakar."},
                {"sender": "assistant", "text": "Dalal ak jamm M. Ndiaye ! Pour votre Nissan Qashqai à Dakar, la formule **Tous Risques Avantage** SanlamAllianz Sénégal vous offre la meilleure couverture dommages avec secours Teranga H24."}
            ],
            "summary": "Prospect Moustapha Ndiaye (Dakar), Nissan Qashqai. Formule: Tous Risques Avantage. Carte grise validée.",
            "next_action": "Appel commercial prévu le 2026-07-27 à 16:00."
        }
    }
}

# Country-Specific Mock Claims
CLAIMS_BY_COUNTRY = {
    "CI": {
        "claim-ci-101": {
            "id": "claim-ci-101",
            "country": "CI",
            "insured_name": "Bakary Diarra",
            "vehicle": "Hyundai Tucson (2022)",
            "date": "2026-07-12",
            "circumstances": "Collision frontale simulée au carrefour de Treichville.",
            "cost": 8500000, # FCFA
            "score": 85,
            "status": "Enquête",
            "expert_report": "Rapport expert : Les déformations sur la Hyundai Tucson à Abidjan ne correspondent pas à un choc statique. Facture du Garage Auto Marcory présentant un montant de 8.5M FCFA manifestement surévalué pour le pare-choc.",
            "flags": [
                "Incohérence déclarative CIMA (Choc Treichville)",
                "Garage suspect (Auto Marcory - Récurence de surfacturations FCFA)",
                "Montant financier anormalement élevé (8.5M FCFA)"
            ],
            "explanation": "Score de risque de 85/100 sous réglementation CIMA. 1° Incohérence cinématique relevée par l'expert. 2° Garagiste sous surveillance pour surfacturations récurrentes sur Abidjan.",
            "comments": [
                {"author": "Enquêteur Abidjan", "text": "Vérification des pièces de rechange au garage d'Abidjan.", "date": "2026-07-15"}
            ]
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
            "cost": 125000, # MAD
            "score": 88,
            "status": "Enquête",
            "expert_report": "Rapport d'expertise Sanlam Maroc : Déformations dynamiques sur voie publique déguisées en choc parking Maarif. Coût estimé par le garage de 125 000 DH dépassant les barèmes ACAPS.",
            "flags": [
                "Incohérence déclarative ACAPS (Casablanca)",
                "Garage suspect (Garage Prestige Casablanca)",
                "Montant financier élevé (125 000 DH)"
            ],
            "explanation": "Score de risque élevé de 88/100 sous contrôle ACAPS. 1° Fausse déclaration de lieu de collision. 2° Garage sous alerte d'audit financier à Casablanca.",
            "comments": [
                {"author": "Enquêteur Casablanca", "text": "Convocation de l'assuré pour expertise contradictoire.", "date": "2026-07-14"}
            ]
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
            "cost": 9200000, # FCFA
            "score": 78,
            "status": "Enquête",
            "expert_report": "Rapport expert Dakar : Vol déclaré 12 jours seulement après la souscription du contrat CIMA. Re-programmation suspecte du transpondeur de clé.",
            "flags": [
                "Sinistralité précoce CIMA (12 jours après souscription)",
                "Anomalie clé électronique transpondeur"
            ],
            "explanation": "Score de 78/100. Alerte automatique sur sinistralité ultra-précoce sous Code CIMA Sénégal.",
            "comments": []
        }
    }
}

# Global State Containers
ACTIVE_COUNTRY = "CI"
PROSPECTS = dict(PROSPECTS_BY_COUNTRY["CI"])
CLAIMS = dict(CLAIMS_BY_COUNTRY["CI"])

NETWORK_DATA = {
    "nodes": [
        {"id": "claim-101", "label": "Sinistre #101", "group": "claim", "title": "Dossier sous investigation"},
        {"id": "user-marc", "label": "Assuré", "group": "insured", "title": "Profil sous alerte"},
        {"id": "garage-prestige", "label": "Garage Partenaire Suspect", "group": "garage", "title": "Garage sous surveillance"},
        {"id": "phone-shared", "label": "Tél +225/212 Partagé", "group": "phone", "title": "Lien réseau décelé"},
        {"id": "expert-lab", "label": "Expertise Technique", "group": "expert", "title": "Rapport sémantique"}
    ],
    "edges": [
        {"from": "claim-101", "to": "user-marc", "label": "Déclaré par"},
        {"from": "claim-101", "to": "garage-prestige", "label": "Réparateur facturé"},
        {"from": "user-marc", "to": "phone-shared", "label": "Contact identique"},
        {"from": "claim-101", "to": "expert-lab", "label": "Analysé par"}
    ]
}

def set_active_country(country_code: str):
    """Switch global active country (CI, MA, SN)."""
    global ACTIVE_COUNTRY, PROSPECTS, CLAIMS
    if country_code in COUNTRY_CONFIGS:
        ACTIVE_COUNTRY = country_code
        PROSPECTS.clear()
        PROSPECTS.update(PROSPECTS_BY_COUNTRY.get(country_code, {}))
        CLAIMS.clear()
        CLAIMS.update(CLAIMS_BY_COUNTRY.get(country_code, {}))
        print(f"[Database Core] Switched active country context to: {country_code} ({COUNTRY_CONFIGS[country_code]['name']})")
        return COUNTRY_CONFIGS[country_code]
    return COUNTRY_CONFIGS["CI"]
