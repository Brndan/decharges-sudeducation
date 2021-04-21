from django.urls import path

from decharges.decharge.views import (
    CreateUtilisationTempsDecharge,
    CTSCreate,
    CTSUpdate,
    ExportMinistere,
    HistoriquePage,
    ImportTempsSyndicats,
    PageAccueilSyndicatView,
    SuppressionUtilisationTempsDecharge,
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
    path("ajouter-cts/", CTSCreate.as_view(), name="ajouter_cts"),
    path("modifier-cts/<int:pk>/", CTSUpdate.as_view(), name="modifier_cts"),
]
