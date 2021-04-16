from decimal import Decimal

import pytest
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from decharges.decharge.models import (
    Corps,
    TempsDeDecharge,
    UtilisationCreditDeTempsSyndicalPonctuel,
    UtilisationTempsDecharge,
)
from decharges.decharge.validators import validate_first_name, validate_last_name
from decharges.user_manager.models import Syndicat

pytestmark = pytest.mark.django_db


def test_instanciate_temps_decharge():
    syndicat = Syndicat.objects.create(username="Syndic1")
    tps_decharge = TempsDeDecharge.objects.create(
        syndicat_beneficiaire=syndicat, annee=2021, temps_de_decharge_etp=0.5
    )
    assert syndicat.temps_de_decharges_par_annee.filter(annee=2021).count() == 1
    assert f"{tps_decharge}" == "0.5 ETP à Syndic1 en 2021"


def test_instanciate_corps():
    corps1 = Corps.objects.create(code_corps="123")
    corps2 = Corps.objects.create(code_corps="456", description="Description")
    assert Corps.objects.count() == 2
    assert f"{corps1}" == "123"
    assert f"{corps2}" == "456 (Description)"


def test_instanciate_utilisation_temps_decharge():
    corps = Corps.objects.create(code_corps="123")
    syndicat = Syndicat.objects.create()
    tps_decharge = UtilisationTempsDecharge.objects.create(
        prenom="Foo",
        nom="BAR",
        heures_de_decharges=10,
        heures_d_obligation_de_service=35,
        corps=corps,
        code_etablissement_rne="1234567A",
        annee=2021,
        syndicat=syndicat,
    )
    assert UtilisationTempsDecharge.objects.first().etp_utilises == round(
        Decimal(10 / 35), settings.PRECISION_ETP
    )
    tps_decharge.etp = Decimal(7 / 35)
    tps_decharge.save()
    assert UtilisationTempsDecharge.objects.first().etp_utilises == round(
        Decimal(7 / 35), settings.PRECISION_ETP
    )

    corps2 = Corps.objects.create(code_corps="456")
    with pytest.raises(IntegrityError):
        UtilisationTempsDecharge.objects.create(
            prenom="Foo",
            nom="BAR",
            heures_de_decharges=2,
            heures_d_obligation_de_service=36,
            corps=corps2,
            code_etablissement_rne="8912345B",
            annee=2021,
            syndicat=syndicat,
        )


def test_instanciate_utilisation_cts():
    syndicat = Syndicat.objects.create()
    UtilisationCreditDeTempsSyndicalPonctuel.objects.create(
        demi_journees_de_decharges=13,
        syndicat=syndicat,
        annee=2021,
    )
    assert (
        UtilisationCreditDeTempsSyndicalPonctuel.objects.first().etp_utilises
        == round(
            Decimal(13 * 3.5 / settings.NB_HOURS_IN_A_YEAR), settings.PRECISION_ETP
        )
    )

    with pytest.raises(IntegrityError):
        UtilisationCreditDeTempsSyndicalPonctuel.objects.create(
            demi_journees_de_decharges=15,
            syndicat=syndicat,
            annee=2021,
        )


def test_validate_first_name():
    with pytest.raises(ValidationError) as excinfo:
        validate_first_name("test")
    assert excinfo.value.message == "Le prénom doit commencer par une majuscule"

    with pytest.raises(ValidationError) as excinfo:
        validate_first_name(" Test")
    assert excinfo.value.message == "Le prénom ne peut pas commencer par un espace"

    with pytest.raises(ValidationError) as excinfo:
        validate_first_name("Test  Test")
    assert (
        excinfo.value.message == "Le prénom ne doit pas contenir 2 espaces consécutifs"
    )

    with pytest.raises(ValidationError) as excinfo:
        validate_first_name("Test ")
    assert excinfo.value.message == "Le prénom ne doit pas se terminer par un espace"

    with pytest.raises(ValidationError) as excinfo:
        validate_first_name("Test|")
    assert excinfo.value.message == "Des caractères non-autorisés sont présents : |"

    validate_first_name("Tést de nom-complïqué")


def test_validate_last_name():
    with pytest.raises(ValidationError) as excinfo:
        validate_last_name("TESTéR")
    assert excinfo.value.message == "Le nom doit être en majuscule"

    with pytest.raises(ValidationError) as excinfo:
        validate_last_name(" TEST")
    assert excinfo.value.message == "Le nom ne peut pas commencer par un espace"

    with pytest.raises(ValidationError) as excinfo:
        validate_last_name("TEST  TEST")
    assert excinfo.value.message == "Le nom ne doit pas contenir 2 espaces consécutifs"

    with pytest.raises(ValidationError) as excinfo:
        validate_last_name("TEST ")
    assert excinfo.value.message == "Le nom ne doit pas se terminer par un espace"

    with pytest.raises(ValidationError) as excinfo:
        validate_last_name("TEST|")
    assert excinfo.value.message == "Des caractères non-autorisés sont présents : |"

    validate_last_name("TÉST DE NOM-COMPLÎQUÉ")
