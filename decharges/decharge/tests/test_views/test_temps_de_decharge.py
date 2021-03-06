from decimal import Decimal

import pytest
from django.conf import settings
from django.urls import reverse

from decharges.decharge.models import TempsDeDecharge
from decharges.parametre.models import ParametresDApplication
from decharges.user_manager.models import Academie, Syndicat

pytestmark = pytest.mark.django_db


def test_ajouter_mutualisation_academique(client):
    federation = Syndicat.objects.create(
        is_superuser=True, email="admin@example.com", username="Fédération"
    )
    ParametresDApplication.objects.create(annee_en_cours=2020)
    academie = Academie.objects.create(nom="Academie1")
    syndicat = Syndicat.objects.create(
        email="syndicat1@example.com", username="Syndicat 1", academie=academie
    )
    syndicat2 = Syndicat.objects.create(
        email="syndicat2@example.com", username="Syndicat 2", academie=academie
    )
    TempsDeDecharge.objects.create(
        syndicat_beneficiaire=syndicat,
        syndicat_donateur=federation,
        annee=2020,
        temps_de_decharge_etp=10,
    )
    client.force_login(syndicat)
    response = client.get(reverse("decharge:ajouter_mutualisation_academique"))
    assert response.status_code == 200
    response = client.post(
        reverse("decharge:ajouter_mutualisation_academique"),
        {
            "syndicat_beneficiaire": syndicat2.pk,
            "temps_de_decharge_etp": 0.1,
        },
    )
    assert response.status_code == 302
    assert TempsDeDecharge.objects.count() == 2
    utilisation_tps = TempsDeDecharge.objects.filter(
        syndicat_beneficiaire=syndicat2
    ).first()
    assert utilisation_tps.syndicat_beneficiaire == syndicat2
    assert utilisation_tps.syndicat_donateur == syndicat
    assert utilisation_tps.annee == 2020
    assert utilisation_tps.temps_de_decharge_etp == round(
        Decimal(0.1), settings.PRECISION_ETP
    )


def test_ajouter_mutualisation_academique__unique_together(client):
    federation = Syndicat.objects.create(
        is_superuser=True, email="admin@example.com", username="Fédération"
    )
    ParametresDApplication.objects.create(annee_en_cours=2020)
    academie = Academie.objects.create(nom="Academie1")
    syndicat = Syndicat.objects.create(
        email="syndicat1@example.com", username="Syndicat 1", academie=academie
    )
    syndicat2 = Syndicat.objects.create(
        email="syndicat2@example.com", username="Syndicat 2", academie=academie
    )
    TempsDeDecharge.objects.create(
        syndicat_beneficiaire=syndicat,
        syndicat_donateur=federation,
        annee=2020,
        temps_de_decharge_etp=10,
    )
    client.force_login(syndicat)
    response = client.get(reverse("decharge:ajouter_mutualisation_academique"))
    assert response.status_code == 200
    assert TempsDeDecharge.objects.count() == 1
    response = client.post(
        reverse("decharge:ajouter_mutualisation_academique"),
        {
            "syndicat_beneficiaire": syndicat2.pk,
            "temps_de_decharge_etp": 0.1,
        },
    )
    assert response.status_code == 302
    assert TempsDeDecharge.objects.count() == 2
    response = client.post(
        reverse("decharge:ajouter_mutualisation_academique"),
        {
            "syndicat_beneficiaire": syndicat2.pk,
            "temps_de_decharge_etp": 0.1,
        },
    )
    assert response.status_code == 200
    assert (
        response.context["form"].errors["__all__"][0]
        == "Un partage de temps pour ce syndicat existe déjà, veuillez plutôt le mettre à jour"
    )
    assert TempsDeDecharge.objects.count() == 2


def test_ajouter_mutualisation_academique__federation(client):
    federation = Syndicat.objects.create(
        is_superuser=True, email="admin@example.com", username="Fédération"
    )
    ParametresDApplication.objects.create(annee_en_cours=2020)
    academie = Academie.objects.create(nom="Academie1")
    syndicat = Syndicat.objects.create(
        email="syndicat1@example.com", username="Syndicat 1", academie=academie
    )
    client.force_login(federation)
    TempsDeDecharge.objects.create(
        syndicat_beneficiaire=federation,
        syndicat_donateur=None,
        annee=2020,
        temps_de_decharge_etp=10,
    )
    response = client.get(reverse("decharge:ajouter_mutualisation_academique"))
    assert response.status_code == 200
    response = client.post(
        reverse("decharge:ajouter_mutualisation_academique"),
        {
            "syndicat_beneficiaire": syndicat.pk,
            "temps_de_decharge_etp": 0.1,
        },
    )
    assert response.status_code == 302
    assert TempsDeDecharge.objects.count() == 2
    utilisation_tps = TempsDeDecharge.objects.filter(
        syndicat_beneficiaire=syndicat
    ).first()
    assert utilisation_tps.syndicat_beneficiaire == syndicat
    assert utilisation_tps.syndicat_donateur == federation
    assert utilisation_tps.annee == 2020
    assert utilisation_tps.temps_de_decharge_etp == round(
        Decimal(0.1), settings.PRECISION_ETP
    )


def test_maj_mutualisation_academique(client):
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
    TempsDeDecharge.objects.create(
        syndicat_beneficiaire=syndicat,
        syndicat_donateur=federation,
        annee=2020,
        temps_de_decharge_etp=10,
    )
    client.force_login(syndicat2)
    utilisation_tps = TempsDeDecharge.objects.create(
        syndicat_donateur=syndicat,
        syndicat_beneficiaire=syndicat2,
        temps_de_decharge_etp=0.1,
        annee=2020,
    )
    response = client.get(
        reverse(
            "decharge:modifier_mutualisation_academique",
            kwargs={"pk": utilisation_tps.pk},
        )
    )
    assert response.status_code == 404  # check permission
    client.force_login(syndicat)
    response = client.get(
        reverse(
            "decharge:modifier_mutualisation_academique",
            kwargs={"pk": utilisation_tps.pk},
        )
    )
    assert response.status_code == 200
    response = client.post(
        reverse(
            "decharge:modifier_mutualisation_academique",
            kwargs={"pk": utilisation_tps.pk},
        ),
        {
            "syndicat_beneficiaire": syndicat2.pk,
            "temps_de_decharge_etp": 0.5,
        },
    )
    assert response.status_code == 302

    utilisation_tps.refresh_from_db()
    assert utilisation_tps.syndicat_beneficiaire == syndicat2
    assert utilisation_tps.syndicat_donateur == syndicat
    assert utilisation_tps.annee == 2020
    assert utilisation_tps.temps_de_decharge_etp == 0.5


def test_suppression_mutualisation_academique(client):
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
    utilisation_tps = TempsDeDecharge.objects.create(
        syndicat_donateur=syndicat,
        syndicat_beneficiaire=syndicat2,
        temps_de_decharge_etp=0.1,
        annee=2020,
    )
    response = client.get(
        reverse(
            "decharge:supprimer_mutualisation_academique",
            kwargs={"pk": utilisation_tps.pk},
        )
    )
    assert response.status_code == 404  # check permission
    client.force_login(syndicat)
    response = client.get(
        reverse(
            "decharge:supprimer_mutualisation_academique",
            kwargs={"pk": utilisation_tps.pk},
        )
    )
    assert response.status_code == 200
    response = client.post(
        reverse(
            "decharge:supprimer_mutualisation_academique",
            kwargs={"pk": utilisation_tps.pk},
        )
    )
    assert response.status_code == 302
    assert TempsDeDecharge.objects.count() == 0


def test_ajouter_quota_federation(client):
    federation = Syndicat.objects.create(
        is_superuser=True, email="admin@example.com", username="Fédération"
    )
    ParametresDApplication.objects.create(annee_en_cours=2020)
    client.force_login(federation)
    response = client.get(reverse("decharge:ajouter_quota_federation"))
    assert response.status_code == 200
    response = client.post(
        reverse("decharge:ajouter_quota_federation"),
        {
            "temps_de_decharge_etp": 0.1,
        },
    )
    assert response.status_code == 302
    assert TempsDeDecharge.objects.count() == 1
    utilisation_tps = TempsDeDecharge.objects.first()
    assert utilisation_tps.syndicat_beneficiaire == federation
    assert utilisation_tps.syndicat_donateur is None
    assert utilisation_tps.annee == 2020
    assert utilisation_tps.temps_de_decharge_etp == round(
        Decimal(0.1), settings.PRECISION_ETP
    )


def test_maj_quota_federation(client):
    federation = Syndicat.objects.create(
        is_superuser=True, email="admin@example.com", username="Fédération"
    )
    ParametresDApplication.objects.create(annee_en_cours=2021)
    client.force_login(federation)
    utilisation_tps = TempsDeDecharge.objects.create(
        syndicat_beneficiaire=federation,
        temps_de_decharge_etp=0.1,
        annee=2020,
    )
    response = client.get(
        reverse(
            "decharge:modifier_quota_federation",
            kwargs={"pk": utilisation_tps.pk},
        )
    )
    assert response.status_code == 200
    response = client.post(
        reverse(
            "decharge:modifier_quota_federation",
            kwargs={"pk": utilisation_tps.pk},
        ),
        {
            "temps_de_decharge_etp": 0.5,
        },
    )
    assert response.status_code == 302

    utilisation_tps.refresh_from_db()
    assert utilisation_tps.syndicat_beneficiaire == federation
    assert utilisation_tps.syndicat_donateur is None
    assert utilisation_tps.annee == 2020
    assert utilisation_tps.temps_de_decharge_etp == 0.5


def test_ajouter_mutualisation_academique__pas_assez_de_quota(client):
    Syndicat.objects.create(
        is_superuser=True, email="admin@example.com", username="Fédération"
    )
    ParametresDApplication.objects.create(annee_en_cours=2020)
    academie = Academie.objects.create(nom="Academie1")
    syndicat = Syndicat.objects.create(
        email="syndicat1@example.com", username="Syndicat 1", academie=academie
    )
    syndicat2 = Syndicat.objects.create(
        email="syndicat2@example.com", username="Syndicat 2", academie=academie
    )
    client.force_login(syndicat)
    response = client.post(
        reverse("decharge:ajouter_mutualisation_academique"),
        {
            "syndicat_beneficiaire": syndicat2.pk,
            "temps_de_decharge_etp": 0.1,
        },
    )
    assert response.status_code == 200
    assert (
        response.context["form"].errors["__all__"][0]
        == "Vous dépassez le quota du syndicat, il reste 0.000 ETP attribuable et vous essayez d'ajouter 0.100 ETP"
    )
    assert TempsDeDecharge.objects.count() == 0
