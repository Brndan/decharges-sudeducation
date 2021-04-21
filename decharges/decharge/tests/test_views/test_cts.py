from decimal import Decimal

import pytest
from django.conf import settings
from django.urls import reverse

from decharges.decharge.models import UtilisationCreditDeTempsSyndicalPonctuel
from decharges.parametre.models import ParametresDApplication
from decharges.user_manager.models import Academie, Syndicat

pytestmark = pytest.mark.django_db


def test_add_cts(client):
    Syndicat.objects.create(
        is_superuser=True, email="admin@example.com", username="Fédération"
    )
    ParametresDApplication.objects.create(annee_en_cours=2021)
    syndicat = Syndicat.objects.create(
        email="syndicat1@example.com", username="Syndicat 1"
    )
    client.force_login(syndicat)
    response = client.get(reverse("decharge:ajouter_cts"))
    assert response.status_code == 200
    response = client.post(
        reverse("decharge:ajouter_cts"), {"demi_journees_de_decharges": 5}
    )
    assert response.status_code == 302
    assert UtilisationCreditDeTempsSyndicalPonctuel.objects.count() == 1
    assert (
        UtilisationCreditDeTempsSyndicalPonctuel.objects.first().demi_journees_de_decharges
        == 5
    )
    assert UtilisationCreditDeTempsSyndicalPonctuel.objects.first().syndicat == syndicat


def test_update_cts(client):
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
    cts = UtilisationCreditDeTempsSyndicalPonctuel.objects.create(
        demi_journees_de_decharges=5, syndicat=syndicat, annee=2021
    )
    response = client.get(reverse("decharge:modifier_cts", kwargs={"pk": cts.pk}))
    assert response.status_code == 404
    client.force_login(syndicat)
    response = client.get(reverse("decharge:modifier_cts", kwargs={"pk": cts.pk}))
    assert response.status_code == 200
    response = client.post(
        reverse("decharge:modifier_cts", kwargs={"pk": cts.pk}),
        {"demi_journees_de_decharges": 8},
    )
    assert response.status_code == 302
    assert UtilisationCreditDeTempsSyndicalPonctuel.objects.count() == 1
    assert (
        UtilisationCreditDeTempsSyndicalPonctuel.objects.first().demi_journees_de_decharges
        == 8
    )
    assert UtilisationCreditDeTempsSyndicalPonctuel.objects.first().syndicat == syndicat


def test_synthese_cts(client):
    federation = Syndicat.objects.create(
        is_superuser=True, email="admin@example.com", username="Fédération"
    )
    ParametresDApplication.objects.create(annee_en_cours=2021)
    academie = Academie.objects.create(nom="Academie1")
    syndicat = Syndicat.objects.create(
        email="syndicat1@example.com", username="Syndicat 1", academie=academie
    )
    syndicat2 = Syndicat.objects.create(
        email="syndicat2@example.com", username="Syndicat 2", academie=academie
    )
    UtilisationCreditDeTempsSyndicalPonctuel.objects.create(
        demi_journees_de_decharges=5, syndicat=syndicat, annee=2021
    )
    UtilisationCreditDeTempsSyndicalPonctuel.objects.create(
        demi_journees_de_decharges=12, syndicat=syndicat2, annee=2021
    )
    client.force_login(federation)
    response = client.get(reverse("decharge:synthese_cts"))
    assert response.status_code == 200
    assert response.context["cts_par_academie"]["Academie1"] == round(
        Decimal(17) * Decimal(3.5) / settings.NB_HOURS_IN_A_YEAR, settings.PRECISION_ETP
    )
