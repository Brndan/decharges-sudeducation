import pytest
from django.contrib.messages import get_messages
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from decharges.decharge.models import TempsDeDecharge
from decharges.parametre.models import ParametresDApplication
from decharges.user_manager.models import Syndicat

pytestmark = pytest.mark.django_db


def test_import_temps_syndicats__get(client):
    federation = Syndicat.objects.create(
        is_superuser=True, email="admin@example.com", username="Fédération"
    )
    ParametresDApplication.objects.create()
    client.force_login(federation)
    response = client.get(reverse("decharge:import_temps"))
    assert response.status_code == 200


def test_import_temps_syndicats__post__unknown_syndicat(client):
    federation = Syndicat.objects.create(
        is_superuser=True, email="admin@example.com", username="Fédération"
    )
    ParametresDApplication.objects.create()
    client.force_login(federation)
    with open(
        "decharges/decharge/tests/assets/temps_decharge_syndicat_example.ods", "rb"
    ) as f:
        ods_file = SimpleUploadedFile(
            "temps_decharge_syndicat_example.ods",
            f.read(),
            content_type="application/vnd.oasis.opendocument.spreadsheet",
        )
    response = client.post(
        reverse("decharge:import_temps"),
        {
            "ods_file": ods_file,
            "annee": 2021,
        },
    )
    assert response.status_code == 200
    assert (
        response.context["form"].errors["ods_file"][0]
        == "Syndicat non trouvé en base : Syndicat 1 (ligne 2)"
    )
    assert TempsDeDecharge.objects.count() == 0


def test_import_temps_syndicats__post__wrong_etp(client):
    federation = Syndicat.objects.create(
        is_superuser=True, email="admin@example.com", username="Fédération"
    )
    ParametresDApplication.objects.create()
    Syndicat.objects.create(email="syndicat1@example.com", username="Syndicat 1")
    Syndicat.objects.create(email="syndicat2@example.com", username="Syndicat 2")
    client.force_login(federation)
    with open(
        "decharges/decharge/tests/assets/temps_decharge_syndicat_invalid_example.ods",
        "rb",
    ) as f:
        ods_file = SimpleUploadedFile(
            "temps_decharge_syndicat_example.ods",
            f.read(),
            content_type="application/vnd.oasis.opendocument.spreadsheet",
        )
    response = client.post(
        reverse("decharge:import_temps"),
        {
            "ods_file": ods_file,
            "annee": 2021,
        },
    )
    assert response.status_code == 200
    assert (
        response.context["form"].errors["ods_file"][0]
        == "ETP invalide : azer (ligne 2)"
    )
    assert TempsDeDecharge.objects.count() == 0


def test_import_temps_syndicats__post(client):
    federation = Syndicat.objects.create(
        is_superuser=True, email="admin@example.com", username="Fédération"
    )
    ParametresDApplication.objects.create()
    Syndicat.objects.create(email="syndicat1@example.com", username="Syndicat 1")
    Syndicat.objects.create(email="syndicat2@example.com", username="Syndicat 2")
    client.force_login(federation)
    with open(
        "decharges/decharge/tests/assets/temps_decharge_syndicat_example.ods", "rb"
    ) as f:
        ods_file = SimpleUploadedFile(
            "temps_decharge_syndicat_example.ods",
            f.read(),
            content_type="application/vnd.oasis.opendocument.spreadsheet",
        )
    response = client.post(
        reverse("decharge:import_temps"),
        {
            "ods_file": ods_file,
            "annee": 2021,
        },
    )
    assert response.status_code == 302
    assert TempsDeDecharge.objects.count() == 2
    assert TempsDeDecharge.objects.first().annee == 2021
    assert (
        str(list(get_messages(response.wsgi_request))[0])
        == "Import terminé avec succès. 2 temps créés."
    )
    with open(
        "decharges/decharge/tests/assets/temps_decharge_syndicat_example.ods", "rb"
    ) as f:
        ods_file = SimpleUploadedFile(
            "temps_decharge_syndicat_example.ods",
            f.read(),
            content_type="application/vnd.oasis.opendocument.spreadsheet",
        )
    response = client.post(
        reverse("decharge:import_temps"),
        {
            "ods_file": ods_file,
            "annee": 2021,
        },
    )
    assert (
        str(list(get_messages(response.wsgi_request))[1])
        == "Import terminé avec succès. 2 temps mis à jour."
    )
    assert TempsDeDecharge.objects.count() == 2
