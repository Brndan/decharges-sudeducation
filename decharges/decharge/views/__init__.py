from decharges.decharge.views.accueil import PageAccueilSyndicatView
from decharges.decharge.views.cts import CTSCreate, CTSUpdate
from decharges.decharge.views.export_ministere import ExportMinistere
from decharges.decharge.views.historique import HistoriquePage
from decharges.decharge.views.import_temps_syndicats import ImportTempsSyndicats
from decharges.decharge.views.synthese_cts import SyntheseCTS
from decharges.decharge.views.temps_de_decharge import (
    CreateTempsDeDecharge,
    SuppressionTempsDeDecharge,
    UpdateTempsDeDecharge,
)
from decharges.decharge.views.utilisation_temps_decharge import (
    CreateUtilisationTempsDecharge,
    SuppressionUtilisationTempsDecharge,
    UpdateUtilisationTempsDecharge,
)

__all__ = [
    "CTSCreate",
    "CTSUpdate",
    "CreateTempsDeDecharge",
    "CreateUtilisationTempsDecharge",
    "ExportMinistere",
    "HistoriquePage",
    "ImportTempsSyndicats",
    "PageAccueilSyndicatView",
    "SuppressionTempsDeDecharge",
    "SuppressionUtilisationTempsDecharge",
    "SyntheseCTS",
    "UpdateTempsDeDecharge",
    "UpdateUtilisationTempsDecharge",
]
