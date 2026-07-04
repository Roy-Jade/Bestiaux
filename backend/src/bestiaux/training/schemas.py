import uuid
from datetime import datetime

from pydantic import BaseModel

from bestiaux.models.interaction import TrainTarget


class TrainRequest(BaseModel):
    target: TrainTarget


class AssignMentorRequest(BaseModel):
    mentor_id: uuid.UUID


class TrainingStatusResponse(BaseModel):
    slots_available: int
    trainings_done_today: int
    last_trained_at: datetime | None
    pending_training_force: float
    pending_training_beauty: float
    pending_training_size: float
    mentor_id: uuid.UUID | None
    mentor_since: datetime | None
    is_asleep: bool
    woke_up_at: datetime | None
    went_to_sleep_at: datetime | None
