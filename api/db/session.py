from repository.session import Database
from core.settings import settings

db = Database(settings.DATABASE_URL)
engine = db.engine
async_session_maker = db.session_maker
get_session = db.get_session
