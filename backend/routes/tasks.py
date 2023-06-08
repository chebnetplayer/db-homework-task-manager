from fastapi import APIRouter, HTTPException, Depends, UploadFile, Response
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import List, Annotated
from datetime import datetime
import logging
from pymongo import MongoClient
from pymongo.errors import OperationFailure
from bson.objectid import ObjectId

from core import settings
from models import CreateTask, GetTask
from .users import get_mongo_uri

router = APIRouter()
security = HTTPBasic()

@router.post("/tasks")
async def create_task(credentials: Annotated[HTTPBasicCredentials, Depends(security)],
                task: CreateTask):
    with MongoClient(get_mongo_uri(credentials)) as client:
        db = client[settings.DB_NAME]
        try:
            result = db.command({'usersInfo': task.assigned_to})
            if len(result['users']) < 1:
                raise HTTPException(status_code=400, detail="Username not exists")
            result = db[settings.TASKS_COLLECTION].insert_one(task.dict())
            return str(result.inserted_id)
        except OperationFailure as e:
            logging.info(e)
            if e.code == 18:
                raise HTTPException(status_code=401, detail="Authentication failed")
            else:
                logging.info(e)
                raise e
        except HTTPException as e:
            raise HTTPException(status_code=e.status_code, detail=e.detail)
        except Exception as e:
            logging.info(e)
            raise e


@router.get("/tasks")
def get_all_tasks(credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    with MongoClient(get_mongo_uri(credentials)) as client:
        db = client[settings.DB_NAME]
        try:
            result = db[settings.TASKS_COLLECTION].find()
            l=[]
            for i in result:
                i["_id"] = str(i["_id"])
                l.append(i)   
            return l
        except OperationFailure as e:
            logging.info(e)
            if e.code == 18:
                raise HTTPException(status_code=401, detail="Authentication failed")
            else:
                logging.info(e)
                raise e
        except HTTPException as e:
            raise HTTPException(status_code=e.status_code, detail=e.detail)
        except Exception as e:
            logging.info(e)   
            raise e
    


@router.get("/tasks/{task_id}")
def get_task(credentials: Annotated[HTTPBasicCredentials, Depends(security)],
    task_id: str)-> dict:
    with MongoClient(get_mongo_uri(credentials)) as client:
        db = client[settings.DB_NAME]
        try:
            result = db[settings.TASKS_COLLECTION].find_one({"_id": ObjectId(task_id)})
            if result is None:
                raise HTTPException(status_code=404, detail="Task not found")
            result["_id"] = str(result["_id"])
            return result
        except OperationFailure as e:
            logging.info(e)
            if e.code == 18:
                raise HTTPException(status_code=401, detail="Authentication failed")
            else:
                logging.info(e)
                raise e
        except HTTPException as e:
            raise HTTPException(status_code=e.status_code, detail=e.detail)
        except Exception as e:
            logging.info(e)      
            raise e
    


@router.put("/tasks/{task_id}")
def complete(credentials: Annotated[HTTPBasicCredentials, Depends(security)],
    task_id: str):
    with MongoClient(get_mongo_uri(credentials)) as client:
        db = client[settings.DB_NAME]
        try:
            result = db[settings.TASKS_COLLECTION].find_one({"_id": ObjectId(task_id)})
            if not result:
                raise HTTPException(status_code=404, detail="Task not found")
            if result.get("completed_date"):
                raise HTTPException(status_code=400, detail="Task is already closed")
            result = db[settings.TASKS_COLLECTION].update_one({"id": ObjectId(task_id)}, {"$set": {"completed_date": datetime.now()}})
            return {"message": "Task completed successfully"}
        except OperationFailure as e:
            logging.info(e)
            if e.code == 18:
                raise HTTPException(status_code=401, detail="Authentication failed")
            else:
                logging.info(e)
                raise e
        except HTTPException as e:
            raise HTTPException(status_code=e.status_code, detail=e.detail)
        except Exception as e:
            logging.info(e)      
            raise e
    

@router.delete("/tasks/{task_id}")
def delete_task(credentials: Annotated[HTTPBasicCredentials, Depends(security)],
    task_id: str):
    with MongoClient(get_mongo_uri(credentials)) as client:
        db = client[settings.DB_NAME]
        try:
            result = db[settings.TASKS_COLLECTION].delete_one({"_id": ObjectId(task_id)})
            if result.deleted_count == 0:
                raise HTTPException(status_code=404, detail="Task not found")
            return {"message": "Task deleted"}
        except OperationFailure as e:
            logging.info(e)
            if e.code == 18:
                raise HTTPException(status_code=401, detail="Authentication failed")
            else:
                logging.info(e)
                raise e
        except HTTPException as e:
            raise HTTPException(status_code=e.status_code, detail=e.detail)
        except Exception as e:
            logging.info(e)      
            raise e


@router.post("/tasks/{task_id}/upload")
async def upload_file(credentials: Annotated[HTTPBasicCredentials, Depends(security)],
    task_id: str,
    file: UploadFile):
    with MongoClient(get_mongo_uri(credentials)) as client:
        db = client[settings.DB_NAME]
        try:
            contents = await file.read()
            result = db[settings.TASKS_COLLECTION].find_one({"_id": ObjectId(task_id)})
            if result is None:
                raise HTTPException(status_code=404, detail="Task not found")       
            result = db[settings.FILES_COLLECTION].insert_one({"filename": file.filename, "file": contents})
            result = db[settings.TASKS_COLLECTION].update_one({"_id": ObjectId(task_id)}, {"$push": {"files": str(result.inserted_id)}})
            logging.info(result.raw_result)
            return {"message": "added file"}
        except OperationFailure as e:
            logging.info(e)
            if e.code == 18:
                raise HTTPException(status_code=401, detail="Authentication failed")
            else:
                logging.info(e)
                raise e
        except HTTPException as e:
            raise HTTPException(status_code=e.status_code, detail=e.detail)
        except Exception as e:
            logging.info(e)  
            raise e    

@router.get("/tasks/download/{id}")
async def download_file(credentials: Annotated[HTTPBasicCredentials, Depends(security)],
    id: str,
    response: Response):
    with MongoClient(get_mongo_uri(credentials)) as client:
        db = client[settings.DB_NAME]
        try:
            result = db[settings.FILES_COLLECTION].find_one({"_id": ObjectId(id)})
            if result is None:
                raise HTTPException(status_code=404, detail="File not found")       
            
            response.headers["Content-Disposition"] = f"attachment; filename={result['filename']}"
            response.headers["Content-Type"] = "application/octet-stream"

            return result["file"]
        except OperationFailure as e:
            logging.info(e)
            if e.code == 18:
                raise HTTPException(status_code=401, detail="Authentication failed")
            else:
                logging.info(e)
                raise e
        except HTTPException as e:
            raise HTTPException(status_code=e.status_code, detail=e.detail)
        except Exception as e:
            logging.info(e)  
            raise e    
        
@router.get("/count_tasks_by_users")
async def count_tasks_by_users(credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    with MongoClient(get_mongo_uri(credentials)) as client:
        db = client[settings.DB_NAME]
        try:
            result = db[settings.TASKS_COLLECTION].aggregate([{ "$group" : { "_id" : "$assigned_to", "count" : {"$sum" :1 } } }])
            return list(result)
        except OperationFailure as e:
            logging.info(e)
            if e.code == 18:
                raise HTTPException(status_code=401, detail="Authentication failed")
            else:
                logging.info(e)
                raise e
        except HTTPException as e:
            raise HTTPException(status_code=e.status_code, detail=e.detail)
        except Exception as e:
            logging.info(e)  
            raise e    