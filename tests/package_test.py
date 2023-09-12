import pytest

from src.sql_app.database import SessionLocal
from sqlalchemy import inspect
from src.sql_app.database import engine

def test_combined_table_exists():
    inspector = inspect(engine)
    table_name = "suggested-combined-transfers"
    return inspector.has_table(table_name)