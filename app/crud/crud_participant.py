from app.crud.base import CRUDBase
from app.models.participant import Participant
from app.schemas.participant import ParticipantCreate, ParticipantUpdate


class CRUDParticipant(CRUDBase[Participant, ParticipantCreate, ParticipantUpdate]):
    pass


participant = CRUDParticipant(Participant)
