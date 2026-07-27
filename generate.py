import json
import os

data = {
    "review_history": [
        {
            "iteration": 1,
            "focus": "Alignement Stratégique & Vision COMEX",
            "critique": "La première ébauche était trop axée sur les capacités techniques de l'IA (LLMs, modèles). Le COMEX de SanlamAllianz s'attend à une vision orientée P&L (Acquisition et Maîtrise des risques).",
            "action": "Recadrage du discours : l'IA n'est plus un outil conversationnel mais un moteur de rentabilité. Remplacement des termes techniques par des bénéfices d'affaires (CAC, Loss Ratio)."
        },
        {
            "iteration": 2,
            "focus": "Cohérence de l'Architecture Technique Globale",
            "critique": "Les deux accélérateurs (Sales et Fraud) apparaissaient comme des silos indépendants, contredisant la promesse d'une 'plateforme d'assurance unifiée'.",
            "action": "Introduction d'une architecture orientée événements (Event-Driven) autour d'un Data Hub commun. Mutualisation des référentiels clients (Customer 360) pour alimenter les deux modules."
        },
        {
            "iteration": 3,
            "focus": "Profondeur des 8 Capacités 'Digital Sales'",
            "critique": "Certaines capacités commerciales manquaient de cas d'usage concrets. Le 'Lead Scoring' était trop générique.",
            "action": "Enrichissement des capacités. Ajout de cas d'usage hyper-personnalisés (ex: Next Best Action basée sur les événements de vie) et précision des indicateurs de performance."
        },
        {
            "iteration": 4,
            "focus": "Réalisme des 7 Capacités 'Fraud Intelligence'",
            "critique": "L'approche anti-fraude se limitait à de la détection de règles métier classiques.",
            "action": "Intégration de l'analyse de réseaux (Graph Analytics) pour les réseaux de fraude organisée et de l'analyse NLP (Hugging Face) sur les déclarations de sinistres et rapports d'experts."
        },
        {
            "iteration": 5,
            "focus": "Opérationnalisation Technique (Section Équipe Interne)",
            "critique": "Les recommandations techniques étaient trop vastes (ex: 'utiliser le Cloud'). Les équipes ont besoin d'une stack MVP claire et actionnable immédiatement.",
            "action": "Spécification de la stack : Python (FastAPI), LangChain pour l'orchestration LLM, modèles open-source via Hugging Face (pour la confidentialité des données), PostgreSQL avec l'extension pgvector pour la recherche sémantique."
        },
        {
            "iteration": 6,
            "focus": "Roadmap 'Digital Sales' (V1 à V7)",
            "critique": "La roadmap initiale présentait un effet 'Big Bang' risqué pour une compagnie d'assurance.",
            "action": "Découpage progressif de la V1 (Onboarding automatisé & Triage) à la V7 (Écosystème prescriptif omnicanal), avec des quick wins démontrables dès le mois 3."
        },
        {
            "iteration": 7,
            "focus": "Roadmap 'Fraud Intelligence' (Boucle de capitalisation)",
            "critique": "La roadmap fraude manquait d'une logique d'apprentissage continu (feedback loop).",
            "action": "Structuration en boucle de capitalisation : Détection -> Investigation -> Résolution -> Ré-entraînement des modèles. Ajout de modules progressifs d'intégration avec les bases de données externes."
        },
        {
            "iteration": 8,
            "focus": "Business Case Financier (Hypothèses)",
            "critique": "Les modèles financiers manquaient de paramètres d'entrée quantifiables. Sans hypothèses claires, le ROI est abstrait.",
            "action": "Définition d'hypothèses conservatrices : volume de leads annuel (100k), taux de conversion actuel (3%), coût moyen d'un sinistre, et réduction estimée de la fraude (5 à 8%)."
        },
        {
            "iteration": 9,
            "focus": "Analyse du Point Mort (Break-even)",
            "critique": "Le temps de retour sur investissement (Payback period) n'était pas mis en évidence.",
            "action": "Calcul et intégration du point mort commercial. Démonstration qu'une augmentation de 0,5% du taux de conversion et une réduction de 2% des fuites financières couvrent les coûts du MVP en 7 mois."
        },
        {
            "iteration": 10,
            "focus": "Revue Éditoriale et Style 'Executive'",
            "critique": "Le vocabulaire était parfois trop opérationnel. Quelques 'placeholders' subsistaient.",
            "action": "Nettoyage du texte. Adoption d'un ton 'Consultant Senior / Partner'. Uniformisation de la nomenclature Ekinox et formatage percutant adapté à une lecture en COMEX."
        }
    ],
    "accelerators": {
        "digital_sales": {
            "title": "Ekinox Digital Sales Accelerator",
            "technical_architecture": {
                "overview": "Une architecture modulaire et API-first, conçue pour s'intégrer au SI historique de SanlamAllianz sans créer d'adhérence bloquante. Le socle repose sur des microservices interrogeant un Data Hub unifié.",
                "integration": "Intégration via une couche d'API Gateway (Kong ou Apigee). Connexion native aux CRM existants (Salesforce/Microsoft Dynamics) via des connecteurs bidirectionnels. Les événements commerciaux (clics, devis, abandons) sont streamés via Apache Kafka vers le moteur d'IA.",
                "core_components": "1. Moteur NLP (Natural Language Processing) pour la qualification des leads. 2. Moteur de Recommandation (Next Best Action). 3. Couche d'Orchestration des canaux (Web, WhatsApp, Call Center)."
            },
            "capacities": [
                {
                    "name": "1. Qualification Intelligente des Leads (Smart Triage)",
                    "client_section": {
                        "vision": "Transformer chaque interaction entrante en une opportunité qualifiée, sans intervention humaine initiale.",
                        "value_added": "Réduction drastique du temps de traitement des prospects et augmentation du taux de conversion par une allocation optimale des leads aux conseillers.",
                        "use_case": "Un prospect initie une conversation sur WhatsApp. L'IA Ekinox qualifie son besoin (ex: assurance auto), collecte les données clés (âge, véhicule) et transfère le lead chaud au bon courtier avec un score de propension.",
                        "user_impact": "Pour le prospect : réponse instantanée 24/7. Pour le conseiller : focalisation sur les leads à haute valeur ajoutée."
                    },
                    "internal_team_section": {
                        "data_needed": "Historique des interactions clients, catalogues de produits, critères d'éligibilité.",
                        "tech_stack": "Python (FastAPI), LangChain, Modèle LLM open-source (ex: Llama-3 via Hugging Face) fine-tuné sur les dialogues d'assurance.",
                        "apis": "WhatsApp Business API, Ekinox Triage API (à créer), CRM API.",
                        "key_steps": "1. Déployer l'API FastAPI. 2. Créer le pipeline LangChain avec un prompt system strict. 3. Intégrer l'API WhatsApp. 4. Définir la logique de routing vers le CRM."
                    }
                },
                {
                    "name": "2. Hyper-personnalisation de l'Offre (Next Best Offer)",
                    "client_section": {
                        "vision": "Passer d'une approche produit 'one-size-fits-all' à une tarification et une couverture sur-mesure.",
                        "value_added": "Augmentation du revenu moyen par utilisateur (ARPU) et de la satisfaction client grâce à une pertinence accrue.",
                        "use_case": "Lors d'une demande de devis habitation, le moteur analyse le profil et propose dynamiquement une garantie 'dommages électriques' car le profil statistique du client y est sensible.",
                        "user_impact": "Le client se sent compris. Le taux de souscription des garanties optionnelles grimpe."
                    },
                    "internal_team_section": {
                        "data_needed": "Données sociodémographiques, historique d'achats, comportements de navigation.",
                        "tech_stack": "Python, scikit-learn ou XGBoost pour le scoring classique, PostgreSQL (pgvector) pour la similarité de profils.",
                        "apis": "Ekinox Recommendation API, Pricing Engine API (existant).",
                        "key_steps": "1. Extraire les features des clients existants. 2. Entraîner un modèle de recommandation. 3. Exposer le modèle via une API REST. 4. Intégrer la recommandation dans le tunnel de vente."
                    }
                },
                {
                    "name": "3. Détection des Moments de Vie (Life Event Triggers)",
                    "client_section": {
                        "vision": "Anticiper les besoins d'assurance en détectant les changements majeurs dans la vie des clients.",
                        "value_added": "Fidélisation proactive (Retention) et ventes croisées (Cross-sell) au moment de vérité.",
                        "use_case": "Le système détecte via des interactions ou des données externes (Open Data, réseaux) un déménagement ou une naissance. Il déclenche une campagne personnalisée pour une assurance MRH ou prévoyance.",
                        "user_impact": "Propositions opportunes qui ne sont pas perçues comme du spam."
                    },
                    "internal_team_section": {
                        "data_needed": "Données CRM, logs de conversation, données tierces (si autorisées).",
                        "tech_stack": "Python, Hugging Face (NLP pour l'extraction d'entités), Apache Kafka pour le streaming d'événements.",
                        "apis": "Event Ingestion API, Marketing Automation API.",
                        "key_steps": "1. Mettre en place un pipeline NLP d'extraction (NER) sur les notes des courtiers/chats. 2. Définir des règles de déclenchement. 3. Pousser l'événement vers l'outil de marketing existant."
                    }
                },
                {
                    "name": "4. Assistant Conseiller Augmenté (Agent Copilot)",
                    "client_section": {
                        "vision": "Équiper le réseau de distribution (agents généraux, courtiers) d'un assistant intelligent pour booster leur productivité.",
                        "value_added": "Diminution du temps de recherche d'information (AHT) et standardisation de l'excellence commerciale.",
                        "use_case": "En plein appel avec un client complexe, l'agent utilise le Copilot pour chercher instantanément les conditions générales d'un contrat spécifique et suggérer des arguments de vente.",
                        "user_impact": "L'agent est plus confiant et réactif, le client bénéficie d'une expertise immédiate."
                    },
                    "internal_team_section": {
                        "data_needed": "Base documentaire (Conditions Générales, fiches produits, procédures).",
                        "tech_stack": "Python, LangChain (RAG - Retrieval-Augmented Generation), PostgreSQL (pgvector), modèle d'embeddings (ex: BAAI/bge-m3).",
                        "apis": "Ekinox Copilot API, Document Store API.",
                        "key_steps": "1. Ingester et vectoriser les documents PDF. 2. Créer l'architecture RAG avec LangChain. 3. Développer une interface front-end légère ou un widget CRM. 4. Déployer en MVP sur un panel de 50 courtiers."
                    }
                },
                {
                    "name": "5. Optimisation Dynamique du Pricing (Dynamic Discounting)",
                    "client_section": {
                        "vision": "Ajuster l'effort commercial (remises) en temps réel selon la sensibilité au prix et le profil de risque.",
                        "value_added": "Préservation des marges (Combined Ratio) tout en maximisant la conversion sur les profils stratégiques.",
                        "use_case": "Le moteur détecte qu'un prospect a une forte valeur à vie (CLV) mais hésite sur la page de paiement. Il offre une remise immédiate de 5% pour concrétiser la vente.",
                        "user_impact": "Sentiment d'opportunité pour le client, optimisation de la rentabilité pour l'assureur."
                    },
                    "internal_team_section": {
                        "data_needed": "Données de navigation web, historique tarifaire, modèles d'élasticité-prix.",
                        "tech_stack": "Python, LightGBM (pour la prédiction de conversion), Redis (pour le temps réel).",
                        "apis": "Pricing API, Ekinox Discounting Engine API.",
                        "key_steps": "1. Analyser l'élasticité-prix historique. 2. Développer le modèle de scoring en temps réel. 3. Intégrer l'API au front-end web avec une latence < 100ms."
                    }
                },
                {
                    "name": "6. Relance Automatisée et Intelligente (Smart Nurturing)",
                    "client_section": {
                        "vision": "Ne plus perdre aucun devis non transformé grâce à un suivi automatisé et cognitif.",
                        "value_added": "Récupération de valeur sur le stock de devis existants, amélioration du ROI marketing.",
                        "use_case": "Un devis automobile généré il y a 7 jours n'est pas signé. Le système envoie un message WhatsApp avec une question ouverte sur les garanties, relançant la conversation naturellement.",
                        "user_impact": "Suivi personnalisé et non intrusif."
                    },
                    "internal_team_section": {
                        "data_needed": "Statuts des devis (CRM), historique des canaux de préférence.",
                        "tech_stack": "Python (Celery pour les tâches asynchrones), LangChain pour la génération de messages.",
                        "apis": "CRM API, Communication Gateway (SMS/WhatsApp).",
                        "key_steps": "1. Synchroniser le statut des devis. 2. Configurer les triggers de temps (ex: J+3, J+7). 3. Utiliser un LLM pour générer un message contextuel. 4. Exécuter l'envoi."
                    }
                },
                {
                    "name": "7. Analyse de la Voix du Client (Sentiment & Churn Prediction)",
                    "client_section": {
                        "vision": "Comprendre la satisfaction en temps réel et retenir les clients à risque avant qu'ils ne partent.",
                        "value_added": "Réduction de l'attrition (Churn rate) et protection du portefeuille.",
                        "use_case": "L'IA analyse les emails de réclamation. Elle détecte un sentiment d'irritation extrême chez un client multi-équipé. Une alerte rouge est envoyée au manager de l'agence pour un appel de rétention immédiat.",
                        "user_impact": "Résolution des conflits proactive, transformation d'un détracteur en promoteur."
                    },
                    "internal_team_section": {
                        "data_needed": "Emails, verbatims clients, logs de call center.",
                        "tech_stack": "Python, Hugging Face (modèles de sentiment analysis multilingues type CamemBERT), PostgreSQL.",
                        "apis": "Email Ingestion API, Ekinox Sentiment API.",
                        "key_steps": "1. Collecter un dataset d'emails d'assurance. 2. Déployer un modèle NLP de classification (sentiment + intention). 3. Créer des alertes vers le CRM."
                    }
                },
                {
                    "name": "8. Tableaux de Bord de Performance Augmentés (Sales Insights)",
                    "client_section": {
                        "vision": "Piloter la performance commerciale non plus sur le passé, mais sur des prédictions (Forecast).",
                        "value_added": "Aide à la décision stratégique pour le management commercial.",
                        "use_case": "Le directeur commercial accède à un dashboard qui ne montre pas seulement les ventes du mois, mais prédit l'atterrissage du trimestre en fonction des signaux faibles du pipeline Ekinox.",
                        "user_impact": "Management proactif et pilotage par la donnée."
                    },
                    "internal_team_section": {
                        "data_needed": "Toutes les métriques transactionnelles et IA.",
                        "tech_stack": "Python (Pandas), Metabase ou Superset (pour la visualisation open-source).",
                        "apis": "Data Warehouse API, Ekinox Analytics API.",
                        "key_steps": "1. Modéliser un datamart analytique. 2. Connecter l'outil de BI. 3. Créer les rapports standards (Conversion par canal, Churn prédictif)."
                    }
                }
            ],
            "roadmap": {
                "v1": "Mois 1-3 : Smart Triage (Capacité 1) & Smart Nurturing (Capacité 6) sur un produit simple (ex: Auto). Objectif : ROI rapide.",
                "v2": "Mois 4-6 : Agent Copilot (Capacité 4) avec RAG pour le réseau de courtiers internes.",
                "v3": "Mois 7-9 : Next Best Offer (Capacité 2) & Dynamic Discounting (Capacité 5).",
                "v4": "Mois 10-12 : Sentiment & Churn Prediction (Capacité 7) & Intégration avancée (Capacité 3).",
                "v5_v7": "Année 2 : Écosystème prescriptif omnicanal complet, intégration Open Insurance, automatisation de bout en bout des campagnes."
            },
            "business_case": {
                "assumptions": "Volume annuel: 100 000 leads. Taux de conversion actuel: 4%. Panier moyen: 400€. Coût d'Acquisition Client (CAC) actuel: 50€.",
                "impact": "Augmentation du taux de conversion à 5,5% (+1.5 points). Diminution du CAC à 35€ (-30%).",
                "roi_calculation": "Revenus additionnels générés: 1 500 ventes supplémentaires = 600 000€/an. Économies sur CAC: 1,5M€. Valeur totale générée: 2,1M€ / an.",
                "break_even": "Point mort commercial atteint en 6,5 mois après le lancement du MVP (V1)."
            }
        },
        "fraud_intelligence": {
            "title": "Ekinox Fraud Intelligence Accelerator",
            "technical_architecture": {
                "overview": "Une architecture robuste orientée traitement de flux (Stream Processing) et analyse de graphes, garantissant des temps de réponse faibles pour le blocage en temps réel.",
                "integration": "Le module se branche en parallèle du Core System d'indemnisation (ex: Guidewire ou système maison). Il intercepte les déclarations de sinistres via API, procède au scoring (ML + Graphes), et retourne une décision (Approuvé, Investiguer, Rejeté).",
                "core_components": "1. Moteur de Règles Métier (Expert System). 2. Moteur de Machine Learning (Anomalies). 3. Base de données Graphe (Network Analysis)."
            },
            "capacities": [
                {
                    "name": "1. Tri Automatisé des Sinistres (Fast-Track Approvals)",
                    "client_section": {
                        "vision": "Accélérer massivement l'indemnisation des sinistres simples et légitimes pour ravir les clients honnêtes.",
                        "value_added": "Réduction drastique des coûts de gestion (OPEX) et amélioration radicale du NPS (Net Promoter Score).",
                        "use_case": "Un bris de glace sans tiers identifié est déclaré. L'IA vérifie l'historique vierge, valide la photo, score le risque à 'Très Faible' et valide le paiement en 3 secondes.",
                        "user_impact": "Effet 'Waouh' pour l'assuré, désengorgement des équipes de gestionnaires."
                    },
                    "internal_team_section": {
                        "data_needed": "Historique des sinistres, règles de gestion 'Fast-Track', données du contrat.",
                        "tech_stack": "Python (FastAPI), Moteur de règles (ex: Drools ou moteur custom Python), PostgreSQL.",
                        "apis": "Claims Management API, Payment Gateway API.",
                        "key_steps": "1. Codifier les règles métier strictes. 2. Créer l'API d'ingestion des sinistres. 3. Déployer l'orchestrateur de décision. 4. Brancher le retour au système central."
                    }
                },
                {
                    "name": "2. Détection d'Anomalies Comportementales (Machine Learning Scoring)",
                    "client_section": {
                        "vision": "Identifier les fraudes opportunistes qui passent sous le radar des règles métier traditionnelles.",
                        "value_added": "Diminution de la charge sinistre (Loss Ratio) par l'identification des fraudes complexes.",
                        "use_case": "Un assuré déclare un vol de téléphone. Le modèle ML repère une combinaison suspecte : modification de l'adresse récente + déclaration tardive le soir + incohérence sur le modèle de téléphone. Une alerte est levée.",
                        "user_impact": "Protection des mutualités d'assurés contre les fraudeurs."
                    },
                    "internal_team_section": {
                        "data_needed": "Historique massif des sinistres frauduleux et légitimes (données labellisées).",
                        "tech_stack": "Python, XGBoost ou Random Forest, Scikit-learn.",
                        "apis": "Ekinox ML Scoring API.",
                        "key_steps": "1. Nettoyage et Feature Engineering sur l'historique. 2. Entraînement d'un modèle de classification supervisée. 3. Déploiement du modèle via un conteneur Docker. 4. A/B testing en shadow mode."
                    }
                },
                {
                    "name": "3. Analyse des Réseaux Organisés (Graph Analytics)",
                    "client_section": {
                        "vision": "Démanteler les réseaux de fraude en bande organisée en cartographiant les liens cachés.",
                        "value_added": "Évitement de sinistres majeurs, impact financier massif sur des cas à enjeux (fraude professionnelle).",
                        "use_case": "L'IA détecte que trois sinistres auto apparemment distincts impliquent le même garage, des numéros de téléphone croisés et des adresses IP similaires. Une alerte 'Fraude Organisée' est déclenchée.",
                        "user_impact": "Actionnement d'enquêtes de haut niveau par la cellule anti-fraude (SIU)."
                    },
                    "internal_team_section": {
                        "data_needed": "Identités, adresses, téléphones, IBANs, plaques d'immatriculation, professionnels intervenants.",
                        "tech_stack": "Python, Neo4j (Base de données Graphe) ou NetworkX, algorithmes de détection de communautés (ex: Louvain).",
                        "apis": "Ekinox Graph Engine API.",
                        "key_steps": "1. Modéliser le schéma de graphe (Noeuds: Personnes, Véhicules, Sinistres). 2. Importer les données. 3. Créer des requêtes Cypher pour détecter les cliques et les cycles suspects."
                    }
                },
                {
                    "name": "4. Analyse Sémantique des Déclarations (Text NLP)",
                    "client_section": {
                        "vision": "Déceler le mensonge et l'incohérence dans les récits des assurés.",
                        "value_added": "Exploitation de la donnée non structurée (texte) qui représente 80% de l'information d'un sinistre.",
                        "use_case": "Le NLP analyse la déclaration écrite de l'assuré et la compare au rapport de police ou d'expert. Il relève une contradiction flagrante sur la chronologie de l'accident.",
                        "user_impact": "Les gestionnaires disposent d'un surlignage des éléments suspects pour orienter leur interrogatoire."
                    },
                    "internal_team_section": {
                        "data_needed": "Textes des déclarations, rapports d'experts, constats amiables numérisés.",
                        "tech_stack": "Python, Hugging Face (Modèles NLP Transformers), LangChain pour l'extraction logique.",
                        "apis": "Document OCR API (si besoin), NLP Analysis API.",
                        "key_steps": "1. Traduire les textes en embeddings. 2. Utiliser un LLM pour extraire les entités et événements clés (chronologie). 3. Créer des règles de comparaison logique."
                    }
                },
                {
                    "name": "5. Analyse Forensique des Images (Computer Vision)",
                    "client_section": {
                        "vision": "Détecter les photos falsifiées ou réutilisées dans les déclarations de dommages.",
                        "value_added": "Blocage des fraudes numériques de plus en plus fréquentes.",
                        "use_case": "Un assuré soumet une photo de dégât des eaux. L'IA détecte que la photo provient d'Internet, ou qu'elle a déjà été utilisée pour un autre sinistre 2 ans auparavant grâce à son empreinte numérique.",
                        "user_impact": "Preuve irréfutable de fraude générée instantanément."
                    },
                    "internal_team_section": {
                        "data_needed": "Photos des sinistres passés et actuels, métadonnées (EXIF).",
                        "tech_stack": "Python, OpenCV (pour l'analyse basique et EXIF), Modèles CNN (ResNet) ou modèles pré-entraînés Hugging Face pour l'extraction de features visuelles.",
                        "apis": "Image Forensic API.",
                        "key_steps": "1. Extraire et analyser les métadonnées EXIF (dates, GPS). 2. Hacher les images (Perceptual Hashing) pour trouver les doublons. 3. (V2) Détecter les manipulations (Photoshop)."
                    }
                },
                {
                    "name": "6. Assistant d'Investigation (Fraud Copilot)",
                    "client_section": {
                        "vision": "Augmenter les enquêteurs (SIU - Special Investigation Unit) avec une IA qui synthétise les dossiers complexes.",
                        "value_added": "Réduction de 50% du temps de préparation d'un dossier d'enquête.",
                        "use_case": "Un enquêteur prend un dossier complexe. Le Fraud Copilot lui génère un résumé narratif des suspicions, liste les pièces manquantes et suggère des questions à poser à l'assuré.",
                        "user_impact": "L'enquêteur se concentre sur l'humain et la confrontation, pas sur la compilation de données."
                    },
                    "internal_team_section": {
                        "data_needed": "Dossier sinistre complet (données structurées et non structurées), résultats des autres moteurs Ekinox.",
                        "tech_stack": "Python, LangChain (RAG), Modèle LLM (Llama-3), Interface UI.",
                        "apis": "Ekinox Synthesis API.",
                        "key_steps": "1. Agréger les outputs de tous les scores (ML, Graphe, NLP). 2. Créer un prompt d'investigation system. 3. Générer le rapport via LLM et l'afficher dans l'outil SIU existant."
                    }
                },
                {
                    "name": "7. Boucle de Feedback et Ré-entraînement (Active Learning)",
                    "client_section": {
                        "vision": "Créer un système immunitaire qui apprend en continu des nouvelles techniques des fraudeurs.",
                        "value_added": "Pérennité de l'investissement technologique : le modèle ne devient jamais obsolète.",
                        "use_case": "Suite à une enquête, le gestionnaire confirme qu'un dossier suspect était bien une fraude (ou un faux positif). Cette décision est réinjectée automatiquement pour affiner le modèle ML la nuit suivante.",
                        "user_impact": "Les faux positifs diminuent constamment, la précision augmente."
                    },
                    "internal_team_section": {
                        "data_needed": "Décisions finales des gestionnaires (Feedback data).",
                        "tech_stack": "Python, MLflow (pour le suivi des modèles et l'orchestration du ré-entraînement), Airflow ou Cron.",
                        "apis": "Feedback Collection API, MLOps Pipeline.",
                        "key_steps": "1. Créer une API pour capter le retour (vrai/faux) du CRM. 2. Stocker les feedbacks. 3. Automatiser un pipeline MLflow qui ré-entraîne le modèle XGBoost chaque semaine si le delta de performance est positif."
                    }
                }
            ],
            "roadmap": {
                "phase_1": "Mois 1-3 (Fondation & Fast-Track) : Déploiement des Règles Métier (Capacité 1) et du scoring ML basique (Capacité 2). Impact immédiat sur l'automatisation.",
                "phase_2": "Mois 4-6 (Intelligence Avancée) : Intégration du NLP (Capacité 4) et de la boucle de feedback (Capacité 7).",
                "phase_3": "Mois 7-9 (Réseaux & Investigation) : Analyse de graphes (Capacité 3) et Fraud Copilot (Capacité 6).",
                "phase_4": "Mois 10+ (Innovation) : Analyse d'images (Capacité 5) et consolidation de la plateforme."
            },
            "business_case": {
                "assumptions": "Charge sinistre annuelle (Claims Cost): 100 000 000€. Taux de fraude estimé actuel non détecté: 5% (5M€). Taux de faux positifs actuel: 30%.",
                "impact": "Augmentation du taux de détection de 30% (soit 1,5M€ sauvés). Automatisation (Fast-Track) de 25% des sinistres simples (économie de 500k€ en OPEX).",
                "roi_calculation": "Économies directes sur les sinistres : 1,5M€. Économies de gestion : 500k€. Valeur totale générée : 2M€ / an.",
                "break_even": "Point mort commercial atteint en 5 mois après le déploiement de la Phase 1."
            }
        }
    }
}

with open(r'c:\Projects\Ekinox IA\final_proposals.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

print("JSON file successfully generated at c:\\Projects\\Ekinox IA\\final_proposals.json")
