from django.urls import path

from decharges.decharge.views import ImportTempsSyndicats, PageAccueilSyndicatView

app_name = "decharge"

urlpatterns = [
    path("", PageAccueilSyndicatView.as_view(), name="index"),
    path("import/", ImportTempsSyndicats.as_view(), name="import_temps"),
]
