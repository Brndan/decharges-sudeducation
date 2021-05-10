from decimal import Decimal

import pandas
import pytest
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from decharges.decharge.models import Corps, UtilisationTempsDecharge
from decharges.parametre.models import ParametresDApplication
from decharges.user_manager.models import Syndicat

pytestmark = pytest.mark.django_db


def test_ajouter_beneficiaire(client):
    Syndicat.objects.create(
        is_superuser=True, email="admin@example.com", username="Fédération"
    )
    ParametresDApplication.objects.create(
        annee_en_cours=2020,
        corps_annexe=SimpleUploadedFile("file.pdf", b"random data"),
    )
    syndicat = Syndicat.objects.create(
        email="syndicat1@example.com", username="Syndicat 1"
    )
    client.force_login(syndicat)
    corps = Corps.objects.create(code_corps="123")
    response = client.get(reverse("decharge:ajouter_beneficiaire"))
    assert response.status_code == 200
    assert response.context["form"].fields["corps"].help_text is not None
    response = client.post(
        reverse("decharge:ajouter_beneficiaire"),
        {
            "civilite": "MME",
            "prenom": "Michelle",
            "nom": "MARTIN",
            "heures_de_decharges": 10,
            "minutes_de_decharges": 14,
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
        (Decimal(10) + Decimal(14 / 60)) / Decimal(35), settings.PRECISION_ETP
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
            "minutes_de_decharges": 14,
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
        (Decimal(20) + Decimal(14 / 60)) / Decimal(35), settings.PRECISION_ETP
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


def test_beneficiaire_non_editable(client):
    Syndicat.objects.create(
        is_superuser=True, email="admin@example.com", username="Fédération"
    )
    ParametresDApplication.objects.create(
        annee_en_cours=2020, decharges_editables=False
    )
    syndicat = Syndicat.objects.create(
        email="syndicat1@example.com", username="Syndicat 1"
    )
    client.force_login(syndicat)
    response = client.get(reverse("decharge:ajouter_beneficiaire"))
    assert response.status_code == 404


def test_ajouter_beneficiaire__en_cours_d_annee(client):
    federation = Syndicat.objects.create(
        is_superuser=True, email="admin@example.com", username="Fédération"
    )
    ParametresDApplication.objects.create(
        annee_en_cours=2020, decharges_editables=False
    )
    syndicat = Syndicat.objects.create(
        email="syndicat1@example.com", username="Syndicat 1"
    )
    syndicat2 = Syndicat.objects.create(
        email="syndicat2@example.com", username="Syndicat 2"
    )
    corps = Corps.objects.create(code_corps="123")
    temps_existant = UtilisationTempsDecharge.objects.create(
        civilite="MME",
        prenom="Michelle",
        nom="MARTIN",
        heures_de_decharges=10,
        heures_d_obligation_de_service=35,
        corps=corps,
        code_etablissement_rne="1234567A",
        syndicat=syndicat2,
        annee=2020,
    )
    client.force_login(federation)
    response = client.get(
        reverse("decharge:ajouter_beneficiaire") + "?syndicat=Syndicat%201"
    )
    assert response.status_code == 200
    assert response.context["form"].fields["syndicat"].initial == syndicat
    response = client.post(
        reverse("decharge:ajouter_beneficiaire"),
        {
            "civilite": "MME",
            "prenom": "Michelle",
            "nom": "MARTIN",
            "heures_de_decharges": 10,
            "minutes_de_decharges": 14,
            "heures_d_obligation_de_service": 35,
            "corps": corps.pk,
            "code_etablissement_rne": "1234567A",
            "syndicat": syndicat.pk,
            "commentaire_de_mise_a_jour": "Parce que",
        },
    )
    assert response.status_code == 200
    assert UtilisationTempsDecharge.objects.count() == 2
    utilisation_tps = UtilisationTempsDecharge.objects.exclude(
        pk=temps_existant.pk
    ).first()
    assert utilisation_tps.syndicat == syndicat
    assert utilisation_tps.annee == 2020
    assert utilisation_tps.nom == "MARTIN"
    assert utilisation_tps.commentaire_de_mise_a_jour == "Parce que"
    assert utilisation_tps.etp_utilises == round(
        (Decimal(10) + Decimal(14 / 60)) / Decimal(35), settings.PRECISION_ETP
    )
    document = pandas.read_excel(response.content, dtype="string")
    assert len(list(document.iterrows())) == 1
    assert list(document.iterrows())[0][1]["Code organisation"] == "S01"
    assert list(document.iterrows())[0][1]["M. Mme"] == "Mme"
    assert list(document.iterrows())[0][1]["Prénom"] == "Michelle"
    assert list(document.iterrows())[0][1]["Nom"] == "MARTIN"
    assert list(document.iterrows())[0][1]["Heures décharges"] == "20"
    assert list(document.iterrows())[0][1]["Minutes décharges"] == "14"
    assert list(document.iterrows())[0][1]["Heures ORS"] == "35"
    assert list(document.iterrows())[0][1]["Minutes ORS"] == "0"
    assert list(document.iterrows())[0][1]["AIRE"] == "2"
    assert list(document.iterrows())[0][1]["Corps"] == "123"
    assert list(document.iterrows())[0][1]["RNE"] == "1234567A"


def test_maj_beneficiaire__en_cours_d_annee(client):
    federation = Syndicat.objects.create(
        is_superuser=True, email="admin@example.com", username="Fédération"
    )
    ParametresDApplication.objects.create(
        annee_en_cours=2021, decharges_editables=False
    )
    syndicat = Syndicat.objects.create(
        email="syndicat1@example.com", username="Syndicat 1"
    )
    client.force_login(federation)
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
        annee=2021,
    )
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
            "minutes_de_decharges": 14,
            "heures_d_obligation_de_service": 35,
            "corps": corps.pk,
            "code_etablissement_rne": "1234567A",
            "syndicat": syndicat.pk,
            "commentaire_de_mise_a_jour": "Parce que",
        },
    )
    assert response.status_code == 200

    utilisation_tps.refresh_from_db()
    assert utilisation_tps.syndicat == syndicat
    assert utilisation_tps.annee == 2021
    assert utilisation_tps.nom == "MARTIN"
    assert utilisation_tps.commentaire_de_mise_a_jour == "Parce que"
    assert utilisation_tps.etp_utilises == round(
        (Decimal(20) + Decimal(14 / 60)) / Decimal(35), settings.PRECISION_ETP
    )
    document = pandas.read_excel(response.content, dtype="string")
    assert len(list(document.iterrows())) == 1
    assert list(document.iterrows())[0][1]["Code organisation"] == "S01"
    assert list(document.iterrows())[0][1]["M. Mme"] == "Mme"
    assert list(document.iterrows())[0][1]["Prénom"] == "Michelle"
    assert list(document.iterrows())[0][1]["Nom"] == "MARTIN"
    assert list(document.iterrows())[0][1]["Heures décharges"] == "20"
    assert list(document.iterrows())[0][1]["Minutes décharges"] == "14"
    assert list(document.iterrows())[0][1]["Heures ORS"] == "35"
    assert list(document.iterrows())[0][1]["Minutes ORS"] == "0"
    assert list(document.iterrows())[0][1]["AIRE"] == "2"
    assert list(document.iterrows())[0][1]["Corps"] == "123"
    assert list(document.iterrows())[0][1]["RNE"] == "1234567A"


def test_suppression_beneficiaire__en_cours_d_annee(client):
    federation = Syndicat.objects.create(
        is_superuser=True, email="admin@example.com", username="Fédération"
    )
    ParametresDApplication.objects.create(
        annee_en_cours=2021, decharges_editables=False
    )
    syndicat = Syndicat.objects.create(
        email="syndicat1@example.com", username="Syndicat 1"
    )
    client.force_login(federation)
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
        annee=2021,
    )
    response = client.get(
        reverse("decharge:supprimer_beneficiaire", kwargs={"pk": utilisation_tps.pk})
    )
    assert response.status_code == 200
    response = client.post(
        reverse("decharge:supprimer_beneficiaire", kwargs={"pk": utilisation_tps.pk})
    )
    assert response.status_code == 200
    assert UtilisationTempsDecharge.objects.count() == 0
    document = pandas.read_excel(response.content, dtype="string")
    assert len(list(document.iterrows())) == 1
    assert list(document.iterrows())[0][1]["Code organisation"] == "S01"
    assert list(document.iterrows())[0][1]["M. Mme"] == "Mme"
    assert list(document.iterrows())[0][1]["Prénom"] == "Michelle"
    assert list(document.iterrows())[0][1]["Nom"] == "MARTIN"
    assert list(document.iterrows())[0][1]["Heures décharges"] == "10"
    assert list(document.iterrows())[0][1]["Minutes décharges"] == "0"
    assert list(document.iterrows())[0][1]["Heures ORS"] == "35"
    assert list(document.iterrows())[0][1]["Minutes ORS"] == "0"
    assert list(document.iterrows())[0][1]["AIRE"] == "2"
    assert list(document.iterrows())[0][1]["Corps"] == "123"
    assert list(document.iterrows())[0][1]["RNE"] == "1234567A"


def test_suppression_beneficiaire__en_cours_d_annee__modification(client):
    federation = Syndicat.objects.create(
        is_superuser=True, email="admin@example.com", username="Fédération"
    )
    ParametresDApplication.objects.create(
        annee_en_cours=2021, decharges_editables=False
    )
    syndicat = Syndicat.objects.create(
        email="syndicat1@example.com", username="Syndicat 1"
    )
    syndicat2 = Syndicat.objects.create(
        email="syndicat2@example.com", username="Syndicat 2"
    )
    client.force_login(federation)
    corps = Corps.objects.create(code_corps="123")
    UtilisationTempsDecharge.objects.create(
        civilite="MME",
        prenom="Michelle",
        nom="MARTIN",
        heures_de_decharges=40,
        heures_d_obligation_de_service=35,
        corps=corps,
        code_etablissement_rne="1234567A",
        syndicat=syndicat2,
        annee=2021,
    )
    utilisation_tps = UtilisationTempsDecharge.objects.create(
        civilite="MME",
        prenom="Michelle",
        nom="MARTIN",
        heures_de_decharges=10,
        heures_d_obligation_de_service=35,
        corps=corps,
        code_etablissement_rne="1234567A",
        syndicat=syndicat,
        annee=2021,
    )
    response = client.get(
        reverse("decharge:supprimer_beneficiaire", kwargs={"pk": utilisation_tps.pk})
    )
    assert response.status_code == 200
    response = client.post(
        reverse("decharge:supprimer_beneficiaire", kwargs={"pk": utilisation_tps.pk})
    )
    assert response.status_code == 200
    assert UtilisationTempsDecharge.objects.count() == 1
    document = pandas.read_excel(response.content, dtype="string")
    assert len(list(document.iterrows())) == 1
    assert list(document.iterrows())[0][1]["Code organisation"] == "S01"
    assert list(document.iterrows())[0][1]["M. Mme"] == "Mme"
    assert list(document.iterrows())[0][1]["Prénom"] == "Michelle"
    assert list(document.iterrows())[0][1]["Nom"] == "MARTIN"
    assert list(document.iterrows())[0][1]["Heures décharges"] == "40"
    assert list(document.iterrows())[0][1]["Minutes décharges"] == "0"
    assert list(document.iterrows())[0][1]["Heures ORS"] == "35"
    assert list(document.iterrows())[0][1]["Minutes ORS"] == "0"
    assert list(document.iterrows())[0][1]["AIRE"] == "2"
    assert list(document.iterrows())[0][1]["Corps"] == "123"
    assert list(document.iterrows())[0][1]["RNE"] == "1234567A"
