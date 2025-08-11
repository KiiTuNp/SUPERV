import asyncio
from datetime import datetime
from fastapi import APIRouter, HTTPException
from ..models import Poll, PollCreate, PollOption, PollStatus, Vote, VoteCreate
from ..services.db import db
from ..services.connection import manager
from ..services.polls import update_poll_results
from ..services.locks import vote_locks, lock_manager

router = APIRouter()

# Poll endpoints
@router.post("/meetings/{meeting_id}/polls", response_model=Poll)
async def create_poll(meeting_id: str, poll_data: PollCreate):
    # Validation des champs obligatoires
    if not poll_data.question or not poll_data.question.strip():
        raise HTTPException(status_code=400, detail="La question du sondage est requise")
    if not poll_data.options or len(poll_data.options) < 2:
        raise HTTPException(status_code=400, detail="Au moins 2 options sont requises")
    
    # Validation des options
    clean_options = []
    for i, option in enumerate(poll_data.options):
        if not option or not option.strip():
            raise HTTPException(status_code=400, detail=f"L'option {i+1} ne peut pas être vide")
        if len(option.strip()) > 200:
            raise HTTPException(status_code=400, detail=f"L'option {i+1} ne peut pas dépasser 200 caractères")
        clean_options.append(option.strip())
    
    # Limitation du nombre d'options
    if len(clean_options) > 20:
        raise HTTPException(status_code=400, detail="Maximum 20 options par sondage")
    
    # Vérifier les doublons
    if len(set(clean_options)) != len(clean_options):
        raise HTTPException(status_code=400, detail="Les options doivent être uniques")
    
    # Verify meeting exists
    meeting = await db.meetings.find_one({"id": meeting_id})
    if not meeting:
        raise HTTPException(status_code=404, detail="Réunion non trouvée")
    
    options = [PollOption(text=opt) for opt in clean_options]
    poll = Poll(
        meeting_id=meeting_id,
        question=poll_data.question.strip(),
        options=options,
        timer_duration=poll_data.timer_duration
    )
    
    await db.polls.insert_one(poll.dict())
    return poll

@router.post("/polls/{poll_id}/start")
async def start_poll(poll_id: str):
    poll = await db.polls.find_one({"id": poll_id})
    if not poll:
        raise HTTPException(status_code=404, detail="Poll not found")
    
    update_data = {
        "status": PollStatus.ACTIVE,
        "timer_started_at": datetime.utcnow() if poll.get("timer_duration") else None
    }
    
    await db.polls.update_one({"id": poll_id}, {"$set": update_data})
    
    # Notify participants
    await manager.send_to_meeting({
        "type": "poll_started",
        "poll_id": poll_id
    }, poll["meeting_id"])
    
    return {"status": "started"}

@router.post("/polls/{poll_id}/close")
async def close_poll(poll_id: str):
    poll = await db.polls.find_one({"id": poll_id})
    if not poll:
        raise HTTPException(status_code=404, detail="Poll not found")
    
    await db.polls.update_one({"id": poll_id}, {"$set": {"status": PollStatus.CLOSED}})
    
    # Notify participants
    await manager.send_to_meeting({
        "type": "poll_closed",
        "poll_id": poll_id
    }, poll["meeting_id"])
    
    return {"status": "closed"}

@router.get("/meetings/{meeting_id}/polls")
async def get_meeting_polls(meeting_id: str):
    polls = await db.polls.find({"meeting_id": meeting_id}).to_list(1000)
    return [Poll(**poll) for poll in polls]

@router.get("/meetings/{meeting_id}/polls/participant")
async def get_meeting_polls_for_participant(meeting_id: str):
    """Get polls for participants - hide detailed results for active polls"""
    polls = await db.polls.find({"meeting_id": meeting_id}).to_list(1000)
    
    participant_polls = []
    for poll_data in polls:
        poll = Poll(**poll_data)
        
        # Si le sondage n'est pas fermé, masquer les résultats détaillés
        if poll.status != PollStatus.CLOSED:
            # Calculer seulement le nombre total de votes
            total_votes = sum(opt.votes for opt in poll.options)
            
            # Masquer les détails des votes pour chaque option
            masked_options = []
            for option in poll.options:
                masked_option = option.dict()
                masked_option["votes"] = 0  # Masquer le nombre de votes par option
                masked_options.append(PollOption(**masked_option))
            
            # Créer une version masquée du poll
            masked_poll = poll.dict()
            masked_poll["options"] = masked_options
            masked_poll["total_votes_count"] = total_votes  # Ajouter le total seulement
            
            participant_polls.append(masked_poll)
        else:
            # Sondage fermé - afficher tous les résultats
            poll_dict = poll.dict()
            poll_dict["total_votes_count"] = sum(opt.votes for opt in poll.options)
            participant_polls.append(poll_dict)
    
    return participant_polls

# Voting endpoints
@router.post("/votes")
async def submit_vote(vote_data: VoteCreate):
    # Get or create lock for this poll
    async with lock_manager:
        if vote_data.poll_id not in vote_locks:
            vote_locks[vote_data.poll_id] = asyncio.Lock()
        poll_lock = vote_locks[vote_data.poll_id]
    
    # Use lock to prevent concurrent vote updates
    async with poll_lock:
        # Verify poll exists and is active
        poll = await db.polls.find_one({"id": vote_data.poll_id})
        if not poll:
            raise HTTPException(status_code=404, detail="Sondage non trouvé")
        
        if poll["status"] != PollStatus.ACTIVE:
            raise HTTPException(status_code=400, detail="Le sondage n'est pas actif")
        
        # Check if option exists
        option_exists = any(opt["id"] == vote_data.option_id for opt in poll["options"])
        if not option_exists:
            raise HTTPException(status_code=400, detail="Option invalide")
        
        # Create anonymous vote
        vote = Vote(poll_id=vote_data.poll_id, option_id=vote_data.option_id)
        await db.votes.insert_one(vote.dict())
        
        # Update poll results immediately in the same transaction
        await update_poll_results(vote_data.poll_id)
        
        # Notify real-time updates
        updated_poll = await db.polls.find_one({"id": vote_data.poll_id})
        await manager.send_to_meeting({
            "type": "vote_submitted",
            "poll": Poll(**updated_poll).dict()
        }, poll["meeting_id"])
        
        return {"status": "vote_submitted", "message": "Vote enregistré avec succès"}


@router.get("/polls/{poll_id}/results")
async def get_poll_results(poll_id: str):
    poll = await db.polls.find_one({"id": poll_id})
    if not poll:
        raise HTTPException(status_code=404, detail="Poll not found")
    
    await update_poll_results(poll_id)
    updated_poll = await db.polls.find_one({"id": poll_id})
    
    total_votes = sum(opt["votes"] for opt in updated_poll["options"])
    
    results = []
    for option in updated_poll["options"]:
        percentage = (option["votes"] / total_votes * 100) if total_votes > 0 else 0
        results.append({
            "option": option["text"],
            "votes": option["votes"],
            "percentage": round(percentage, 1)
        })
    
    return {
        "question": updated_poll["question"],
        "results": results,
        "total_votes": total_votes
    }

