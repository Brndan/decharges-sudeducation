from decharges.decharge.views.accueil import PageAccueilSyndicatView
from decharges.decharge.views.cts import CTSCreate, CTSUpdate
from decharges.decharge.views.export_ministere import ExportMinistere
from decharges.decharge.views.historique import HistoriquePage, HistoriqueTelecharger
from decharges.decharge.views.import_temps_syndicats import ImportTempsSyndicats
from decharges.decharge.views.syndicats_en_retard import SyndicatsEnRetard
from decharges.decharge.views.synthese_cts import SyntheseCTS
from decharges.decharge.views.temps_de_decharge import (
    CreateQuotaETPFederation,
    CreateTempsDeDecharge,
    SuppressionTempsDeDecharge,
    UpdateQuotaETPFederation,
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
    "CreateQuotaETPFederation",
    "CreateTempsDeDecharge",
    "CreateUtilisationTempsDecharge",
    "ExportMinistere",
    "HistoriquePage",
    "HistoriqueTelecharger",
    "ImportTempsSyndicats",
    "PageAccueilSyndicatView",
    "SuppressionTempsDeDecharge",
    "SuppressionUtilisationTempsDecharge",
    "SyndicatsEnRetard",
    "SyntheseCTS",
    "UpdateQuotaETPFederation",
    "UpdateTempsDeDecharge",
    "UpdateUtilisationTempsDecharge",
]
