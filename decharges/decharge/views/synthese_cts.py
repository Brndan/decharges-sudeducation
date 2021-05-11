from django.views.generic import TemplateView

from decharges.decharge.mixins import CheckConfigurationMixin, FederationRequiredMixin
from decharges.decharge.models import (
    TempsDeDecharge,
    UtilisationCreditDeTempsSyndicalPonctuel,
    UtilisationTempsDecharge,
)
from decharges.user_manager.models import Academie


class SyntheseCTS(CheckConfigurationMixin, FederationRequiredMixin, TemplateView):
    template_name = "decharge/synthese_cts.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["annee_en_cours"] = self.params.annee_en_cours
        context["cts_par_academie"] = {}
        context[
            "cts_federation"
        ] = UtilisationCreditDeTempsSyndicalPonctuel.objects.filter(
            annee=self.params.annee_en_cours, syndicat=self.federation
        ).first()

        for academie in Academie.objects.all():
            context["cts_par_academie"][academie.nom] = {
                "etp": 0,
                "demi_journees": 0,
            }
            for cts in UtilisationCreditDeTempsSyndicalPonctuel.objects.filter(
                annee=self.params.annee_en_cours,
                syndicat__in=academie.syndicats_membres.all(),
            ):
                context["cts_par_academie"][academie.nom]["etp"] += cts.etp_utilises
                context["cts_par_academie"][academie.nom][
                    "demi_journees"
                ] += cts.demi_journees_de_decharges

        temps_de_decharge_federation = TempsDeDecharge.objects.filter(
            syndicat_beneficiaire=self.federation,
            annee=self.params.annee_en_cours,
            syndicat_donateur__isnull=True,
        ).first()
        total_etp_annee_en_cours = 0
        if temps_de_decharge_federation:
            total_etp_annee_en_cours = (
                temps_de_decharge_federation.temps_de_decharge_etp
            )

        total_etp_consommes = 0

        for cts_utilise in UtilisationCreditDeTempsSyndicalPonctuel.objects.filter(
            annee=self.params.annee_en_cours
        ):
            total_etp_consommes += cts_utilise.etp_utilises

        for temps_utilise in UtilisationTempsDecharge.objects.filter(
            annee=self.params.annee_en_cours,
            est_une_decharge_solidaires=False,
        ):
            total_etp_consommes += temps_utilise.etp_utilises

        context["total_etp_non_consommes"] = (
            total_etp_annee_en_cours - total_etp_consommes
        )

        return context
