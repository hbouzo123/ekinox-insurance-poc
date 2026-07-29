import os
import json
import urllib.request
import urllib.parse
from datetime import datetime
from core import config

class ORASSClient:
    """Client API Sandbox ORASS (ERP Core Insurance System) avec gestion actuarielle CIMA & scoring du risque."""
    
    def __init__(self, username: str = "afgbenin", password: str = "afgbenin", client_id: str = "orass-sandbox-web"):
        self.username = username
        self.password = password
        self.client_id = client_id
        self.token = None

    def get_candidate_urls(self, endpoint_suffix: str) -> list:
        urls = [
            f"{config.ORASS_REMOTE_URL}{endpoint_suffix}",
            f"{config.ORASS_LOCAL_SANDBOX_URL}{endpoint_suffix}",
            f"http://127.0.0.1:{config.PORT}/api/v1/sandbox{endpoint_suffix}"
        ]
        return list(dict.fromkeys(urls))

    def calculate_risk_score(self, sinistres_2ans: int = 0, usage_code: str = "101", puifisc: int = 7, city: str = "Cotonou") -> dict:
        """Calcul du score de souscription (0 à 100)."""
        score = 10
        city_lower = (city or "").lower()
        
        if sinistres_2ans >= 2:
            score += 50
        elif sinistres_2ans == 1:
            score += 20
            
        if usage_code in ["104", "102"]:
            score += 25
            
        if puifisc >= 14:
            score += 15
            
        level = "ELEVE" if score >= 50 else "STANDARD"
        return {
            "score": score,
            "level": level,
            "requires_agency_visit": (level == "ELEVE")
        }

    def calculate_devis_auto(self, code_cate: str = "101", puifisc: int = 7, codedure: str = "12", bonumalu: float = 80.0, garanties: list = None, city: str = "Cotonou", sinistres_2ans: int = 0, custom_valeur: int = None) -> dict:
        """Calcul de devis auto CIMA avec ventilation détaillée, hypothèses transparentes et ajustement zone."""
        if garanties is None:
            garanties = ["VOL", "INCENDIE", "BRIS_GLACE"]

        city_lower = (city or "").lower()
        is_zone_b = any(v in city_lower for v in ["parakou", "natitingou", "djougou", "bohicon", "kandi", "lokossa", "ouidah"])
        zone_label = "Zone B (Intérieur du Bénin -15%)" if is_zone_b else "Zone A (Cotonou / Littoral)"
        zone_coef = 0.85 if is_zone_b else 1.0

        # Assiette de Valeur (Neuf / Vénale)
        valeur_estimee = custom_valeur if custom_valeur else (puifisc * 1500000)

        # Base RC CIMA Bénin ajustée par Zone & Bonus
        base_rc_brute = 55600 if puifisc <= 7 else 75000
        prime_rc_nette = int(base_rc_brute * zone_coef * (bonumalu / 100.0))

        # Garanties Annexes & Dommages Tous Accidents (3.5% de la Valeur)
        annexes = 45000 if "VOL" in garanties else 25000
        if "DOMMAGES_TOUS_ACCIDENTS" in garanties or "PLATINUM" in [g.upper() for g in garanties]:
            annexes += int(valeur_estimee * 0.035)

        prime_nette = prime_rc_nette + annexes
        accessoires = 5000
        timbres = 1430
        taxe_assu = int(prime_nette * 0.10) # Taxe CIMA 10%
        taxe_fga = int(prime_rc_nette * 0.02) # FGA Bénin 2%
        prime_ttc = prime_nette + accessoires + timbres + taxe_assu + taxe_fga

        nume_quit = f"QUIT-{int(datetime.now().timestamp()) % 1000000}"
        num_devis = f"DEV-{int(datetime.now().timestamp()) % 1000000}"

        risk_data = self.calculate_risk_score(sinistres_2ans=sinistres_2ans, usage_code=code_cate, puifisc=puifisc, city=city)

        return {
            "numdevis": num_devis,
            "codecate": str(code_cate),
            "puifisc": puifisc,
            "codedure": codedure,
            "bonumalu": bonumalu,
            "city": city,
            "valeurEstimee": valeur_estimee,
            "risk": risk_data,
            "assumptions": {
                "valeurNeufOrVenale": f"{valeur_estimee:,} FCFA".replace(",", " "),
                "zoneGeo": zone_label,
                "bonusMalus": f"Bonus 20% (0 sinistre)" if bonumalu <= 80 else f"Malus {int(bonumalu)}%",
                "usage": "101 Promenade & Affaires (Usage Privé)"
            },
            "detail": {
                "primeRcNette": prime_rc_nette,
                "garantiesAnnexes": annexes,
                "primeNetTotale": prime_nette,
                "accessoires": accessoires,
                "timbres": timbres,
                "taxeAssurance": taxe_assu,
                "taxeFga": taxe_fga,
                "primeTtc": prime_ttc
            },
            "quittance": {
                "NUMEQUIT": nume_quit,
                "MONTTTC": prime_ttc,
                "STATQUIT": "PRE_VALIDEE"
            }
        }

    def validate_new_deal_auto(self, assure_nom: str, assure_prenom: str, marque: str, modele: str, immatriculation: str, code_cate: str = "101", duration_months: str = "12") -> dict:
        num_poli = f"POL-AUTO-{int(datetime.now().timestamp()) % 1000000}"
        return {
            "numepoli": num_poli,
            "statut": "VALIDEE_AGENT",
            "dateSouscription": datetime.now().isoformat() + "Z"
        }

# Global Singleton Instance
orass_engine = ORASSClient()
