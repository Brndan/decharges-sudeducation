import pytest

from decharges.parametre.models import ParametresDApplication

pytestmark = pytest.mark.django_db


def test_instanciate_parameters():
    params = ParametresDApplication.objects.create()
    assert f"{params}" == "Paramètres de l'application"
