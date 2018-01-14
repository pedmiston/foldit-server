from .load import load_from_json
from .db import DB
from .tables import Base

# Create tables that do not exist
Base.metadata.create_all(DB)
