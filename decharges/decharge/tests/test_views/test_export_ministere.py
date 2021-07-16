import datetime
from io import BytesIO

import pandas
import pytest
from django.urls import reverse
from django.utils import timezone

from decharges.decharge.models import Corps, UtilisationTempsDecharge
from decharges.parametre.models import ParametresDApplication
from decharges.user_manager.models import Syndicat

pytestmark = pytest.mark.django_db


def test_export_ministere(client):
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
    corps = Corps.objects.create(code_corps="023")
    client.force_login(federation)
    UtilisationTempsDecharge.objects.create(
        civilite="M.",
        prenom="Foo",
        nom="BAR",
        heures_de_decharges=40.25,
        heures_d_obligation_de_service=1607,
        code_etablissement_rne="0234567A",
        annee=2021,
        syndicat=syndicat,
        corps=corps,
        date_debut_decharge=datetime.date(year=2021, month=10, day=9),
    )
    UtilisationTempsDecharge.objects.create(
        civilite="M.",
        prenom="Foo",
        nom="BAR",
        heures_de_decharges=10,
        heures_d_obligation_de_service=1607,
        code_etablissement_rne="0234567A",
        annee=2021,
        syndicat=syndicat2,
        corps=corps,
        date_debut_decharge=datetime.date(year=2021, month=10, day=9),
    )
    UtilisationTempsDecharge.objects.create(
        civilite="M.",
        prenom="Foo",
        nom="BAR",
        heures_de_decharges=10,
        heures_d_obligation_de_service=1607,
        code_etablissement_rne="0234567A",
        annee=2021,
        syndicat=syndicat2,
        corps=corps,
        est_une_decharge_solidaires=True,
        date_debut_decharge=datetime.date(year=2021, month=10, day=9),
    )
    UtilisationTempsDecharge.objects.create(
        civilite="M.",
        prenom="Foo",
        nom="BAR",
        heures_de_decharges=10,
        heures_d_obligation_de_service=1607,
        code_etablissement_rne="0234567B",
        annee=2021,
        syndicat=syndicat,
        corps=corps,
    )
    UtilisationTempsDecharge.objects.create(
        civilite="M.",
        prenom="Foo",
        nom="BAR",
        heures_de_decharges=10,
        heures_d_obligation_de_service=1607,
        code_etablissement_rne="0234567B",
        annee=2020,
        syndicat=syndicat,
        corps=corps,
    )
    UtilisationTempsDecharge.objects.create(
        civilite="M.",
        prenom="Foo2",
        nom="BAR",
        heures_de_decharges=10,
        heures_d_obligation_de_service=1607,
        code_etablissement_rne="0234567B",
        annee=2021,
        syndicat=syndicat,
        supprime_a=timezone.now(),
        corps=corps,
    )
    res = client.get(reverse("decharge:export_ministere"))
    document = pandas.read_csv(BytesIO(res.content), dtype="string")
    rows = list(document.iterrows())
    assert len(rows) == 2
    assert rows[0][1]["Code organisation"] == "S01"
    assert rows[0][1]["Code civilité"] == "M."
    assert rows[0][1]["Prénom"] == "Foo"
    assert rows[0][1]["Nom"] == "BAR"
    assert rows[0][1]["Heures de décharge"] == "50"
    assert rows[0][1]["Minutes de décharge"] == "15"
    assert rows[0][1]["Heures d'obligations de service"] == "1607"
    assert rows[0][1]["Aire"] == "2"
    assert rows[0][1]["Corps"] == "023"
    assert rows[0][1]["Etablissement"] == "0234567A"
    assert rows[0][1]["Date d'effet"] == "09/10/2021"
    assert rows[0][1]["Date de fin"] == "31/08/2022"

    assert rows[1][1]["Code organisation"] == "S01"
    assert rows[1][1]["Code civilité"] == "M."
    assert rows[1][1]["Prénom"] == "Foo"
    assert rows[1][1]["Nom"] == "BAR"
    assert rows[1][1]["Heures de décharge"] == "10"
    assert rows[1][1]["Minutes de décharge"] == "0"
    assert rows[1][1]["Heures d'obligations de service"] == "1607"
    assert rows[1][1]["Aire"] == "2"
    assert rows[1][1]["Corps"] == "023"
    assert rows[1][1]["Etablissement"] == "0234567B"
    assert rows[1][1]["Date d'effet"] == "01/09/2021"
    assert rows[1][1]["Date de fin"] == "31/08/2022"
