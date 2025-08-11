from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict
from pydantic import BaseModel, Field
import uuid

# Enums
class ParticipantStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved" 
    REJECTED = "rejected"

class PollStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    CLOSED = "closed"

class MeetingStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"

# Models
class ScrutatorStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class Scrutator(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    meeting_id: str
    approval_status: ScrutatorStatus = ScrutatorStatus.PENDING
    added_at: datetime = Field(default_factory=datetime.utcnow)
    approved_at: Optional[datetime] = None

class ScrutatorApproval(BaseModel):
    scrutator_id: str
    approved: bool

class ReportGenerationRequest(BaseModel):
    meeting_id: str
    requested_by: str  # organizer name

class ScrutatorReportVote(BaseModel):
    meeting_id: str
    scrutator_name: str
    approved: bool  # True = autorise, False = refuse

class Meeting(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    organizer_name: str
    organizer_timezone: Optional[str] = None  # Fuseau horaire de l'organisateur (ex: "Europe/Paris")
    meeting_code: str = Field(default_factory=lambda: str(uuid.uuid4())[:8].upper())
    scrutator_code: Optional[str] = None  # Code spécial pour les scrutateurs
    scrutators: List[str] = Field(default_factory=list)  # Liste des noms de scrutateurs
    report_generation_pending: bool = False  # Demande de génération en cours
    report_generation_approved: bool = False  # Génération approuvée par majorité
    report_votes: Dict[str, bool] = Field(default_factory=dict)  # Votes des scrutateurs {nom: vote}
    report_downloaded: bool = False  # Suivi du téléchargement du rapport
    recovery_url: Optional[str] = None  # URL de récupération
    recovery_password: Optional[str] = None  # Mot de passe de récupération
    organizer_last_seen: datetime = Field(default_factory=datetime.utcnow)  # Dernière activité organisateur
    organizer_present: bool = True  # Présence organisateur
    leadership_transferred_to: Optional[str] = None  # Nom du scrutateur ayant reçu le leadership
    auto_deletion_scheduled: Optional[datetime] = None  # Suppression automatique programmée
    status: MeetingStatus = MeetingStatus.ACTIVE
    created_at: datetime = Field(default_factory=datetime.utcnow)

class MeetingCreate(BaseModel):
    title: str
    organizer_name: str
    organizer_timezone: Optional[str] = None  # Fuseau horaire détecté automatiquement

class RecoveryRequest(BaseModel):
    meeting_id: str
    password: str

class OrganizerHeartbeat(BaseModel):
    meeting_id: str
    organizer_name: str

class Participant(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    meeting_id: str
    approval_status: ParticipantStatus = ParticipantStatus.PENDING
    joined_at: datetime = Field(default_factory=datetime.utcnow)

class ScrutatorAdd(BaseModel):
    names: List[str]  # Liste des noms de scrutateurs à ajouter

class ScrutatorJoin(BaseModel):
    name: str
    scrutator_code: str

class ParticipantJoin(BaseModel):
    name: str
    meeting_code: str

class ParticipantApproval(BaseModel):
    participant_id: str
    approved: bool

class PollOption(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    text: str
    votes: int = 0

class Poll(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    meeting_id: str
    question: str
    options: List[PollOption]
    status: PollStatus = PollStatus.DRAFT
    timer_duration: Optional[int] = None  # in seconds
    timer_started_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class PollCreate(BaseModel):
    question: str
    options: List[str]
    timer_duration: Optional[int] = None

class Vote(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    poll_id: str
    option_id: str
    voted_at: datetime = Field(default_factory=datetime.utcnow)
    # Note: No participant_id to maintain anonymity

class VoteCreate(BaseModel):
    poll_id: str
    option_id: str
