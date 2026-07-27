from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import Response
from core import database, document
from sales import assistant
import csv
import io

router = APIRouter()

@router.get("/api/sales/prospects")
def get_prospects(channel: str = None, status: str = None):
    """Retrieve prospects with channel or status filters (Sales Workspace)."""
    prospects = list(database.PROSPECTS.values())
    if channel:
        prospects = [p for p in prospects if p.get("channel", "").lower() == channel.lower()]
    if status:
        prospects = [p for p in prospects if p.get("intention", "").lower() == status.lower()]
    return prospects

@router.post("/api/sales/chat")
def sales_chat(prospect_id: str = Form(...), message: str = Form(...), channel: str = Form("WhatsApp")):
    """Post a chat message in the simulated omni-channel interface."""
    try:
        result = assistant.handle_sales_conversation(prospect_id, message, channel)
        return {
            "status": "success",
            "reply": result["reply"],
            "state": result["prospect_state"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/sales/upload")
async def sales_upload(prospect_id: str = Form(...), file: UploadFile = File(...)):
    """Upload document (Carte Grise / CNI) for open-source OCR parsing and country detection."""
    if prospect_id not in database.PROSPECTS:
        assistant.handle_sales_conversation(prospect_id, "Document transmis", channel="WhatsApp")
        
    prospect = database.PROSPECTS[prospect_id]
    
    try:
        content = await file.read()
        result = document.process_uploaded_document(file.filename, content)
        
        prospect["document_uploaded"] = True
        prospect["document_name"] = file.filename
        
        ext_data = result["extracted_data"]
        confirmation_msg = f"Document '{file.filename}' analysé avec succès ({result['type']}). "
        confirmation_msg += f"Pays d'origine détecté : {result['country_flag']} {result['country']} ({result['entity']}). "
        
        if "immatriculation" in ext_data:
            confirmation_msg += f"Matricule extraite : **{ext_data['immatriculation']}** ({ext_data.get('marque', '')} {ext_data.get('modele', '')})."
            prospect["vehicle"] = f"{ext_data.get('marque', '')} {ext_data.get('modele', '')} ({ext_data['immatriculation']})"
            
        prospect["conversation"].append({
            "sender": "assistant", 
            "text": f"✅ {confirmation_msg}\n\nContexte pays mis à jour sur {result['country_flag']} **{result['country']}** ! [1️⃣ Obtenir mon Tarif] [2️⃣ Prendre RDV]"
        })
        
        assistant.update_lead_intelligence(prospect, database.COUNTRY_CONFIGS[database.ACTIVE_COUNTRY])
        
        return {
            "status": "success",
            "extracted_info": result,
            "prospect_state": prospect
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/sales/appointment")
def schedule_appointment(prospect_id: str = Form(...), slot_date: str = Form(...), slot_time: str = Form(...)):
    """Schedule callback appointment with human insurance advisor."""
    if prospect_id not in database.PROSPECTS:
        raise HTTPException(status_code=404, detail="Prospect not found")
        
    prospect = database.PROSPECTS[prospect_id]
    appointment_str = f"{slot_date} à {slot_time}"
    prospect["appointment"] = appointment_str
    prospect["next_action"] = f"Rendez-vous téléphonique confirmé pour le {appointment_str}."
    
    confirm_msg = f"🗓️ Votre rendez-vous avec notre conseiller commercial est confirmé pour le **{appointment_str}**. Une notification de rappel vous sera envoyée."
    prospect["conversation"].append({"sender": "assistant", "text": confirm_msg})
    
    return {"status": "success", "appointment": appointment_str, "prospect_state": prospect}

@router.get("/api/sales/export")
def export_prospects_csv():
    """Export prospects pipeline as CSV for commercial reporting."""
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(["ID", "Pays", "Nom", "Téléphone", "Canal", "Véhicule", "Besoin", "Intention", "Pièce Jointe", "Rendez-vous", "Synthèse IA", "Prochaine Action"])
    
    for p in database.PROSPECTS.values():
        writer.writerow([
            p.get("id", ""),
            p.get("country", ""),
            p.get("name", ""),
            p.get("phone", ""),
            p.get("channel", ""),
            p.get("vehicle", ""),
            p.get("need", ""),
            p.get("intention", ""),
            "Oui" if p.get("document_uploaded") else "Non",
            p.get("appointment", "Non planifié"),
            p.get("summary", ""),
            p.get("next_action", "")
        ])
        
    output.seek(0)
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=ekinox_prospects_pipeline.csv"}
    )
