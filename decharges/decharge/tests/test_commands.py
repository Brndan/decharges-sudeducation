from decimal import Decimal

import pytest
from django.conf import settings
from django.core.management import call_command

from decharges.decharge.models import UtilisationTempsDecharge
from decharges.user_manager.models import Syndicat

pytestmark = pytest.mark.django_db


def test_import_historique__no_federation():
    assert UtilisationTempsDecharge.objects.count() == 0
    with pytest.raises(SystemExit):
        call_command(
            "import_historique",
            "-f",
            "decharges/decharge/tests/assets/historique.example.csv",
        )
    assert UtilisationTempsDecharge.objects.count() == 0


def test_import_historique():
    assert UtilisationTempsDecharge.objects.count() == 0
    federation = Syndicat.objects.create(is_superuser=True)
    call_command(
        "import_historique",
        "-f",
        "decharges/decharge/tests/assets/historique.example.csv",
    )
    assert UtilisationTempsDecharge.objects.count() == 228
    utilisation_tps_decharge = UtilisationTempsDecharge.objects.get(
        prenom="Example1", nom="EXAMPLE-1", annee=2012
    )
    assert utilisation_tps_decharge.etp_utilises == round(
        Decimal(1 / 6), settings.PRECISION_ETP
    )
    call_command(
        "import_historique",
        "-f",
        "decharges/decharge/tests/assets/historique.example2.csv",
    )
    utilisation_tps_decharge = UtilisationTempsDecharge.objects.get(
        prenom="Example1", nom="EXAMPLE-1", annee=2012
    )
    assert UtilisationTempsDecharge.objects.count() == 228
    assert utilisation_tps_decharge.etp_utilises == 2
    assert utilisation_tps_decharge.syndicat == federation
    assert utilisation_tps_decharge.code_etablissement_rne == "11"
    assert utilisation_tps_decharge.corps.code_corps == "CERT"
