from pydantic import BaseModel
from enum import Enum

from core import settings

class Roles(str,Enum):
    writer = settings.TASKS_COLLECTION_WRITER_ROLE
    reader = settings.TASKS_COLLECTION_READER_ROLE
    
class CreateUser(BaseModel):
    user: str
    password: str
    role: Roles
        
