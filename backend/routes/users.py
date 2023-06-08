from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import Annotated, List
import logging
from pymongo import MongoClient
from pymongo.errors import OperationFailure

from core import settings
from models import CreateUser

router = APIRouter()
security = HTTPBasic()


def get_mongo_uri(credentials: HTTPBasicCredentials):
    return "mongodb://{0}:{1}@{2}".format(credentials.username, credentials.password, settings.MONGO)

@router.post("/register")
async def register(credentials: Annotated[HTTPBasicCredentials, Depends(security)], 
             user: CreateUser):
    with MongoClient(get_mongo_uri(credentials)) as client:
        db = client[settings.DB_NAME]
        try:
            result = db.command({'usersInfo': user.user})
            if len(result['users']) > 0:
                raise HTTPException(status_code=400, detail="Username already exists")
            db.command(
                "createUser", user.user,
                pwd=user.password,
                roles=[{
                    "role": user.role.value,
                    "db": settings.DB_NAME
                }]
            )
            return {"message": f"User {user.user} registered successfully"}
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

@router.get("/users")
async def get_users(credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    with MongoClient(get_mongo_uri(credentials)) as client:
        db = client[settings.DB_NAME]
        try:
            result = db.command('usersInfo')
            logging.info(result)
            l=[]
            for i in result['users']:
                l.append(i['user'])    
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