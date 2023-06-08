from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

from .mongo import PyObjectId

class CreateTask(BaseModel):
    title: str
    description: str
    assigned_to: str
    created_date: Optional[datetime] = datetime.now()
    completed_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    files: Optional[list[str]] = []
    
class GetTask(CreateTask):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")