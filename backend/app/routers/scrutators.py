from fastapi import APIRouter, HTTPException
from datetime import datetime
import uuid
import logging
from ..models import ScrutatorAdd, Scrutator, ScrutatorApproval, ScrutatorStatus, ReportGenerationRequest, ScrutatorReportVote, ScrutatorJoin, Meeting
from ..services.db import db
from ..services.connection import manager

router = APIRouter()
logger = logging.getLogger(__name__)

# Scrutator endpoints
@router.post("/meetings/{meeting_id}/scrutators")
async def add_scrutators(meeting_id: str, scrutator_data: ScrutatorAdd):
    """Ajouter des scrutateurs à une réunion"""
    # Validation des champs obligatoires
    if not scrutator_data.names or len(scrutator_data.names) == 0:
        raise HTTPException(status_code=400, detail="Au moins un nom de scrutateur est requis")
    
    # Validation des noms
    clean_names = []
    for name in scrutator_data.names:
        if not name or not name.strip():
            raise HTTPException(status_code=400, detail="Les noms de scrutateurs ne peuvent pas être vides")
        if len(name.strip()) > 100:
            raise HTTPException(status_code=400, detail="Les noms ne peuvent pas dépasser 100 caractères")
        clean_names.append(name.strip())
    
    # Vérifier les doublons
    if len(set(clean_names)) != len(clean_names):
        raise HTTPException(status_code=400, detail="Les noms de scrutateurs doivent être uniques")
    
    # Vérifier que la réunion existe
    meeting = await db.meetings.find_one({"id": meeting_id})
    if not meeting:
        raise HTTPException(status_code=404, detail="Réunion non trouvée")
    
    # Générer un code spécial pour les scrutateurs (différent du code de réunion)
    scrutator_code = f"SC{str(uuid.uuid4())[:6].upper()}"
    
    # Mettre à jour la réunion avec les scrutateurs et le code spécial
    await db.meetings.update_one(
        {"id": meeting_id},
        {"$set": {
            "scrutators": clean_names,
            "scrutator_code": scrutator_code
        }}
    )
    
    # Ajouter les scrutateurs dans la collection scrutators pour traçabilité
    scrutator_docs = []
    for name in clean_names:
        scrutator = Scrutator(name=name, meeting_id=meeting_id)
        scrutator_docs.append(scrutator.dict())
    
    if scrutator_docs:
        await db.scrutators.insert_many(scrutator_docs)
    
    return {
        "scrutator_code": scrutator_code,
        "scrutators": clean_names,
        "message": f"Code de scrutateur généré : {scrutator_code}"
    }

@router.get("/meetings/{meeting_id}/scrutators")
async def get_meeting_scrutators(meeting_id: str):
    """Obtenir la liste des scrutateurs d'une réunion"""
    meeting = await db.meetings.find_one({"id": meeting_id})
    if not meeting:
        raise HTTPException(status_code=404, detail="Réunion non trouvée")
    
    scrutators = await db.scrutators.find({"meeting_id": meeting_id}).to_list(100)
    
    return {
        "scrutator_code": meeting.get("scrutator_code"),
        "scrutators": [Scrutator(**s) for s in scrutators]
    }

@router.post("/scrutators/{scrutator_id}/approve")
async def approve_scrutator(scrutator_id: str, approval: ScrutatorApproval):
    """Approuver ou rejeter un scrutateur"""
    scrutator = await db.scrutators.find_one({"id": scrutator_id})
    if not scrutator:
        raise HTTPException(status_code=404, detail="Scrutateur non trouvé")
    
    new_status = ScrutatorStatus.APPROVED if approval.approved else ScrutatorStatus.REJECTED
    update_data = {
        "approval_status": new_status,
        "approved_at": datetime.utcnow() if approval.approved else None
    }
    
    await db.scrutators.update_one(
        {"id": scrutator_id},
        {"$set": update_data}
    )
    
    # Notify via WebSocket
    await manager.send_to_meeting({
        "type": "scrutator_approved",
        "scrutator_id": scrutator_id,
        "scrutator_name": scrutator["name"],
        "status": new_status
    }, scrutator["meeting_id"])
    
    return {"status": "success", "new_status": new_status}

@router.post("/meetings/{meeting_id}/request-report")
async def request_report_generation(meeting_id: str, request_data: ReportGenerationRequest):
    """Génération directe du rapport - plus d'approbation des scrutateurs nécessaire"""
    
    # Vérifier que la réunion existe
    meeting = await db.meetings.find_one({"id": meeting_id})
    if not meeting:
        raise HTTPException(status_code=404, detail="Réunion non trouvée")
    
    # GÉNÉRATION DIRECTE - plus besoin d'approbation des scrutateurs
    return {"direct_generation": True, "message": "Génération directe du rapport autorisée"}

@router.post("/meetings/{meeting_id}/scrutator-vote")
async def submit_scrutator_vote(meeting_id: str, vote_data: ScrutatorReportVote):
    """Voter pour la génération du rapport en tant que scrutateur"""
    
    # Vérifier que la réunion existe et qu'une demande est en cours
    meeting = await db.meetings.find_one({"id": meeting_id})
    if not meeting:
        raise HTTPException(status_code=404, detail="Réunion non trouvée")
    
    if not meeting.get("report_generation_pending", False):
        raise HTTPException(status_code=400, detail="Aucune demande de génération en cours")
    
    # Vérifier que le scrutateur est approuvé
    scrutator = await db.scrutators.find_one({
        "meeting_id": meeting_id,
        "name": vote_data.scrutator_name,
        "approval_status": "approved"
    })
    if not scrutator:
        raise HTTPException(status_code=403, detail="Scrutateur non autorisé")
    
    # Enregistrer le vote
    current_votes = meeting.get("report_votes", {})
    current_votes[vote_data.scrutator_name] = vote_data.approved
    
    await db.meetings.update_one(
        {"id": meeting_id},
        {"$set": {"report_votes": current_votes}}
    )
    
    # Vérifier si tous les scrutateurs ont voté ou si la majorité est atteinte
    approved_scrutators = await db.scrutators.find({
        "meeting_id": meeting_id,
        "approval_status": "approved"
    }).to_list(100)
    
    total_scrutators = len(approved_scrutators)
    votes_cast = len(current_votes)
    yes_votes = sum(1 for vote in current_votes.values() if vote)
    no_votes = votes_cast - yes_votes
    majority_needed = (total_scrutators // 2) + 1
    
    # Notifier le vote
    await manager.send_to_meeting({
        "type": "scrutator_vote_submitted",
        "scrutator_name": vote_data.scrutator_name,
        "vote": vote_data.approved,
        "votes_cast": votes_cast,
        "total_scrutators": total_scrutators,
        "yes_votes": yes_votes,
        "no_votes": no_votes,
        "majority_needed": majority_needed
    }, meeting_id)
    
    # Vérifier si la décision est prise
    if yes_votes >= majority_needed:
        # Majorité atteinte - approuver la génération
        await db.meetings.update_one(
            {"id": meeting_id},
            {"$set": {
                "report_generation_pending": False,
                "report_generation_approved": True
            }}
        )
        
        await manager.send_to_meeting({
            "type": "report_generation_approved",
            "yes_votes": yes_votes,
            "majority_needed": majority_needed
        }, meeting_id)
        
        return {
            "decision": "approved",
            "yes_votes": yes_votes,
            "majority_needed": majority_needed,
            "message": "Génération du rapport approuvée par la majorité"
        }
    
    elif no_votes >= majority_needed:
        # Majorité contre - rejeter la génération
        await db.meetings.update_one(
            {"id": meeting_id},
            {"$set": {
                "report_generation_pending": False,
                "report_generation_approved": False
            }}
        )
        
        await manager.send_to_meeting({
            "type": "report_generation_rejected",
            "no_votes": no_votes,
            "majority_needed": majority_needed
        }, meeting_id)
        
        return {
            "decision": "rejected",
            "no_votes": no_votes,
            "majority_needed": majority_needed,
            "message": "Génération du rapport rejetée par la majorité"
        }
    
    else:
        # Attendre plus de votes
        return {
            "decision": "pending",
            "votes_cast": votes_cast,
            "total_scrutators": total_scrutators,
            "yes_votes": yes_votes,
            "no_votes": no_votes,
            "majority_needed": majority_needed,
            "message": f"En attente de {majority_needed - max(yes_votes, no_votes)} vote(s) supplémentaire(s)"
        }


@router.post("/scrutators/join")
async def join_as_scrutator(join_data: ScrutatorJoin):
    """Rejoindre une réunion en tant que scrutateur (avec approbation requise)"""
    # Validation des champs obligatoires
    if not join_data.name or not join_data.name.strip():
        raise HTTPException(status_code=400, detail="Le nom du scrutateur est requis")
    if not join_data.scrutator_code or not join_data.scrutator_code.strip():
        raise HTTPException(status_code=400, detail="Le code de scrutateur est requis")
    
    clean_name = join_data.name.strip()
    clean_code = join_data.scrutator_code.strip().upper()
    
    # Vérifier que le code de scrutateur existe
    meeting = await db.meetings.find_one({"scrutator_code": clean_code, "status": "active"})
    if not meeting:
        raise HTTPException(status_code=404, detail="Code de scrutateur invalide ou réunion inactive")
    
    # Vérifier que le nom est dans la liste des scrutateurs autorisés
    if clean_name not in meeting.get("scrutators", []):
        raise HTTPException(status_code=403, detail="Nom non autorisé pour cette réunion en tant que scrutateur")
    
    # Vérifier si le scrutateur existe déjà dans la base
    existing_scrutator = await db.scrutators.find_one({
        "meeting_id": meeting["id"],
        "name": clean_name
    })
    
    if existing_scrutator:
        # Le scrutateur existe déjà - accès direct (plus d'approbation nécessaire)
        # Mettre à jour le statut à approved si nécessaire
        if existing_scrutator["approval_status"] != "approved":
            await db.scrutators.update_one(
                {"meeting_id": meeting["id"], "name": clean_name},
                {"$set": {"approval_status": "approved", "approved_at": datetime.utcnow()}}
            )
        
        return {
            "meeting": Meeting(**meeting),
            "scrutator_name": clean_name,
            "access_type": "scrutator",
            "status": "approved"
        }
    else:
        # Nouveau scrutateur - ACCÈS DIRECT sans approbation
        scrutator = Scrutator(
            name=clean_name, 
            meeting_id=meeting["id"],
            approval_status=ScrutatorStatus.APPROVED,  # Approuvé automatiquement
            approved_at=datetime.utcnow()
        )
        await db.scrutators.insert_one(scrutator.dict())
        
        # Notifier l'organisateur (information seulement, pas de demande d'approbation)
        await manager.send_to_meeting({
            "type": "scrutator_joined",  # Changé de "join_request" à "joined"
            "scrutator": scrutator.dict(),
            "message": f"Le scrutateur {clean_name} a rejoint la réunion"
        }, meeting["id"])
        
        return {
            "meeting": Meeting(**meeting),
            "scrutator_name": clean_name,
            "access_type": "scrutator", 
            "status": "approved"
        }

