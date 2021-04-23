import pandas
import pytest
from django.urls import reverse

from decharges.decharge.models import Corps, UtilisationTempsDecharge
from decharges.parametre.models import ParametresDApplication
from decharges.user_manager.models import Syndicat

pytestmark = pytest.mark.django_db


def test_historique(client):
    federation = Syndicat.objects.create(
        is_superuser=True, email="admin@example.com", username="Fédération"
    )
    ParametresDApplication.objects.create(annee_en_cours=2021)
    syndicat = Syndicat.objects.create(
        email="syndicat1@example.com", username="Syndicat 1"
    )
    client.force_login(federation)
    corps = Corps.objects.create(code_corps="023")
    for annee in range(2014, 2022):
        UtilisationTempsDecharge.objects.create(
            civilite="M.",
            prenom="Foo",
            nom="BAR",
            heures_de_decharges=20,
            heures_d_obligation_de_service=35,
            code_etablissement_rne="0234567A",
            annee=annee,
            syndicat=syndicat,
            corps=corps,
        )
    for annee in range(2012, 2018):
        UtilisationTempsDecharge.objects.create(
            civilite="M.",
            prenom="Foo2",
            nom="BAR",
            heures_de_decharges=20,
            heures_d_obligation_de_service=35,
            code_etablissement_rne="0234567A",
            annee=annee,
            syndicat=syndicat,
            corps=corps,
        )
    for annee in range(2020, 2022):
        UtilisationTempsDecharge.objects.create(
            civilite="M.",
            prenom="Foo2",
            nom="BAR",
            heures_de_decharges=20,
            heures_d_obligation_de_service=35,
            code_etablissement_rne="0234567A",
            annee=annee,
            syndicat=syndicat,
            corps=corps,
        )
    response = client.get(reverse("decharge:historique"))
    assert response.status_code == 200
    assert response.context["annee_en_cours"] == 2021
    assert response.context["row_iterator"] == [0, 1]
    assert len(response.context["beneficiaires_approchant_les_limites"]) == 1
    assert response.context["beneficiaires_approchant_les_limites"][
        "Foo BAR (0234567A)"
    ] == {"annees_consecutives": 8, "etp_consecutifs": 4.571}

    # download history
    response = client.get(reverse("decharge:telecharger_historique"))
    document = pandas.read_excel(response.content)
    assert len(list(document.iterrows())) == 2
    assert list(document.iterrows())[0][1]["Civilité"] == "M."
    assert list(document.iterrows())[0][1]["Prénom"] == "Foo"
    assert list(document.iterrows())[0][1][2021] == 0.57143
    assert list(document.iterrows())[1][1]["Civilité"] == "M."
    assert list(document.iterrows())[1][1]["Prénom"] == "Foo2"
    assert list(document.iterrows())[1][1][2021] == 0.57143

    # download limites règles
    response = client.get(reverse("decharge:telecharger_regles"))
    document = pandas.read_excel(response.content)
    assert len(list(document.iterrows())) == 1
    assert list(document.iterrows())[0][1]["Identifiant"] == "Foo BAR (0234567A)"
    assert list(document.iterrows())[0][1]["Années consecutives"] == 8
    assert list(document.iterrows())[0][1]["Cumul d'ETP"] == 4.571
