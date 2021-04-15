import pytest
from django.core.management import call_command

from decharges.user_manager.models import Syndicat

pytestmark = pytest.mark.django_db


def test_instanciate():
    user = Syndicat.objects.create(
        email="test@example.com", first_name="Test", last_name="tseT"
    )
    assert f"{user}" == "test@example.com"


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
