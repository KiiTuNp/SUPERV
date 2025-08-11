import asyncio
from datetime import datetime
import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from ..models import MeetingStatus
from ..services.db import db
from ..services.connection import manager
from ..services.polls import update_poll_results
from ..services.report import generate_pdf_report

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/meetings/{meeting_id}/report")
async def generate_meeting_report(meeting_id: str):
    """Generate and download PDF report - GÉNÉRATION DIRECTE sans approbation scrutateurs"""
    
    # Get meeting data
    meeting = await db.meetings.find_one({"id": meeting_id})
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    # GÉNÉRATION DIRECTE - Plus de vérification d'approbation des scrutateurs
    # Get participants data
    participants = await db.participants.find({"meeting_id": meeting_id}).to_list(1000)
    
    # Get scrutators data
    scrutators = await db.scrutators.find({"meeting_id": meeting_id}).to_list(1000)
    
    # Get polls data with updated results
    polls = await db.polls.find({"meeting_id": meeting_id}).to_list(1000)
    
    # Update all poll results before generating report
    for poll in polls:
        await update_poll_results(poll["id"])
    
    # Get updated polls with final results
    updated_polls = await db.polls.find({"meeting_id": meeting_id}).to_list(1000)
    
    try:
        # Generate PDF with scrutators data
        pdf_path = generate_pdf_report(meeting, participants, updated_polls, scrutators)
        
        # Create filename
        safe_title = "".join(c for c in meeting['title'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"Rapport_{safe_title}_{meeting['meeting_code']}.pdf"
        
        # Mark meeting as completed BEFORE deletion (for logging purposes)
        await db.meetings.update_one(
            {"id": meeting_id},
            {"$set": {
                "status": MeetingStatus.COMPLETED, 
                "completed_at": datetime.utcnow(),
                "report_downloaded": True  # Marquer le rapport comme téléchargé
            }}
        )
        
        # Delete all associated data after PDF generation
        # Delete votes first (they reference polls)
        poll_ids = [poll["id"] for poll in updated_polls]
        if poll_ids:
            delete_votes_result = await db.votes.delete_many({"poll_id": {"$in": poll_ids}})
            logger.info(f"Deleted {delete_votes_result.deleted_count} votes for meeting {meeting_id}")
        
        # Delete polls
        delete_polls_result = await db.polls.delete_many({"meeting_id": meeting_id})
        logger.info(f"Deleted {delete_polls_result.deleted_count} polls for meeting {meeting_id}")
        
        # Delete participants
        delete_participants_result = await db.participants.delete_many({"meeting_id": meeting_id})
        logger.info(f"Deleted {delete_participants_result.deleted_count} participants for meeting {meeting_id}")
        
        # Delete scrutators
        delete_scrutators_result = await db.scrutators.delete_many({"meeting_id": meeting_id})
        logger.info(f"Deleted {delete_scrutators_result.deleted_count} scrutators for meeting {meeting_id}")
        
        # Delete scrutator access records (if any)
        try:
            delete_access_result = await db.scrutator_access.delete_many({"meeting_id": meeting_id})
            logger.info(f"Deleted {delete_access_result.deleted_count} scrutator access records for meeting {meeting_id}")
        except:
            pass  # Collection might not exist
        
        # Notify all participants that the meeting is closed before deleting
        await manager.send_to_meeting({
            "type": "meeting_closed",
            "reason": "report_downloaded",
            "meeting_title": meeting['title'],
            "organizer_name": meeting['organizer_name'],
            "message": "La réunion a été fermée après téléchargement du rapport final. Toutes les données ont été supprimées."
        }, meeting_id)
        
        # Wait a moment to ensure WebSocket message is sent
        await asyncio.sleep(0.5)
        
        # Finally delete the meeting itself
        delete_meeting_result = await db.meetings.delete_one({"id": meeting_id})
        logger.info(f"Deleted meeting {meeting_id}")
        
        logger.info(f"Complete data cleanup finished for meeting {meeting_id}")
        
        # Return the PDF file
        return FileResponse(
            path=pdf_path,
            filename=filename,
            media_type='application/pdf',
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        logger.error(f"Error generating report for meeting {meeting_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")
