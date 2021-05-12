import pytest

from decharges.decharge.admin import TempsDeDechargeAdmin
from decharges.decharge.models import Corps, TempsDeDecharge, UtilisationTempsDecharge
from decharges.parametre.admin import import_corps
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


def test_import_corps():
    syndicat = Syndicat.objects.create()
    corps = Corps.objects.create(code_corps="xxx")
    Corps.objects.create(code_corps="zzz")
    UtilisationTempsDecharge.objects.create(
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
    with open("decharges/decharge/tests/assets/corps_example.ods", "rb") as f:
        import_corps(f)
    assert Corps.objects.count() == 513
    assert Corps.objects.filter(code_corps="zzz").count() == 0
    assert Corps.objects.filter(code_corps="xxx").count() == 1

    # test idempotency
    with open("decharges/decharge/tests/assets/corps_example.ods", "rb") as f:
        import_corps(f)
    assert Corps.objects.count() == 513
    assert Corps.objects.filter(code_corps="zzz").count() == 0
    assert Corps.objects.filter(code_corps="xxx").count() == 1
