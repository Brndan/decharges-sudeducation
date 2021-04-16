import pytest
from django.core.management import call_command

from decharges.user_manager.models import Academie, Syndicat

pytestmark = pytest.mark.django_db


def test_instanciate():
    user1 = Syndicat.objects.create(email="test1@example.com")
    user2 = Syndicat.objects.create(email="test2@example.com", username="Test")
    assert f"{user1}" == "test1@example.com"
    assert f"{user2}" == "Test"
    assert not user2.is_federation


def test_management_create_superuser():
    assert Syndicat.objects.count() == 0
    call_command(
        "createsuperuser",
        email="test@test.com",
        first_name="testi",
        last_name="test",
        interactive=False,
    )
    admin = Syndicat.objects.first()
    assert admin.is_superuser


def test_instanciate_academie():
    academie = Academie.objects.create(nom="Academ")
    assert f"{academie}" == "Academ"
