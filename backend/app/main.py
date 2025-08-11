import asyncio
import logging
import os
from datetime import datetime, timedelta
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from starlette.middleware.cors import CORSMiddleware

from .routers import meetings, participants, scrutators, polls, reports
from .services.db import client, db
from .services.connection import manager

app = FastAPI()

# Include routers
app.include_router(meetings.router, prefix="/api")
app.include_router(participants.router, prefix="/api")
app.include_router(scrutators.router, prefix="/api")
app.include_router(polls.router, prefix="/api")
app.include_router(reports.router, prefix="/api")

logger = logging.getLogger(__name__)

# Background task to monitor organizer presence and handle automatic cleanup
async def monitor_organizer_presence():
    while True:
        try:
            active_meetings = await db.meetings.find({"status": "active"}).to_list(1000)
            for meeting in active_meetings:
                meeting_id = meeting["id"]
                organizer_last_seen = meeting.get("organizer_last_seen", meeting["created_at"])
                organizer_present = meeting.get("organizer_present", True)
                time_elapsed = datetime.utcnow() - organizer_last_seen
                if time_elapsed.total_seconds() > 300 and organizer_present:
                    await db.meetings.update_one({"id": meeting_id}, {"$set": {"organizer_present": False}})
                    approved_scrutators = await db.scrutators.find({"meeting_id": meeting_id, "approval_status": "approved"}).sort("approved_at", 1).to_list(100)
                    if approved_scrutators:
                        senior_scrutator = approved_scrutators[0]
                        await db.meetings.update_one({"id": meeting_id}, {"$set": {"leadership_transferred_to": senior_scrutator["name"]}})
                        await manager.send_to_meeting({
                            "type": "leadership_transferred",
                            "new_leader": senior_scrutator["name"],
                            "reason": "organizer_absence",
                            "message": f"Leadership transféré à {senior_scrutator['name']} (organisateur absent)"
                        }, meeting_id)
                        logger.info(f"Leadership transferred to {senior_scrutator['name']} for meeting {meeting_id}")
                    else:
                        await manager.send_to_meeting({
                            "type": "organizer_absent",
                            "reason": "no_scrutators",
                            "message": "L'organisateur est absent. Vous pouvez télécharger un rapport partiel. Les données seront supprimées automatiquement."
                        }, meeting_id)
                        deletion_time = datetime.utcnow() + timedelta(hours=12)
                        await db.meetings.update_one({"id": meeting_id}, {"$set": {"auto_deletion_scheduled": deletion_time}})
                auto_deletion = meeting.get("auto_deletion_scheduled")
                if auto_deletion and datetime.utcnow() >= auto_deletion:
                    active_connections = len(manager.active_connections.get(meeting_id, []))
                    if active_connections == 0:
                        await cleanup_meeting_data(meeting_id, "auto_deletion_time_limit")
                        logger.info(f"Auto-deleted meeting {meeting_id} due to time limit and no active connections")
                    else:
                        new_deletion_time = datetime.utcnow() + timedelta(hours=1)
                        await db.meetings.update_one({"id": meeting_id}, {"$set": {"auto_deletion_scheduled": new_deletion_time}})
        except Exception as e:
            logger.error(f"Error in organizer presence monitoring: {str(e)}")
        await asyncio.sleep(60)

async def cleanup_meeting_data(meeting_id: str, reason: str):
    try:
        await manager.send_to_meeting({
            "type": "meeting_auto_deleted",
            "reason": reason,
            "message": "La réunion a été automatiquement supprimée selon les règles de rétention des données."
        }, meeting_id)
        await asyncio.sleep(2)
        await db.votes.delete_many({"poll_id": {"$in": [poll["id"] for poll in await db.polls.find({"meeting_id": meeting_id}).to_list(1000)]}})
        await db.polls.delete_many({"meeting_id": meeting_id})
        await db.participants.delete_many({"meeting_id": meeting_id})
        await db.scrutators.delete_many({"meeting_id": meeting_id})
        await db.recovery_sessions.delete_many({"meeting_id": meeting_id})
        await db.meetings.delete_one({"id": meeting_id})
        logger.info(f"Meeting {meeting_id} completely cleaned up due to {reason}")
    except Exception as e:
        logger.error(f"Error cleaning up meeting {meeting_id}: {str(e)}")

asyncio.create_task(monitor_organizer_presence())

@app.websocket("/ws/meetings/{meeting_id}")
async def websocket_endpoint(websocket: WebSocket, meeting_id: str):
    await manager.connect(websocket, meeting_id)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, meeting_id)

@app.get("/api/health")
async def health_check():
    try:
        await client.admin.command('ping')
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {"database": "connected", "api": "running"}
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

cors_origins = os.environ.get('CORS_ORIGINS', '*').split(',')
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=cors_origins,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
