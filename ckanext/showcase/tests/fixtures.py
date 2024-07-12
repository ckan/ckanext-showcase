import pytest

import ckan.model as model
from ckan.plugins import toolkit


@pytest.fixture
def clean_db(reset_db, migrate_db_for):
    reset_db()
    migrate_db_for("showcase")


@pytest.fixture
def clean_session():
    if toolkit.check_ckan_version(max_version="2.9.0"):
        if hasattr(model.Session, "revision"):
            model.Session.revision = None
