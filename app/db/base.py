# Import all the models, so that Base has them before being
# imported by Alembic
from app.db.base_class import Base  # noqa
from app.models import Country  # noqa
from app.models import Event  # noqa
from app.models import Participant  # noqa
