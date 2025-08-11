from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from datetime import datetime
import uuid
import secrets
import string
import logging
from ..models import Meeting, MeetingCreate, RecoveryRequest, OrganizerHeartbeat, Participant, Poll
from ..services.db import db
from ..services.connection import manager
from ..services.polls import update_poll_results
from ..services.report import generate_pdf_report

router = APIRouter()
logger = logging.getLogger(__name__)

# Meeting endpoints
@router.post("/meetings", response_model=Meeting)
async def create_meeting(meeting_data: MeetingCreate):
    # Validation des champs obligatoires
    if not meeting_data.title or not meeting_data.title.strip():
        raise HTTPException(status_code=400, detail="Le titre de la réunion est requis")
    if not meeting_data.organizer_name or not meeting_data.organizer_name.strip():
        raise HTTPException(status_code=400, detail="Le nom de l'organisateur est requis")
    
    # Limitation de la longueur des champs
    if len(meeting_data.title.strip()) > 200:
        raise HTTPException(status_code=400, detail="Le titre de la réunion ne peut pas dépasser 200 caractères")
    if len(meeting_data.organizer_name.strip()) > 100:
        raise HTTPException(status_code=400, detail="Le nom de l'organisateur ne peut pas dépasser 100 caractères")
    
    meeting = Meeting(
        title=meeting_data.title.strip(),
        organizer_name=meeting_data.organizer_name.strip(),
        organizer_timezone=meeting_data.organizer_timezone  # Stocker le fuseau horaire
    )
    await db.meetings.insert_one(meeting.dict())
    return meeting

@router.post("/meetings/{meeting_id}/generate-recovery")
async def generate_recovery_url(meeting_id: str):
    """Générer une URL de récupération avec mot de passe pour l'organisateur"""
    meeting = await db.meetings.find_one({"id": meeting_id})
    if not meeting:
        raise HTTPException(status_code=404, detail="Réunion non trouvée")
    
    # Générer un mot de passe aléatoire
    import secrets
    import string
    alphabet = string.ascii_letters + string.digits
    recovery_password = ''.join(secrets.choice(alphabet) for _ in range(12))
    
    # Générer l'URL de récupération
    recovery_code = str(uuid.uuid4())
    recovery_url = f"/recover/{recovery_code}"
    
    # Mettre à jour la réunion
    await db.meetings.update_one(
        {"id": meeting_id},
        {"$set": {
            "recovery_url": recovery_url,
            "recovery_password": recovery_password
        }}
    )
    
    # Stocker les informations de récupération
    await db.recovery_sessions.insert_one({
        "id": str(uuid.uuid4()),
        "recovery_code": recovery_code,
        "meeting_id": meeting_id,
        "password": recovery_password,
        "created_at": datetime.utcnow(),
        "expires_at": datetime.utcnow().replace(hour=23, minute=59, second=59, microsecond=999999)  # Expire à la fin de la journée
    })
    
    return {
        "recovery_url": recovery_url,
        "recovery_password": recovery_password,
        "message": "URL de récupération générée avec succès"
    }

@router.post("/meetings/recover")
async def recover_meeting_access(recovery_data: RecoveryRequest):
    """Récupérer l'accès à une réunion avec l'URL et le mot de passe"""
    # Extraire le code de récupération de l'URL
    recovery_code = recovery_data.meeting_id.replace("/recover/", "")
    
    # Vérifier la session de récupération
    recovery_session = await db.recovery_sessions.find_one({
        "recovery_code": recovery_code,
        "expires_at": {"$gt": datetime.utcnow()}
    })
    
    if not recovery_session:
        raise HTTPException(status_code=404, detail="Lien de récupération invalide ou expiré")
    
    if recovery_session["password"] != recovery_data.password:
        raise HTTPException(status_code=403, detail="Mot de passe incorrect")
    
    # Récupérer la réunion
    meeting = await db.meetings.find_one({"id": recovery_session["meeting_id"]})
    if not meeting:
        raise HTTPException(status_code=404, detail="Réunion non trouvée")
    
    # Marquer l'organisateur comme présent et mettre à jour la dernière activité
    await db.meetings.update_one(
        {"id": recovery_session["meeting_id"]},
        {"$set": {
            "organizer_present": True,
            "organizer_last_seen": datetime.utcnow(),
            "leadership_transferred_to": None
        }}
    )
    
    return {
        "meeting": Meeting(**meeting),
        "message": "Accès récupéré avec succès"
    }

@router.post("/meetings/{meeting_id}/heartbeat")
async def organizer_heartbeat(meeting_id: str, heartbeat_data: OrganizerHeartbeat):
    """Signal de vie de l'organisateur"""
    meeting = await db.meetings.find_one({"id": meeting_id})
    if not meeting:
        raise HTTPException(status_code=404, detail="Réunion non trouvée")
    
    # Vérifier que c'est bien l'organisateur ou le scrutateur ayant reçu le leadership
    if (meeting["organizer_name"] != heartbeat_data.organizer_name and 
        meeting.get("leadership_transferred_to") != heartbeat_data.organizer_name):
        raise HTTPException(status_code=403, detail="Non autorisé")
    
    # Mettre à jour la présence
    await db.meetings.update_one(
        {"id": meeting_id},
        {"$set": {
            "organizer_present": True,
            "organizer_last_seen": datetime.utcnow(),
            "auto_deletion_scheduled": None  # Annuler la suppression automatique
        }}
    )
    
    return {"status": "heartbeat_received"}

@router.get("/meetings/{meeting_id}/can-close")
async def can_close_meeting(meeting_id: str):
    """Vérifier si la réunion peut être fermée (rapport téléchargé)"""
    meeting = await db.meetings.find_one({"id": meeting_id})
    if not meeting:
        raise HTTPException(status_code=404, detail="Réunion non trouvée")
    
    return {
        "can_close": meeting.get("report_downloaded", False),
        "reason": "Rapport déjà téléchargé" if meeting.get("report_downloaded", False) else "Le rapport doit être téléchargé avant de fermer la réunion"
    }

@router.get("/meetings/{meeting_id}/partial-report")
async def generate_partial_report(meeting_id: str):
    """Générer un rapport partiel quand l'organisateur est absent"""
    meeting = await db.meetings.find_one({"id": meeting_id})
    if not meeting:
        raise HTTPException(status_code=404, detail="Réunion non trouvée")
    
    # Vérifier que l'organisateur est bien absent
    if meeting.get("organizer_present", True):
        raise HTTPException(status_code=400, detail="Rapport partiel disponible seulement quand l'organisateur est absent")
    
    # Générer le rapport partiel (sans supprimer les données)
    participants = await db.participants.find({"meeting_id": meeting_id}).to_list(1000)
    scrutators = await db.scrutators.find({"meeting_id": meeting_id}).to_list(1000)
    polls = await db.polls.find({"meeting_id": meeting_id}).to_list(1000)
    
    # Mettre à jour les résultats des sondages
    for poll in polls:
        await update_poll_results(poll["id"])
    
    updated_polls = await db.polls.find({"meeting_id": meeting_id}).to_list(1000)
    
    try:
        # Générer le PDF avec mention "RAPPORT PARTIEL"
        meeting_data = meeting.copy()
        meeting_data["title"] = f"[RAPPORT PARTIEL] {meeting_data['title']}"
        
        pdf_path = generate_pdf_report(meeting_data, participants, updated_polls, scrutators)
        
        safe_title = "".join(c for c in meeting['title'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"Rapport_Partiel_{safe_title}_{meeting['meeting_code']}.pdf"
        
        return FileResponse(
            path=pdf_path,
            filename=filename,
            media_type='application/pdf',
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        logger.error(f"Error generating partial report for meeting {meeting_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la génération du rapport partiel: {str(e)}")

@router.get("/meetings/{meeting_code}")
async def get_meeting_by_code(meeting_code: str):
    meeting = await db.meetings.find_one({"meeting_code": meeting_code, "status": "active"})
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return Meeting(**meeting)

@router.get("/meetings/{meeting_id}/organizer")
async def get_meeting_organizer_view(meeting_id: str):
    meeting = await db.meetings.find_one({"id": meeting_id})
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    # Get participants
    participants = await db.participants.find({"meeting_id": meeting_id}).to_list(1000)
    
    # Get polls
    polls = await db.polls.find({"meeting_id": meeting_id}).to_list(1000)
    
    return {
        "meeting": Meeting(**meeting),
        "participants": [Participant(**p) for p in participants],
        "polls": [Poll(**poll) for poll in polls]
    }

