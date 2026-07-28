from fastapi import APIRouter, Form, Body, Header, HTTPException
from datetime import datetime
import random

router = APIRouter()

@router.post("/auth/realms/orass-sandbox/protocol/openid-connect/token")
def get_oidc_token(grant_type: str = Form("password"), client_id: str = Form("orass-sandbox-web"), username: str = Form("afgbenin"), password: str = Form("afgbenin")):
    """OAuth 2.0 / OIDC Token Endpoint pour le Sandbox ORASS."""
    return {
        "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.ORASS_SANDBOX_JWT_LIVE_TOKEN",
        "expires_in": 3600,
        "token_type": "Bearer",
        "scope": "openid profile email"
    }

@router.get("/api/v1/sandbox/catalog")
def get_orass_catalog():
    """Catalogue officiel des 128 scénarios d'API du Sandbox ORASS."""
    return {
        "total_scenarios": 128,
        "domain": "IARD & Vie - CIMA / ACAPS / FANAF",
        "scenarios": [
            {"code": "iard.devis.garantie-calc", "name": "Calcul de devis auto & quittance CIMA", "method": "POST"},
            {"code": "iard.new-deal.validate-auto", "name": "Émission & Validation de police auto", "method": "POST"},
            {"code": "iard.sinistre.declaration", "name": "Déclaration et ouverture de dossier de sinistre", "method": "POST"},
            {"code": "iard.contrat.recherche", "name": "Recherche de contrat par immatriculation / CNI", "method": "GET"}
        ]
    }

@router.post("/api/v1/sandbox/iard/devis/garantie-calc")
def calculate_orass_devis(payload: dict = Body(...), authorization: str = Header(None)):
    """API Métier ORASS : Calcul de prime auto & génération de quittance CIMA."""
    code_cate = str(payload.get("CODECATE", "101"))
    puifisc = int(payload.get("PUIFISC", 7))
    codedure = str(payload.get("CODEDURE", "12"))
    bonumalu = float(payload.get("BONUMALU", 80.0))
    garanties = payload.get("GARANTIES", ["VOL", "INCENDIE", "BRIS_GLACE"])
    
    base_rc = 55600 if puifisc <= 7 else 75000
    annexes = 45000 if "VOL" in garanties else 25000
    prime_nette = int((base_rc * (bonumalu / 100.0)) + annexes)
    accessoires = 5000
    timbres = 1200
    taxe_assu = int(prime_nette * 0.12)
    taxe_fga = int(prime_nette * 0.015)
    prime_ttc = prime_nette + accessoires + timbres + taxe_assu + taxe_fga
    
    nume_quit = f"QUIT-{random.randint(700000, 999999)}"
    
    return {
        "data": {
            "codecate": code_cate,
            "puifisc": puifisc,
            "codedure": codedure,
            "bonumalu": bonumalu,
            "detail": {
                "primeRcNette": base_rc,
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
                "STATQUIT": "EMISE"
            }
        },
        "error": False,
        "message": "Calcul de prime exécuté avec succès par le Sandbox ORASS"
    }

@router.post("/api/v1/sandbox/iard/new-deal/validate-auto")
def validate_orass_policy(payload: dict = Body(...), authorization: str = Header(None)):
    """API Métier ORASS : Émission & Validation de police auto."""
    police = payload.get("police", {})
    assure = payload.get("assure", {})
    risque = payload.get("risque", {})
    
    num_poli = f"POL-AUTO-{random.randint(800000, 999999)}"
    
    return {
        "data": {
            "numepoli": num_poli,
            "statut": "VALIDEE",
            "dateSouscription": datetime.now().isoformat() + "Z",
            "assure": assure,
            "vehicule": risque
        },
        "error": False,
        "message": "Police d'assurance auto validée et émise dans le Sandbox ORASS"
    }
