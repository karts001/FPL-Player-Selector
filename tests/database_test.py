import pytest
from dotenv import load_dotenv
import os
from sqlalchemy import inspect
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from fastapi.testclient import TestClient

from src.sql_app.database import Base, get_db
from src.main import app


load_dotenv()
username = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
db_name= os.getenv("DB_NAME")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")

SQLALCHEMY_DATABASE_URL = f"postgresql://{username}:{password}@{db_host}:{db_port}/{db_name}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def session():

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        
@pytest.fixture()
def client(session):

    # Dependency override

    def override_get_db():
        try:

            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)
    
def test_combined_table_exists(session):
    inspector = inspect(engine)
    table_name = "suggested-combined-transfers"
    assert inspector.has_table(table_name)
    
def test_goalkeeper_table_exists(session):
    inspector = inspect(engine)
    table_name = "suggested-goalkeeper-transfers"
    assert inspector.has_table(table_name)
    
def test_defender_table_exists(session):
    inspector = inspect(engine)
    table_name = "suggested-defender-transfers"
    assert inspector.has_table(table_name)
    
def test_midfielder_table_exists(session):
    inspector = inspect(engine)
    table_name = "suggested-midfielder-transfers"
    assert inspector.has_table(table_name)
    
def test_attacker_table_exists(session):
    inspector = inspect(engine)
    table_name = "suggested-attacker-transfers"
    assert inspector.has_table(table_name)
    