import pytest

from decharges.parametre.models import ParametresDApplication
from decharges.user_manager.models import Syndicat

pytestmark = pytest.mark.django_db


def test_tests(client):
    federation = Syndicat.objects.create(
        is_superuser=True, email="admin@example.com", username="Fédération"
    )
    ParametresDApplication.objects.create()
    client.force_login(federation)
    res = client.get("/")
    assert res.status_code == 200
