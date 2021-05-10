from django.views.generic import TemplateView

from decharges.decharge.mixins import CheckConfigurationMixin, FederationRequiredMixin
from decharges.decharge.models import (
    TempsDeDecharge,
    UtilisationCreditDeTempsSyndicalPonctuel,
    UtilisationTempsDecharge,
)
from decharges.decharge.views.utils import calcul_repartition_temps
from decharges.user_manager.models import Syndicat


class SyndicatsARelancer(
    CheckConfigurationMixin, FederationRequiredMixin, TemplateView
):
    template_name = "decharge/syndicats_a_relancer.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        annee_en_cours = self.params.annee_en_cours
        context["annee"] = annee_en_cours
        temps_de_decharge_mutualise = TempsDeDecharge.objects.filter(
            annee=annee_en_cours
        )
        utilisation_temps_decharge = UtilisationTempsDecharge.objects.filter(
            annee=annee_en_cours,
        )
        utilisation_cts = UtilisationCreditDeTempsSyndicalPonctuel.objects.filter(
            annee=annee_en_cours,
        )
        syndicats_depassant_leur_quota = []
        for syndicat in Syndicat.objects.all():
            (
                cts_consommes,
                temps_decharge_federation,
                temps_donnes,
                temps_donnes_total,
                temps_recus_par_des_syndicats,
                temps_recus_par_la_federation,
                temps_restant,
                temps_utilises,
                temps_utilises_total,
            ) = calcul_repartition_temps(annee_en_cours, self.federation, syndicat)
            if temps_restant < 0:
                syndicats_depassant_leur_quota.append((syndicat, abs(temps_restant)))

        context["syndicats_n_ayant_rien_rempli"] = (
            Syndicat.objects.exclude(pk=self.federation.pk).exclude(
                temps_de_decharges_donnes__in=temps_de_decharge_mutualise
            )
            .exclude(
                utilisation_temps_de_decharges_par_annee__in=utilisation_temps_decharge
            )
            .exclude(utilisation_cts_ponctuels_par_annee__in=utilisation_cts)
            .order_by("username")
        )
        context["syndicats_depassant_leur_quota"] = syndicats_depassant_leur_quota

        return context
