from decimal import Decimal

import pytest
from django.conf import settings
from django.contrib.messages import get_messages
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.utils import timezone

from decharges.decharge.models import (
    TempsDeDecharge,
    UtilisationCreditDeTempsSyndicalPonctuel,
    UtilisationTempsDecharge,
)
from decharges.parametre.models import ParametresDApplication
from decharges.user_manager.models import Syndicat

pytestmark = pytest.mark.django_db


def test_accueil__bad_configuration(client):
    syndicat = Syndicat.objects.create(
        email="syndicat@example.com", username="Syndicat"
    )
    Syndicat.objects.create(
        is_superuser=True, email="admin@example.com", username="Fédération"
    )
    client.force_login(syndicat)
    res = client.get("/")
    assert res.status_code == 400
    Syndicat.objects.filter(is_superuser=True).delete()
    ParametresDApplication.objects.create()
    res = client.get("/")
    assert res.status_code == 400


def test_accueil__empty(client):
    federation = Syndicat.objects.create(
        is_superuser=True, email="admin@example.com", username="Fédération"
    )
    ParametresDApplication.objects.create()
    client.force_login(federation)
    res = client.get("/")
    assert res.status_code == 200
    assert res.context["temps_restant"] == 0
    assert res.context["cts_consommes"] is None
    assert res.context["temps_donnes"].count() == 0
    assert res.context["temps_utilises"].count() == 0
    assert res.context["temps_recus_par_la_federation"] == 0
    assert res.context["temps_recus_par_des_syndicats"] == 0
    assert res.context["temps_utilises_total"] == 0
    assert res.context["temps_donnes_total"] == 0


def test_accueil__temps_utilises(client):
    syndicat = Syndicat.objects.create(
        email="syndicat@example.com", username="Syndicat"
    )
    syndicat_donateur = Syndicat.objects.create(
        email="syndicat2@example.com", username="Syndicat2"
    )
    Syndicat.objects.create(
        is_superuser=True, email="admin@example.com", username="Fédération"
    )
    ParametresDApplication.objects.create(annee_en_cours=2021)
    client.force_login(syndicat)
    TempsDeDecharge.objects.create(
        syndicat_beneficiaire=syndicat, annee=2021, temps_de_decharge_etp=3
    )
    TempsDeDecharge.objects.create(
        syndicat_beneficiaire=syndicat, annee=2020, temps_de_decharge_etp=3
    )
    TempsDeDecharge.objects.create(
        syndicat_beneficiaire=syndicat,
        annee=2021,
        temps_de_decharge_etp=0.1,
        syndicat_donateur=syndicat_donateur,
    )
    TempsDeDecharge.objects.create(
        syndicat_beneficiaire=syndicat,
        annee=2020,
        temps_de_decharge_etp=0.1,
        syndicat_donateur=syndicat_donateur,
    )
    TempsDeDecharge.objects.create(
        syndicat_beneficiaire=syndicat_donateur,
        annee=2021,
        temps_de_decharge_etp=0.2,
        syndicat_donateur=syndicat,
    )
    TempsDeDecharge.objects.create(
        syndicat_beneficiaire=syndicat_donateur,
        annee=2020,
        temps_de_decharge_etp=0.2,
        syndicat_donateur=syndicat,
    )
    UtilisationTempsDecharge.objects.create(
        civilite="M.",
        prenom="Foo",
        nom="BAR",
        heures_de_decharges=40,
        heures_d_obligation_de_service=1607,
        code_etablissement_rne="1234567A",
        annee=2021,
        syndicat=syndicat,
    )
    UtilisationTempsDecharge.objects.create(
        civilite="M.",
        prenom="Foo",
        nom="BAR",
        heures_de_decharges=40,
        heures_d_obligation_de_service=1607,
        code_etablissement_rne="1234567A",
        annee=2021,
        syndicat=syndicat_donateur,
    )
    UtilisationTempsDecharge.objects.create(
        civilite="M.",
        prenom="Foo",
        nom="BAR",
        heures_de_decharges=40,
        heures_d_obligation_de_service=1607,
        code_etablissement_rne="1234567A",
        annee=2020,
        syndicat=syndicat,
    )
    UtilisationTempsDecharge.objects.create(
        civilite="M.",
        prenom="Foo2",
        nom="BAR2",
        heures_de_decharges=40,
        heures_d_obligation_de_service=1607,
        code_etablissement_rne="1234567A",
        annee=2021,
        syndicat=syndicat,
        supprime_a=timezone.now(),
    )
    cts = UtilisationCreditDeTempsSyndicalPonctuel.objects.create(
        demi_journees_de_decharges=20, annee=2021, syndicat=syndicat
    )
    UtilisationCreditDeTempsSyndicalPonctuel.objects.create(
        demi_journees_de_decharges=20, annee=2021, syndicat=syndicat_donateur
    )
    UtilisationCreditDeTempsSyndicalPonctuel.objects.create(
        demi_journees_de_decharges=10, annee=2020, syndicat=syndicat
    )

    res = client.get("/")
    assert res.status_code == 200
    assert res.context["temps_restant"] == round(
        Decimal(3)
        + Decimal(0.1)
        - Decimal(0.2)
        - Decimal(40) / Decimal(1607)
        - Decimal(20) * Decimal(3.5) / settings.NB_HOURS_IN_A_YEAR,
        settings.PRECISION_ETP,
    )
    assert res.context["cts_consommes"] == cts
    assert res.context["temps_donnes"].count() == 1
    assert res.context["temps_utilises"].count() == 1
    assert res.context["temps_recus_par_la_federation"] == round(
        Decimal(3), settings.PRECISION_ETP
    )
    assert res.context["temps_recus_par_des_syndicats"] == round(
        Decimal(0.1), settings.PRECISION_ETP
    )
    assert res.context["temps_utilises_total"] == round(
        Decimal(40) / Decimal(1607), settings.PRECISION_ETP
    )
    assert res.context["temps_donnes_total"] == round(
        Decimal(0.2), settings.PRECISION_ETP
    )


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
