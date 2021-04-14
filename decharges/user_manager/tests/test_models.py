import pytest
from django.core.management import call_command

from decharges.user_manager.models import User

pytestmark = pytest.mark.django_db


def test_instanciate():
    user = User.objects.create(
        email="test@example.com", first_name="Test", last_name="tseT"
    )
    assert f"{user}" == "test@example.com"


def test_management_create_superuser():
    assert User.objects.count() == 0
    call_command(
        "createsuperuser",
        email="test@test.com",
        first_name="testi",
        last_name="test",
        interactive=False,
    )
    admin = User.objects.first()
    assert admin.is_superuser
