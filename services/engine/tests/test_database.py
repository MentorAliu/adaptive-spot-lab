from sqlalchemy import inspect

from app.db import database_ready, get_engine


def test_migrated_database_is_ready():
    assert database_ready()
    assert "system_metadata" in inspect(get_engine()).get_table_names()
