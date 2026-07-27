from fastapi import APIRouter, Form, HTTPException
from core import database
from fraud import engine
import datetime

router = APIRouter()

@router.get("/api/fraud/claims")
def get_claims():
    """Retrieve all claims in the Fraud Workspace."""
    return list(database.CLAIMS.values())

@router.get("/api/fraud/claims/{claim_id}")
def get_claim(claim_id: str):
    """Retrieve a single claim details."""
    if claim_id not in database.CLAIMS:
        raise HTTPException(status_code=404, detail="Claim not found")
    return database.CLAIMS[claim_id]

@router.post("/api/fraud/claims/{claim_id}/evaluate")
def evaluate_claim(claim_id: str):
    """Re-evaluate and score a claim for fraud risk."""
    if claim_id not in database.CLAIMS:
        raise HTTPException(status_code=404, detail="Claim not found")
    return engine.evaluate_claim_fraud(claim_id)

@router.get("/api/fraud/knowledge")
def get_fraud_knowledge_base():
    """Retrieve Fraud Knowledge Base entries (Capability 1)."""
    return engine.FRAUD_KNOWLEDGE_BASE

@router.post("/api/fraud/claims/{claim_id}/comment")
def add_comment(claim_id: str, text: str = Form(...), author: str = Form("Enquêteur Fraude")):
    """Add investigation note / log entry."""
    if claim_id not in database.CLAIMS:
        raise HTTPException(status_code=404, detail="Claim not found")
        
    claim = database.CLAIMS[claim_id]
    comment = {
        "author": author,
        "text": text,
        "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    claim["comments"].append(comment)
    return {"status": "success", "comments": claim["comments"]}

@router.post("/api/fraud/claims/{claim_id}/status")
def update_status(claim_id: str, status: str = Form(...)):
    """Update claim status (Enquête, Rejeté, Résolu, Fast-Track)."""
    if claim_id not in database.CLAIMS:
        raise HTTPException(status_code=404, detail="Claim not found")
        
    claim = database.CLAIMS[claim_id]
    claim["status"] = status
    
    # Capitalisation loop simulation:
    # If status is "Résolu" (confirmed fraud), we create a new entry in the Fraud Knowledge Base
    if status == "Résolu":
        new_entry = {
            "id": f"kb-{len(engine.FRAUD_KNOWLEDGE_BASE)+1}",
            "typology": f"Capitalisation Dossier #{claim['id']} ({claim['insured_name']})",
            "modus_operandi": f"Fraude confirmée par l'enquêteur. Circonstances : {claim['circumstances']}.",
            "detection_criteria": claim.get("flags", ["Dossier récurrent"]),
            "jurisprudence": f"Dossier Sanlam #{claim['id']} résolu le {datetime.datetime.now().strftime('%Y-%m-%d')}."
        }
        engine.FRAUD_KNOWLEDGE_BASE.append(new_entry)
        
    return {"status": "success", "status_updated": claim["status"]}

@router.get("/api/fraud/network")
def get_network():
    """Retrieve graph relationship nodes and edges for Network Explorer."""
    return database.NETWORK_DATA
