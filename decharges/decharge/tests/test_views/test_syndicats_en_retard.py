import pytest
from django.urls import reverse

from decharges.decharge.models import (
    TempsDeDecharge,
    UtilisationCreditDeTempsSyndicalPonctuel,
    UtilisationTempsDecharge,
)
from decharges.parametre.models import ParametresDApplication
from decharges.user_manager.models import Syndicat

pytestmark = pytest.mark.django_db


def test_synthese_cts(client):
    federation = Syndicat.objects.create(
        is_superuser=True, email="admin@example.com", username="Fédération"
    )
    ParametresDApplication.objects.create(annee_en_cours=2021)
    TempsDeDecharge.objects.create(
        syndicat_beneficiaire=federation, annee=2021, temps_de_decharge_etp=10
    )
    syndicat1 = Syndicat.objects.create(
        email="syndicat1@example.com", username="Syndicat 1"
    )
    syndicat2 = Syndicat.objects.create(
        email="syndicat2@example.com", username="Syndicat 2"
    )
    syndicat3 = Syndicat.objects.create(
        email="syndicat3@example.com", username="Syndicat 3"
    )
    syndicat4 = Syndicat.objects.create(
        email="syndicat4@example.com", username="Syndicat 4"
    )
    UtilisationTempsDecharge.objects.create(
        prenom="Foo",
        nom="BAR",
        heures_de_decharges=10,
        heures_d_obligation_de_service=35,
        code_etablissement_rne="1234567A",
        annee=2021,
        syndicat=syndicat1,
    )
    UtilisationCreditDeTempsSyndicalPonctuel.objects.create(
        demi_journees_de_decharges=5, syndicat=syndicat2, annee=2021
    )

    UtilisationCreditDeTempsSyndicalPonctuel.objects.create(
        demi_journees_de_decharges=5, syndicat=syndicat4, annee=2020  # année passée
    )
    TempsDeDecharge.objects.create(
        syndicat_beneficiaire=syndicat1,
        syndicat_donateur=syndicat3,
        temps_de_decharge_etp=0.1,
        annee=2021,
    )

    client.force_login(federation)
    response = client.get(reverse("decharge:syndicats_en_retard"))
    assert response.status_code == 200
    assert response.context["syndicats_a_relancer"].count() == 1
    assert response.context["syndicats_a_relancer"].first() == syndicat4
