from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from decharges.parametre.models import ParametresDApplication
from decharges.user_manager.models import Syndicat


class PageAccueilSyndicatView(LoginRequiredMixin, TemplateView):
    template_name = "decharge/page_accueil_syndicat.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        params = ParametresDApplication.objects.first()
        federation = Syndicat.objects.filter(is_superuser=True).first()
        annee_en_cours = params.annee_en_cours
        temps_de_decharges_recus = (
            self.request.user.temps_de_decharges_par_annee.filter(
                annee=annee_en_cours,
            )
        )
        context[
            "temps_de_decharges_utilises"
        ] = self.request.user.utilisation_temps_de_decharges_par_annee.filter(
            annee=annee_en_cours,
            supprime_a__isnull=True,
        )
        context["temps_de_decharges_utilises_total"] = sum(
            temps_consomme.etp_utilises
            for temps_consomme in context["temps_de_decharges_utilises"]
        )
        context[
            "temps_de_decharge_donnes"
        ] = self.request.user.temps_de_decharges_donnes.filter(
            annee=annee_en_cours,
        )
        context["temps_de_decharge_donnes_total"] = sum(
            temps_donne.temps_de_decharge_etp
            for temps_donne in context["temps_de_decharge_donnes"]
        )
        context[
            "cts_consommes"
        ] = self.request.user.utilisation_cts_ponctuels_par_annee.filter(
            annee=annee_en_cours
        ).first()

        context["temps_de_decharge_recus_par_la_federation"] = 0
        context["temps_de_decharge_recus_par_des_syndicats"] = 0
        for temps_recu in temps_de_decharges_recus:
            if (
                temps_recu.syndicat_donateur is not None
                and temps_recu.syndicat_donateur != federation
            ):  # pragma: no cover
                context[
                    "temps_de_decharge_recus_par_des_syndicats"
                ] += temps_recu.temps_de_decharge_etp  # pragma: no cover
            else:  # pragma: no cover
                context[
                    "temps_de_decharge_recus_par_la_federation"
                ] += temps_recu.temps_de_decharge_etp  # pragma: no cover

        context["temps_restant"] = (
            context["temps_de_decharge_recus_par_la_federation"]
            + context["temps_de_decharge_recus_par_des_syndicats"]
            - context["temps_de_decharges_utilises_total"]
            - context["temps_de_decharge_donnes_total"]
        )
        if context["cts_consommes"]:  # pragma: no cover
            context["temps_restant"] -= context[
                "cts_consommes"
            ].etp_utilises  # pragma: no cover

        return context
