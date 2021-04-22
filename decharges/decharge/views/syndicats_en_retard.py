from django.views.generic import TemplateView

from decharges.decharge.mixins import CheckConfigurationMixin, FederationRequiredMixin
from decharges.decharge.models import (
    TempsDeDecharge,
    UtilisationCreditDeTempsSyndicalPonctuel,
    UtilisationTempsDecharge,
)
from decharges.user_manager.models import Syndicat


class SyndicatsEnRetard(CheckConfigurationMixin, FederationRequiredMixin, TemplateView):
    template_name = "decharge/syndicats_en_retard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["annee"] = self.params.annee_en_cours
        temps_de_decharge_mutualise = TempsDeDecharge.objects.filter(
            annee=self.params.annee_en_cours
        )
        utilisation_temps_decharge = UtilisationTempsDecharge.objects.filter(
            annee=self.params.annee_en_cours,
        )
        utilisation_cts = UtilisationCreditDeTempsSyndicalPonctuel.objects.filter(
            annee=self.params.annee_en_cours,
        )

        context["syndicats_a_relancer"] = (
            Syndicat.objects.exclude(pk=self.federation.pk)
            .exclude(temps_de_decharges_donnes__in=temps_de_decharge_mutualise)
            .exclude(
                utilisation_temps_de_decharges_par_annee__in=utilisation_temps_decharge
            )
            .exclude(utilisation_cts_ponctuels_par_annee__in=utilisation_cts)
            .order_by("username")
        )
        return context
