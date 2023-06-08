FROM python:slim-buster

WORKDIR /app

RUN pip install pymongo fastapi pydantic uvicorn passlib bcrypt python-multipart

COPY . .