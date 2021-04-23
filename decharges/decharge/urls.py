from django.urls import path

from decharges.decharge.views import (
    ApprocheDesReglesTelecharger,
    CreateQuotaETPFederation,
    CreateTempsDeDecharge,
    CreateUtilisationTempsDecharge,
    CTSCreate,
    CTSUpdate,
    ExportMinistere,
    HistoriquePage,
    HistoriqueTelecharger,
    ImportTempsSyndicats,
    PageAccueilSyndicatView,
    SuppressionTempsDeDecharge,
    SuppressionUtilisationTempsDecharge,
    SyndicatsEnRetard,
    SyntheseCTS,
    UpdateQuotaETPFederation,
    UpdateTempsDeDecharge,
    UpdateUtilisationTempsDecharge,
)

app_name = "decharge"

urlpatterns = [
    path("", PageAccueilSyndicatView.as_view(), name="index"),
    path("import/", ImportTempsSyndicats.as_view(), name="import_temps"),
    path(
        "ajouter-beneficiare/",
        CreateUtilisationTempsDecharge.as_view(),
        name="ajouter_beneficiaire",
    ),
    path(
        "modifier-beneficiare/<int:pk>/",
        UpdateUtilisationTempsDecharge.as_view(),
        name="modifier_beneficiaire",
    ),
    path(
        "supprimer-beneficiare/<int:pk>/",
        SuppressionUtilisationTempsDecharge.as_view(),
        name="supprimer_beneficiaire",
    ),
    path("export-ministere/", ExportMinistere.as_view(), name="export_ministere"),
    path("historique/", HistoriquePage.as_view(), name="historique"),
    path(
        "historique/telecharger/",
        HistoriqueTelecharger.as_view(),
        name="telecharger_historique",
    ),
    path(
        "regles/telecharger/",
        ApprocheDesReglesTelecharger.as_view(),
        name="telecharger_regles",
    ),
    path("ajouter-cts/", CTSCreate.as_view(), name="ajouter_cts"),
    path("modifier-cts/<int:pk>/", CTSUpdate.as_view(), name="modifier_cts"),
    path("synthese-cts/", SyntheseCTS.as_view(), name="synthese_cts"),
    path(
        "ajouter-mutualisation-academique/",
        CreateTempsDeDecharge.as_view(),
        name="ajouter_mutualisation_academique",
    ),
    path(
        "modifier-mutualisation-academique/<int:pk>/",
        UpdateTempsDeDecharge.as_view(),
        name="modifier_mutualisation_academique",
    ),
    path(
        "supprimer-mutualisation-academique/<int:pk>/",
        SuppressionTempsDeDecharge.as_view(),
        name="supprimer_mutualisation_academique",
    ),
    path(
        "ajouter-quota-federation/",
        CreateQuotaETPFederation.as_view(),
        name="ajouter_quota_federation",
    ),
    path(
        "modifier-quota-federation/<int:pk>/",
        UpdateQuotaETPFederation.as_view(),
        name="modifier_quota_federation",
    ),
    path(
        "syndicats-en-retard/", SyndicatsEnRetard.as_view(), name="syndicats_en_retard"
    ),
]
