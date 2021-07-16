import datetime
from decimal import Decimal
from io import BytesIO

import pandas
import pytest
from django.conf import settings
from django.contrib.messages import get_messages
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from decharges.decharge.models import Corps, TempsDeDecharge, UtilisationTempsDecharge
from decharges.parametre.models import ParametresDApplication
from decharges.user_manager.models import Syndicat

pytestmark = pytest.mark.django_db


def test_ajouter_beneficiaire(client):
    federation = Syndicat.objects.create(
        is_superuser=True, email="admin@example.com", username="Fédération"
    )
    ParametresDApplication.objects.create(
        annee_en_cours=2020,
        corps_annexe=SimpleUploadedFile("file.pdf", b"random data"),
    )
    syndicat = Syndicat.objects.create(
        email="syndicat1@example.com", username="Syndicat 1"
    )
    TempsDeDecharge.objects.create(
        syndicat_beneficiaire=syndicat,
        syndicat_donateur=federation,
        annee=2020,
        temps_de_decharge_etp=10,
    )
    client.force_login(syndicat)
    corps = Corps.objects.create(code_corps="123")
    response = client.get(reverse("decharge:ajouter_beneficiaire"))
    assert response.status_code == 200
    assert response.context["form"].fields["corps"].help_text is not None
    assert "est_une_decharge_solidaires" not in response.context["form"].fields
    response = client.post(
        reverse("decharge:ajouter_beneficiaire"),
        {
            "civilite": "MME",
            "prenom": "Michelle",
            "nom": "MARTIN",
            "int_heures_de_decharges": 10,
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
    assert utilisation_tps.date_debut_decharge == datetime.date(
        year=2020, month=9, day=1
    )
    assert utilisation_tps.date_fin_decharge == datetime.date(
        year=2021, month=8, day=31
    )
    assert utilisation_tps.etp_utilises == round(
        (Decimal(10) + Decimal(14 / 60)) / Decimal(35), settings.PRECISION_ETP
    )


def test_ajouter_beneficiaire__prorata(client):
    federation = Syndicat.objects.create(
        is_superuser=True, email="admin@example.com", username="Fédération"
    )
    ParametresDApplication.objects.create(
        annee_en_cours=2020,
        corps_annexe=SimpleUploadedFile("file.pdf", b"random data"),
    )
    syndicat = Syndicat.objects.create(
        email="syndicat1@example.com", username="Syndicat 1"
    )
    TempsDeDecharge.objects.create(
        syndicat_beneficiaire=syndicat,
        syndicat_donateur=federation,
        annee=2020,
        temps_de_decharge_etp=10,
    )
    client.force_login(syndicat)
    corps = Corps.objects.create(code_corps="123")
    response = client.get(reverse("decharge:ajouter_beneficiaire"))
    assert response.status_code == 200
    assert response.context["form"].fields["corps"].help_text is not None
    assert "est_une_decharge_solidaires" not in response.context["form"].fields
    response = client.post(
        reverse("decharge:ajouter_beneficiaire"),
        {
            "civilite": "MME",
            "prenom": "Michelle",
            "nom": "MARTIN",
            "int_heures_de_decharges": 10,
            "minutes_de_decharges": 14,
            "heures_d_obligation_de_service": 35,
            "corps": corps.pk,
            "code_etablissement_rne": "1234567A",
            "decharge_applicable_uniquement_sur_une_partie_de_lannee": True,
            "date_debut_decharge": "01/10/2020",
            "date_fin_decharge": "01/07/2021",
        },
    )
    assert response.status_code == 302
    assert UtilisationTempsDecharge.objects.count() == 1
    utilisation_tps = UtilisationTempsDecharge.objects.first()
    assert utilisation_tps.syndicat == syndicat
    assert utilisation_tps.annee == 2020
    assert utilisation_tps.nom == "MARTIN"
    assert utilisation_tps.date_debut_decharge == datetime.date(
        year=2020, month=10, day=1
    )
    assert utilisation_tps.date_fin_decharge == datetime.date(year=2021, month=7, day=1)
    assert utilisation_tps.etp_utilises == round(
        Decimal(274 / 365) * (Decimal(10) + Decimal(14 / 60)) / Decimal(35),
        settings.PRECISION_ETP,
    )


def test_ajouter_beneficiaire__prorata_erreur(client):
    federation = Syndicat.objects.create(
        is_superuser=True, email="admin@example.com", username="Fédération"
    )
    ParametresDApplication.objects.create(
        annee_en_cours=2020,
        corps_annexe=SimpleUploadedFile("file.pdf", b"random data"),
    )
    syndicat = Syndicat.objects.create(
        email="syndicat1@example.com", username="Syndicat 1"
    )
    TempsDeDecharge.objects.create(
        syndicat_beneficiaire=syndicat,
        syndicat_donateur=federation,
        annee=2020,
        temps_de_decharge_etp=10,
    )
    client.force_login(syndicat)
    corps = Corps.objects.create(code_corps="123")
    response = client.get(reverse("decharge:ajouter_beneficiaire"))
    assert response.status_code == 200
    assert response.context["form"].fields["corps"].help_text is not None
    assert "est_une_decharge_solidaires" not in response.context["form"].fields
    response = client.post(
        reverse("decharge:ajouter_beneficiaire"),
        {
            "civilite": "MME",
            "prenom": "Michelle",
            "nom": "MARTIN",
            "int_heures_de_decharges": 10,
            "minutes_de_decharges": 14,
            "heures_d_obligation_de_service": 35,
            "corps": corps.pk,
            "code_etablissement_rne": "1234567A",
            "decharge_applicable_uniquement_sur_une_partie_de_lannee": True,
            "date_debut_decharge": "01/08/2020",
            "date_fin_decharge": "01/09/2021",
        },
    )
    assert response.status_code == 200
    assert (
        response.context["form"].errors["date_debut_decharge"][0]
        == "La date de début de décharge doit être une date dans l'année inférieure à la date de fin de décharge"
    )
    assert (
        response.context["form"].errors["date_fin_decharge"][0]
        == "La date de fin de décharge doit être une date dans l'année supérieure à la date de début de décharge"
    )


def test_ajouter_beneficiaire__unique_together(client):
    federation = Syndicat.objects.create(
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
    TempsDeDecharge.objects.create(
        syndicat_beneficiaire=syndicat,
        syndicat_donateur=federation,
        annee=2020,
        temps_de_decharge_etp=10,
    )
    corps = Corps.objects.create(code_corps="123")
    response = client.get(reverse("decharge:ajouter_beneficiaire"))
    assert response.status_code == 200
    assert response.context["form"].fields["corps"].help_text is not None
    assert "est_une_decharge_solidaires" not in response.context["form"].fields
    response = client.post(
        reverse("decharge:ajouter_beneficiaire"),
        {
            "civilite": "MME",
            "prenom": "Michelle",
            "nom": "MARTIN",
            "int_heures_de_decharges": 10,
            "minutes_de_decharges": 14,
            "heures_d_obligation_de_service": 35,
            "corps": corps.pk,
            "code_etablissement_rne": "1234567A",
        },
    )
    assert response.status_code == 302
    response = client.post(
        reverse("decharge:ajouter_beneficiaire"),
        {
            "civilite": "MME",
            "prenom": "Michelle",
            "nom": "MARTIN",
            "int_heures_de_decharges": 10,
            "minutes_de_decharges": 14,
            "heures_d_obligation_de_service": 35,
            "corps": corps.pk,
            "code_etablissement_rne": "1234567A",
        },
    )
    assert response.status_code == 200
    assert (
        response.context["form"].errors["__all__"][0]
        == "Une décharge pour cette ou ce bénéficiaire existe déjà, veuillez plutôt la mettre à jour"
    )
    assert UtilisationTempsDecharge.objects.count() == 1


def test_ajouter_beneficiaire__decharge_solidaires(client):
    federation = Syndicat.objects.create(
        is_superuser=True, email="admin@example.com", username="Fédération"
    )
    ParametresDApplication.objects.create(
        annee_en_cours=2020,
        corps_annexe=SimpleUploadedFile("file.pdf", b"random data"),
        decharges_editables=False,
    )
    syndicat = Syndicat.objects.create(
        email="syndicat1@example.com", username="Syndicat 1"
    )
    client.force_login(federation)
    corps = Corps.objects.create(code_corps="123")
    response = client.get(reverse("decharge:ajouter_beneficiaire"))
    assert response.status_code == 200
    assert response.context["form"].fields["corps"].help_text is not None
    assert (
        response.context["form"].fields["est_une_decharge_solidaires"].initial is False
    )
    response = client.post(
        reverse("decharge:ajouter_beneficiaire"),
        {
            "civilite": "MME",
            "prenom": "Michelle",
            "nom": "MARTIN",
            "int_heures_de_decharges": 10,
            "minutes_de_decharges": 14,
            "heures_d_obligation_de_service": 35,
            "corps": corps.pk,
            "code_etablissement_rne": "1234567A",
            "est_une_decharge_solidaires": True,
            "syndicat": syndicat.pk,
        },
    )
    assert (
        response.context["form"].errors["est_une_decharge_solidaires"][0]
        == "La décharge ne peut provenir d'un autre syndicat uniquement pour les décharges fédérales"
    )
    response = client.post(
        reverse("decharge:ajouter_beneficiaire"),
        {
            "civilite": "MME",
            "prenom": "Michelle",
            "nom": "MARTIN",
            "int_heures_de_decharges": 10,
            "minutes_de_decharges": 14,
            "heures_d_obligation_de_service": 35,
            "corps": corps.pk,
            "code_etablissement_rne": "1234567A",
            "est_une_decharge_solidaires": True,
            "syndicat": federation.pk,
            "commentaire_de_mise_a_jour": "C'est un test",
        },
    )
    assert response.status_code == 302
    assert UtilisationTempsDecharge.objects.count() == 1
    utilisation_tps = UtilisationTempsDecharge.objects.first()
    assert utilisation_tps.syndicat == federation
    assert utilisation_tps.annee == 2020
    assert utilisation_tps.nom == "MARTIN"
    assert utilisation_tps.etp_utilises == round(
        (Decimal(10) + Decimal(14 / 60)) / Decimal(35), settings.PRECISION_ETP
    )
    assert utilisation_tps.est_une_decharge_solidaires


def test_maj_beneficiaire(client):
    federation = Syndicat.objects.create(
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
    TempsDeDecharge.objects.create(
        syndicat_beneficiaire=syndicat,
        syndicat_donateur=federation,
        annee=2020,
        temps_de_decharge_etp=10,
    )
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
            "int_heures_de_decharges": 15,
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
    assert utilisation_tps.date_debut_decharge == datetime.date(
        year=2020, month=9, day=1
    )
    assert utilisation_tps.date_fin_decharge == datetime.date(
        year=2021, month=8, day=31
    )
    assert utilisation_tps.etp_utilises == round(
        (Decimal(15) + Decimal(14 / 60)) / Decimal(35), settings.PRECISION_ETP
    )


def test_maj_beneficiaire__prorata(client):
    federation = Syndicat.objects.create(
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
    TempsDeDecharge.objects.create(
        syndicat_beneficiaire=syndicat,
        syndicat_donateur=federation,
        annee=2020,
        temps_de_decharge_etp=10,
    )
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
        date_debut_decharge=datetime.date(year=2020, month=11, day=5),
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
    assert (
        response.context["form"]
        .fields["decharge_applicable_uniquement_sur_une_partie_de_lannee"]
        .initial
    )
    response = client.post(
        reverse("decharge:modifier_beneficiaire", kwargs={"pk": utilisation_tps.pk}),
        {
            "civilite": "MME",
            "prenom": "Michelle",
            "nom": "MARTIN",
            "int_heures_de_decharges": 15,
            "minutes_de_decharges": 14,
            "heures_d_obligation_de_service": 35,
            "corps": corps.pk,
            "code_etablissement_rne": "1234567A",
            "decharge_applicable_uniquement_sur_une_partie_de_lannee": True,
            "date_debut_decharge": "01/10/2020",
            "date_fin_decharge": "01/07/2021",
        },
    )
    assert response.status_code == 302

    utilisation_tps.refresh_from_db()
    assert utilisation_tps.syndicat == syndicat
    assert utilisation_tps.annee == 2020
    assert utilisation_tps.nom == "MARTIN"
    assert utilisation_tps.date_debut_decharge == datetime.date(
        year=2020, month=10, day=1
    )
    assert utilisation_tps.date_fin_decharge == datetime.date(year=2021, month=7, day=1)
    assert utilisation_tps.etp_utilises == round(
        Decimal(274 / 365) * (Decimal(15) + Decimal(14 / 60)) / Decimal(35),
        settings.PRECISION_ETP,
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


def test_suppression_beneficiaire__en_cours_d_annee__decharge_solidaires(client):
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
        annee=2020,
        est_une_decharge_solidaires=True,
    )
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
    TempsDeDecharge.objects.create(
        syndicat_beneficiaire=syndicat,
        syndicat_donateur=federation,
        annee=2020,
        temps_de_decharge_etp=10,
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
            "int_heures_de_decharges": 5,
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
        (Decimal(5) + Decimal(14 / 60)) / Decimal(35), settings.PRECISION_ETP
    )
    document = pandas.read_csv(BytesIO(response.content), dtype="string")
    rows = list(document.iterrows())
    assert len(rows) == 1
    assert rows[0][1]["Code organisation"] == "S01"
    assert rows[0][1]["Code civilité"] == "MME"
    assert rows[0][1]["Prénom"] == "Michelle"
    assert rows[0][1]["Nom"] == "MARTIN"
    assert rows[0][1]["Heures de décharge"] == "15"
    assert rows[0][1]["Minutes de décharge"] == "14"
    assert rows[0][1]["Heures d'obligations de service"] == "35"
    assert rows[0][1]["Aire"] == "2"
    assert rows[0][1]["Corps"] == "123"
    assert rows[0][1]["Etablissement"] == "1234567A"
    assert rows[0][1]["Date d'effet"] == "01/09/2020"
    assert rows[0][1]["Date de fin"] == "31/08/2021"


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
    TempsDeDecharge.objects.create(
        syndicat_beneficiaire=syndicat,
        syndicat_donateur=federation,
        annee=2021,
        temps_de_decharge_etp=10,
    )
    corps = Corps.objects.create(code_corps="123")
    utilisation_tps = UtilisationTempsDecharge.objects.create(
        civilite="MME",
        prenom="Michelle",
        nom="MARTINE",
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
            "int_heures_de_decharges": 15,
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
        (Decimal(15) + Decimal(14 / 60)) / Decimal(35), settings.PRECISION_ETP
    )
    document = pandas.read_csv(BytesIO(response.content), dtype="string")
    rows = list(document.iterrows())
    assert len(rows) == 1
    assert rows[0][1]["Code organisation"] == "S01"
    assert rows[0][1]["Code civilité"] == "MME"
    assert rows[0][1]["Prénom"] == "Michelle"
    assert rows[0][1]["Nom"] == "MARTIN"
    assert rows[0][1]["Heures de décharge"] == "15"
    assert rows[0][1]["Minutes de décharge"] == "14"
    assert rows[0][1]["Heures d'obligations de service"] == "35"
    assert rows[0][1]["Aire"] == "2"
    assert rows[0][1]["Corps"] == "123"
    assert rows[0][1]["Etablissement"] == "1234567A"
    assert rows[0][1]["Date d'effet"] == "01/09/2021"
    assert rows[0][1]["Date de fin"] == "31/08/2022"


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
    document = pandas.read_csv(BytesIO(response.content), dtype="string")
    rows = list(document.iterrows())
    assert len(rows) == 1
    assert rows[0][1]["Code organisation"] == "S01"
    assert rows[0][1]["Code civilité"] == "MME"
    assert rows[0][1]["Prénom"] == "Michelle"
    assert rows[0][1]["Nom"] == "MARTIN"
    assert rows[0][1]["Heures de décharge"] == "10"
    assert rows[0][1]["Minutes de décharge"] == "0"
    assert rows[0][1]["Heures d'obligations de service"] == "35"
    assert rows[0][1]["Aire"] == "2"
    assert rows[0][1]["Corps"] == "123"
    assert rows[0][1]["Etablissement"] == "1234567A"
    assert rows[0][1]["Date d'effet"] == "01/09/2021"
    assert rows[0][1]["Date de fin"] == "31/08/2022"


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
    document = pandas.read_csv(BytesIO(response.content), dtype="string")
    rows = list(document.iterrows())
    assert len(rows) == 1
    assert rows[0][1]["Code organisation"] == "S01"
    assert rows[0][1]["Code civilité"] == "MME"
    assert rows[0][1]["Prénom"] == "Michelle"
    assert rows[0][1]["Nom"] == "MARTIN"
    assert rows[0][1]["Heures de décharge"] == "40"
    assert rows[0][1]["Minutes de décharge"] == "0"
    assert rows[0][1]["Heures d'obligations de service"] == "35"
    assert rows[0][1]["Aire"] == "2"
    assert rows[0][1]["Corps"] == "123"
    assert rows[0][1]["Etablissement"] == "1234567A"
    assert rows[0][1]["Date d'effet"] == "01/09/2021"
    assert rows[0][1]["Date de fin"] == "31/08/2022"


def test_ajouter_beneficiaire__pas_assez_de_quota(client):
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
    response = client.post(
        reverse("decharge:ajouter_beneficiaire"),
        {
            "civilite": "MME",
            "prenom": "Michelle",
            "nom": "MARTIN",
            "int_heures_de_decharges": 10,
            "minutes_de_decharges": 14,
            "heures_d_obligation_de_service": 35,
            "corps": corps.pk,
            "code_etablissement_rne": "1234567A",
        },
    )
    assert response.status_code == 200
    assert (
        response.context["form"].errors["__all__"][0]
        == "Vous dépassez le quota du syndicat, il reste 0.000 ETP attribuable et vous essayez d'ajouter 0.292 ETP"
    )
    assert UtilisationTempsDecharge.objects.count() == 0


def test_ajouter_beneficiaire__depasse_quota_individuel(client):
    federation = Syndicat.objects.create(
        is_superuser=True, email="admin@example.com", username="Fédération"
    )
    ParametresDApplication.objects.create(
        annee_en_cours=2020,
        corps_annexe=SimpleUploadedFile("file.pdf", b"random data"),
    )
    syndicat = Syndicat.objects.create(
        email="syndicat1@example.com", username="Syndicat 1"
    )
    syndicat2 = Syndicat.objects.create(
        email="syndicat2@example.com", username="Syndicat 2"
    )
    corps = Corps.objects.create(code_corps="123")
    UtilisationTempsDecharge.objects.create(
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
    TempsDeDecharge.objects.create(
        syndicat_beneficiaire=syndicat,
        syndicat_donateur=federation,
        annee=2020,
        temps_de_decharge_etp=10,
    )
    client.force_login(syndicat)
    response = client.post(
        reverse("decharge:ajouter_beneficiaire"),
        {
            "civilite": "MME",
            "prenom": "Michelle",
            "nom": "MARTIN",
            "int_heures_de_decharges": 10,
            "minutes_de_decharges": 14,
            "heures_d_obligation_de_service": 35,
            "corps": corps.pk,
            "code_etablissement_rne": "1234567A",
        },
    )
    assert response.status_code == 200
    assert (
        response.context["form"].errors["__all__"][0]
        == "Vous dépassez le quota du bénéficiaire, il lui reste au maximum 0.214 ETP à consommer et vous essayez de lui ajouter 0.292 ETP"
    )


def test_ajouter_beneficiaire__depasse_8_annees_consecutives(client):
    federation = Syndicat.objects.create(
        is_superuser=True, email="admin@example.com", username="Fédération"
    )
    ParametresDApplication.objects.create(
        annee_en_cours=2020,
        corps_annexe=SimpleUploadedFile("file.pdf", b"random data"),
    )
    syndicat = Syndicat.objects.create(
        email="syndicat1@example.com", username="Syndicat 1"
    )
    syndicat2 = Syndicat.objects.create(
        email="syndicat2@example.com", username="Syndicat 2"
    )
    corps = Corps.objects.create(code_corps="123")
    for i in range(4):
        UtilisationTempsDecharge.objects.create(
            civilite="MME",
            prenom="Michelle",
            nom="MARTIN",
            heures_de_decharges=0.1,
            heures_d_obligation_de_service=35,
            corps=corps,
            code_etablissement_rne="1234567A",
            syndicat=syndicat2,
            annee=2009 + i,
        )
    for i in range(3):
        UtilisationTempsDecharge.objects.create(
            civilite="MME",
            prenom="Michelle",
            nom="MARTIN",
            heures_de_decharges=0.1,
            heures_d_obligation_de_service=35,
            corps=corps,
            code_etablissement_rne="1234567A",
            syndicat=syndicat2,
            annee=2014 + i,
        )

    UtilisationTempsDecharge.objects.create(
        civilite="MME",
        prenom="Michelle",
        nom="MARTIN",
        heures_de_decharges=0.1,
        heures_d_obligation_de_service=35,
        corps=corps,
        code_etablissement_rne="1234567A",
        syndicat=syndicat2,
        annee=2018,
    )
    TempsDeDecharge.objects.create(
        syndicat_beneficiaire=syndicat,
        syndicat_donateur=federation,
        annee=2020,
        temps_de_decharge_etp=10,
    )
    client.force_login(syndicat)
    response = client.post(
        reverse("decharge:ajouter_beneficiaire"),
        {
            "civilite": "MME",
            "prenom": "Michelle",
            "nom": "MARTIN",
            "int_heures_de_decharges": 10,
            "minutes_de_decharges": 14,
            "heures_d_obligation_de_service": 35,
            "corps": corps.pk,
            "code_etablissement_rne": "1234567A",
        },
    )
    assert response.status_code == 200
    assert (
        response.context["form"].errors["__all__"][0]
        == "La ou le bénéficiaire cumule déjà 8 années consécutives de décharges, il ou elle ne peut donc pas bénéficier de décharges cette année"
    )


def test_ajouter_beneficiaire__depasse_3_etp_consecutifs(client):
    federation = Syndicat.objects.create(
        is_superuser=True, email="admin@example.com", username="Fédération"
    )
    ParametresDApplication.objects.create(
        annee_en_cours=2020,
        corps_annexe=SimpleUploadedFile("file.pdf", b"random data"),
    )
    syndicat = Syndicat.objects.create(
        email="syndicat1@example.com", username="Syndicat 1"
    )
    syndicat2 = Syndicat.objects.create(
        email="syndicat2@example.com", username="Syndicat 2"
    )
    corps = Corps.objects.create(code_corps="123")
    for i in range(4):
        UtilisationTempsDecharge.objects.create(
            civilite="MME",
            prenom="Michelle",
            nom="MARTIN",
            heures_de_decharges=1,
            heures_d_obligation_de_service=35,
            corps=corps,
            code_etablissement_rne="1234567A",
            syndicat=syndicat2,
            annee=2008 + i,
        )  # le compteur est remis à 0 après ces annees
    for i in range(5):
        UtilisationTempsDecharge.objects.create(
            civilite="MME",
            prenom="Michelle",
            nom="MARTIN",
            heures_de_decharges=110,
            heures_d_obligation_de_service=200,
            corps=corps,
            code_etablissement_rne="1234567A",
            syndicat=syndicat2,
            annee=2014 + i,
        )
    TempsDeDecharge.objects.create(
        syndicat_beneficiaire=syndicat,
        syndicat_donateur=federation,
        annee=2020,
        temps_de_decharge_etp=10,
    )
    client.force_login(syndicat)
    response = client.post(
        reverse("decharge:ajouter_beneficiaire"),
        {
            "civilite": "MME",
            "prenom": "Michelle",
            "nom": "MARTIN",
            "int_heures_de_decharges": 10,
            "minutes_de_decharges": 0,
            "heures_d_obligation_de_service": 35,
            "corps": corps.pk,
            "code_etablissement_rne": "1234567A",
        },
    )
    assert response.status_code == 200
    assert (
        response.context["form"].errors["__all__"][0]
        == "La ou le bénéficiaire cumule déjà 2.750ETP consécutifs de décharges sur les dernières années (+l'année en cours) et vous essayez de rajouter 0.286ETP"
    )


def test_renommer_beneficiaire(client):
    federation = Syndicat.objects.create(
        is_superuser=True, email="admin@example.com", username="Fédération"
    )
    ParametresDApplication.objects.create(
        annee_en_cours=2020,
        corps_annexe=SimpleUploadedFile("file.pdf", b"random data"),
    )
    syndicat = Syndicat.objects.create(
        email="syndicat1@example.com", username="Syndicat 1"
    )
    corps = Corps.objects.create(code_corps="123")
    utilisation_temps = UtilisationTempsDecharge.objects.create(
        civilite="MME",
        prenom="Michelle",
        nom="MARTIN",
        heures_de_decharges=1,
        heures_d_obligation_de_service=35,
        corps=corps,
        code_etablissement_rne="1234567A",
        syndicat=syndicat,
        annee=2020,
    )
    client.force_login(federation)
    response = client.post(
        reverse("decharge:renommer_beneficiaire"),
        {
            "ancien_prenom": "Michelle",
            "ancien_nom": "MARTIN",
            "ancien_rne": "1234567A",
            "nouveau_prenom": "Michel",
            "nouveau_nom": "MARTINE",
            "nouveau_rne": "1234567B",
        },
    )
    utilisation_temps.refresh_from_db()
    assert response.status_code == 302
    assert (
        str(list(get_messages(response.wsgi_request))[0])
        == "1 déclarations de temps ont été mis à jour"
    )
    assert utilisation_temps.prenom == "Michel"
    assert utilisation_temps.nom == "MARTINE"
    assert utilisation_temps.code_etablissement_rne == "1234567B"

    response = client.post(
        reverse("decharge:renommer_beneficiaire"),
        {
            "ancien_prenom": "Michelle",
            "ancien_nom": "MARTIN",
            "ancien_rne": "1234567A",
            "nouveau_prenom": "Michel",
            "nouveau_nom": "MARTINE",
            "nouveau_rne": "1234567B",
        },
    )
    utilisation_temps.refresh_from_db()
    assert response.status_code == 302
    assert (
        str(list(get_messages(response.wsgi_request))[1])
        == "Aucun·e bénéficiaire ne correspondait à vos données, aucun changement n'a été effectué"
    )
