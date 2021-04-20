from django.urls import path

from decharges.decharge.views import (
    CreateUtilisationTempsDecharge,
    ExportMinistere,
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
        "ajout-beneficiare/",
        CreateUtilisationTempsDecharge.as_view(),
        name="ajouter_beneficiaire",
    ),
    path(
        "modifier-beneficiare/<int:pk>/",
        UpdateUtilisationTempsDecharge.as_view(),
        name="modifier_beneficiaire",
    ),
    path(
        "suppression-beneficiare/<int:pk>/",
        SuppressionUtilisationTempsDecharge.as_view(),
        name="supprimer_beneficiaire",
    ),
    path("export-ministere/", ExportMinistere.as_view(), name="export_ministere"),
]
