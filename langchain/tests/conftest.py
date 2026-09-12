import os
import pytest

@pytest.fixture(scope="session")
def database_url():
    return os.getenv("DATABASE_URL", "postgresql://pqal:pqal@localhost:5432/pqal")
