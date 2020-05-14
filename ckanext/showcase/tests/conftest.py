import pytest
from ckanext.showcase.model import setup as showcase_setup


@pytest.fixture
def clean_db(reset_db):
    reset_db()
    showcase_setup()
