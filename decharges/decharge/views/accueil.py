from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from decharges.decharge.mixins import CheckConfigurationMixin


class PageAccueilSyndicatView(
    CheckConfigurationMixin, LoginRequiredMixin, TemplateView
):
    template_name = "decharge/page_accueil_syndicat.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        annee_en_cours = self.params.annee_en_cours
        temps_utilises = (
            self.request.user.utilisation_temps_de_decharges_par_annee.filter(
                annee=annee_en_cours,
                supprime_a__isnull=True,
            )
        )
        temps_utilises_total = sum(
            temps_consomme.etp_utilises for temps_consomme in temps_utilises
        )
        temps_donnes = self.request.user.temps_de_decharges_donnes.filter(
            annee=annee_en_cours,
        )
        temps_donnes_total = sum(
            temps_donne.temps_de_decharge_etp for temps_donne in temps_donnes
        )

        temps_decharge_federation = None
        temps_recus_par_la_federation = 0
        temps_recus_par_des_syndicats = 0
        for temps_recu in self.request.user.temps_de_decharges_par_annee.filter(
            annee=annee_en_cours,
        ):
            if (
                temps_recu.syndicat_donateur is not None
                and temps_recu.syndicat_donateur != self.federation
            ):
                temps_recus_par_des_syndicats += temps_recu.temps_de_decharge_etp
            else:
                temps_recus_par_la_federation += temps_recu.temps_de_decharge_etp
                temps_decharge_federation = temps_recu

        temps_restant = (
            temps_recus_par_la_federation
            + temps_recus_par_des_syndicats
            - temps_utilises_total
            - temps_donnes_total
        )
        cts_consommes = self.request.user.utilisation_cts_ponctuels_par_annee.filter(
            annee=annee_en_cours
        ).first()
        if cts_consommes:
            temps_restant -= cts_consommes.etp_utilises

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
            }
        )

        return context
