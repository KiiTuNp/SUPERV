from fastapi import APIRouter, HTTPException
from ..models import ParticipantJoin, Participant, ParticipantApproval, ParticipantStatus
from ..services.db import db
from ..services.connection import manager

router = APIRouter()

@router.post("/participants/join")
async def join_meeting(join_data: ParticipantJoin):
    # Validation des champs obligatoires
    if not join_data.name or not join_data.name.strip():
        raise HTTPException(status_code=400, detail="Le nom du participant est requis")
    if not join_data.meeting_code or not join_data.meeting_code.strip():
        raise HTTPException(status_code=400, detail="Le code de réunion est requis")
    
    # Limitation de la longueur et format
    if len(join_data.name.strip()) > 100:
        raise HTTPException(status_code=400, detail="Le nom ne peut pas dépasser 100 caractères")
    if len(join_data.meeting_code.strip()) != 8:
        raise HTTPException(status_code=400, detail="Le code de réunion doit faire 8 caractères")
    
    clean_name = join_data.name.strip()
    clean_code = join_data.meeting_code.strip().upper()
    
    # Check if meeting exists and is active
    meeting = await db.meetings.find_one({"meeting_code": clean_code, "status": "active"})
    if not meeting:
        raise HTTPException(status_code=404, detail="Réunion non trouvée ou inactive")
    
    # Check if participant name already exists in this meeting
    existing = await db.participants.find_one({
        "name": clean_name, 
        "meeting_id": meeting["id"]
    })
    if existing:
        raise HTTPException(status_code=400, detail="Ce nom est déjà pris dans cette réunion")
    
    participant = Participant(name=clean_name, meeting_id=meeting["id"])
    await db.participants.insert_one(participant.dict())
    
    # Notify organizer via WebSocket
    await manager.send_to_meeting({
        "type": "participant_joined",
        "participant": participant.dict()
    }, meeting["id"])
    
    return participant

@router.post("/participants/{participant_id}/approve")
async def approve_participant(participant_id: str, approval: ParticipantApproval):
    participant = await db.participants.find_one({"id": participant_id})
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")
    
    new_status = ParticipantStatus.APPROVED if approval.approved else ParticipantStatus.REJECTED
    await db.participants.update_one(
        {"id": participant_id},
        {"$set": {"approval_status": new_status}}
    )
    
    # Notify via WebSocket
    await manager.send_to_meeting({
        "type": "participant_approved",
        "participant_id": participant_id,
        "status": new_status
    }, participant["meeting_id"])
    
    return {"status": "success"}

@router.get("/participants/{participant_id}/status")
async def get_participant_status(participant_id: str):
    participant = await db.participants.find_one({"id": participant_id})
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")
    return {"status": participant["approval_status"]}

