import pytest

from decharges.decharge.admin import TempsDeDechargeAdmin
from decharges.decharge.models import TempsDeDecharge
from decharges.user_manager.models import Syndicat

pytestmark = pytest.mark.django_db


def test_nom_syndicat_beneficiaire():
    syndicat = Syndicat.objects.create(username="test_username")
    tps_decharge = TempsDeDecharge.objects.create(
        syndicat_beneficiaire=syndicat, annee=2021, temps_de_decharge_etp=0.5
    )
    assert "test_username" == TempsDeDechargeAdmin.nom_syndicat_beneficiaire(
        tps_decharge
    )


def test_nom_syndicat_donateur():
    syndicat = Syndicat.objects.create(email="test1@example.com")
    syndicat_donateur = Syndicat.objects.create(
        username="test_username", email="test2@example.com"
    )
    tps_decharge1 = TempsDeDecharge.objects.create(
        syndicat_beneficiaire=syndicat, annee=2021, temps_de_decharge_etp=0.5
    )
    tps_decharge2 = TempsDeDecharge.objects.create(
        syndicat_beneficiaire=syndicat,
        annee=2021,
        temps_de_decharge_etp=0.5,
        syndicat_donateur=syndicat_donateur,
    )
    assert TempsDeDechargeAdmin.nom_syndicat_donateur(tps_decharge1) is None
    assert "test_username" == TempsDeDechargeAdmin.nom_syndicat_donateur(tps_decharge2)
