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
    document = pandas.read_excel(res.content, dtype="string")
    assert len(list(document.iterrows())) == 2
    assert list(document.iterrows())[0][1]["Code organisation"] == "S01"
    assert list(document.iterrows())[0][1]["M. Mme"] == "M."
    assert list(document.iterrows())[0][1]["Prénom"] == "Foo"
    assert list(document.iterrows())[0][1]["Nom"] == "BAR"
    assert list(document.iterrows())[0][1]["Heures décharges"] == "50"
    assert list(document.iterrows())[0][1]["Minutes décharges"] == "15"
    assert list(document.iterrows())[0][1]["Heures ORS"] == "1607"
    assert list(document.iterrows())[0][1]["Minutes ORS"] == "0"
    assert list(document.iterrows())[0][1]["AIRE"] == "2"
    assert list(document.iterrows())[0][1]["Corps"] == "023"
    assert list(document.iterrows())[0][1]["RNE"] == "0234567A"

    assert list(document.iterrows())[1][1]["Code organisation"] == "S01"
    assert list(document.iterrows())[1][1]["M. Mme"] == "M."
    assert list(document.iterrows())[1][1]["Prénom"] == "Foo"
    assert list(document.iterrows())[1][1]["Nom"] == "BAR"
    assert list(document.iterrows())[1][1]["Heures décharges"] == "10"
    assert list(document.iterrows())[1][1]["Minutes décharges"] == "0"
    assert list(document.iterrows())[1][1]["Heures ORS"] == "1607"
    assert list(document.iterrows())[1][1]["Minutes ORS"] == "0"
    assert list(document.iterrows())[1][1]["AIRE"] == "2"
    assert list(document.iterrows())[1][1]["Corps"] == "023"
    assert list(document.iterrows())[1][1]["RNE"] == "0234567B"
