from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import uvicorn
from pymongo import MongoClient

from core import settings
from routes import task_router, user_router

logging.basicConfig(level=logging.INFO)

app = FastAPI()
app.add_middleware(
 CORSMiddleware,
 allow_origins=["*"],
 allow_credentials=True,
 allow_methods=["*"],
 allow_headers=["*"],
)

app.include_router(task_router)
app.include_router(user_router)

@app.on_event("startup")
def create_roles():
    with MongoClient("mongodb://root:root@mongo") as client:
        db = client[settings.DB_NAME]
        result = db.command({'rolesInfo': {'role': settings.TASKS_COLLECTION_READER_ROLE,'db': settings.DB_NAME}})
        if len(result['roles']) < 1:            
            db.command(
                "createRole", settings.TASKS_COLLECTION_READER_ROLE,
                privileges=[{"resource" : {"role" : "read", "db": settings.DB_NAME, "collection": "tasks"},"actions" : ["find"]}],
                roles = []
            )
        result = db.command({'rolesInfo': {'role': settings.TASKS_COLLECTION_WRITER_ROLE,'db': settings.DB_NAME}})
        if len(result['roles']) < 1:
            db.command(
                "createRole", settings.TASKS_COLLECTION_WRITER_ROLE,
                privileges=[{"resource" : {"role" : "readWrite", "db": settings.DB_NAME, "collection": "tasks"},"actions" : ["find", "update", "insert", "remove"]}],
                roles = []
            )
        db[settings.TASKS_COLLECTION].create_index([("title", "text")])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)