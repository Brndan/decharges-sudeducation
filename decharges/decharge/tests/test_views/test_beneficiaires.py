from decimal import Decimal

import pytest
from django.conf import settings
from django.urls import reverse

from decharges.decharge.models import Corps, UtilisationTempsDecharge
from decharges.parametre.models import ParametresDApplication
from decharges.user_manager.models import Syndicat

pytestmark = pytest.mark.django_db


def test_ajouter_beneficiaire(client):
    Syndicat.objects.create(
        is_superuser=True, email="admin@example.com", username="Fédération"
    )
    ParametresDApplication.objects.create(annee_en_cours=2020)
    syndicat = Syndicat.objects.create(
        email="syndicat1@example.com", username="Syndicat 1"
    )
    client.force_login(syndicat)
    corps = Corps.objects.create(code_corps="123")
    response = client.get(reverse("decharge:ajouter_beneficiaire"))
    assert response.status_code == 200
    response = client.post(
        reverse("decharge:ajouter_beneficiaire"),
        {
            "civilite": "MME",
            "prenom": "Michelle",
            "nom": "MARTIN",
            "heures_de_decharges": 10,
            "heures_d_obligation_de_service": 35,
            "corps": corps.pk,
            "code_etablissement_rne": "1234567A",
        },
    )
    assert response.status_code == 302
    assert UtilisationTempsDecharge.objects.count() == 1
    utilisation_tps = UtilisationTempsDecharge.objects.first()
    assert utilisation_tps.syndicat == syndicat
    assert utilisation_tps.annee == 2020
    assert utilisation_tps.nom == "MARTIN"
    assert utilisation_tps.etp_utilises == round(
        Decimal(10) / Decimal(35), settings.PRECISION_ETP
    )


def test_maj_beneficiaire(client):
    Syndicat.objects.create(
        is_superuser=True, email="admin@example.com", username="Fédération"
    )
    ParametresDApplication.objects.create(annee_en_cours=2021)
    syndicat = Syndicat.objects.create(
        email="syndicat1@example.com", username="Syndicat 1"
    )
    syndicat2 = Syndicat.objects.create(
        email="syndicat2@example.com", username="Syndicat 2"
    )
    client.force_login(syndicat2)
    corps = Corps.objects.create(code_corps="123")
    utilisation_tps = UtilisationTempsDecharge.objects.create(
        civilite="MME",
        prenom="Michelle",
        nom="MARTIN",
        heures_de_decharges=10,
        heures_d_obligation_de_service=35,
        corps=corps,
        code_etablissement_rne="1234567A",
        syndicat=syndicat,
        annee=2020,
    )
    response = client.get(
        reverse("decharge:modifier_beneficiaire", kwargs={"pk": utilisation_tps.pk})
    )
    assert response.status_code == 404  # check permission
    client.force_login(syndicat)
    response = client.get(
        reverse("decharge:modifier_beneficiaire", kwargs={"pk": utilisation_tps.pk})
    )
    assert response.status_code == 200
    response = client.post(
        reverse("decharge:modifier_beneficiaire", kwargs={"pk": utilisation_tps.pk}),
        {
            "civilite": "MME",
            "prenom": "Michelle",
            "nom": "MARTIN",
            "heures_de_decharges": 20,
            "heures_d_obligation_de_service": 35,
            "corps": corps.pk,
            "code_etablissement_rne": "1234567A",
        },
    )
    assert response.status_code == 302

    utilisation_tps.refresh_from_db()
    assert utilisation_tps.syndicat == syndicat
    assert utilisation_tps.annee == 2020
    assert utilisation_tps.nom == "MARTIN"
    assert utilisation_tps.etp_utilises == round(
        Decimal(20) / Decimal(35), settings.PRECISION_ETP
    )


def test_suppression_beneficiaire(client):
    Syndicat.objects.create(
        is_superuser=True, email="admin@example.com", username="Fédération"
    )
    ParametresDApplication.objects.create(annee_en_cours=2021)
    syndicat = Syndicat.objects.create(
        email="syndicat1@example.com", username="Syndicat 1"
    )
    syndicat2 = Syndicat.objects.create(
        email="syndicat2@example.com", username="Syndicat 2"
    )
    client.force_login(syndicat2)
    corps = Corps.objects.create(code_corps="123")
    utilisation_tps = UtilisationTempsDecharge.objects.create(
        civilite="MME",
        prenom="Michelle",
        nom="MARTIN",
        heures_de_decharges=10,
        heures_d_obligation_de_service=35,
        corps=corps,
        code_etablissement_rne="1234567A",
        syndicat=syndicat,
        annee=2020,
    )
    response = client.get(
        reverse("decharge:supprimer_beneficiaire", kwargs={"pk": utilisation_tps.pk})
    )
    assert response.status_code == 404  # check permission
    client.force_login(syndicat)
    response = client.get(
        reverse("decharge:supprimer_beneficiaire", kwargs={"pk": utilisation_tps.pk})
    )
    assert response.status_code == 200
    response = client.post(
        reverse("decharge:supprimer_beneficiaire", kwargs={"pk": utilisation_tps.pk})
    )
    assert response.status_code == 302
    assert UtilisationTempsDecharge.objects.count() == 0
