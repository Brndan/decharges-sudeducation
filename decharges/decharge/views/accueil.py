from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from decharges.decharge.mixins import CheckConfigurationMixin
from decharges.decharge.models import UtilisationTempsDecharge
from decharges.decharge.views.utils import calcul_repartition_temps


class PageAccueilSyndicatView(
    CheckConfigurationMixin, LoginRequiredMixin, TemplateView
):
    template_name = "decharge/page_accueil_syndicat.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        annee_en_cours = self.params.annee_en_cours
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
        ) = calcul_repartition_temps(annee_en_cours, self.federation, self.request.user)

        if self.request.user.is_federation and not self.params.decharges_editables:
            # Si on est en cours d'année, la fédé peut éditer les décharges des syndicats
            temps_utilises_par_syndicat = {}
            for temps_utilise in UtilisationTempsDecharge.objects.filter(
                annee=annee_en_cours,
                supprime_a__isnull=True,
            ).exclude(syndicat=self.federation):
                temps_utilises_par_syndicat[
                    temps_utilise.syndicat.username
                ] = temps_utilises_par_syndicat.get(
                    temps_utilise.syndicat.username, []
                ) + [
                    temps_utilise
                ]
            context["temps_utilises_par_syndicat"] = temps_utilises_par_syndicat

        context.update(
            {
                "temps_decharge_federation": temps_decharge_federation,
                "temps_restant": round(temps_restant, settings.PRECISION_ETP),
                "cts_consommes": cts_consommes,
                "temps_donnes": temps_donnes,
                "temps_utilises": temps_utilises,
                "temps_recus_par_la_federation": round(
                    temps_recus_par_la_federation, settings.PRECISION_ETP
                ),
                "temps_recus_par_des_syndicats": round(
                    temps_recus_par_des_syndicats, settings.PRECISION_ETP
                ),
                "temps_utilises_total": round(
                    temps_utilises_total, settings.PRECISION_ETP
                ),
                "temps_donnes_total": round(temps_donnes_total, settings.PRECISION_ETP),
                "decharges_editables": self.params.decharges_editables,
            }
        )

        return context
