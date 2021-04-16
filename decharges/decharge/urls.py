from django.urls import path

from decharges.decharge.views import PageAccueilSyndicatView

namespace = "decharge"
urlpatterns = [path("", PageAccueilSyndicatView.as_view())]
