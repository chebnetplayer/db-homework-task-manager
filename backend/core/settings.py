from pydantic import BaseSettings

class Settings(BaseSettings):
    MONGO: str
    DB_NAME: str
    FILES_COLLECTION: str = 'files'
    TASKS_COLLECTION: str = 'tasks'
    TASKS_COLLECTION_READER_ROLE: str = 'tasks_reader'
    TASKS_COLLECTION_WRITER_ROLE: str = 'tasks_writer'
    class Config:
        env_prefix = 'ENV_'

settings = Settings()