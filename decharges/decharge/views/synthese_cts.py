from django.views.generic import TemplateView

from decharges.decharge.mixins import CheckConfigurationMixin, FederationRequiredMixin
from decharges.decharge.models import UtilisationCreditDeTempsSyndicalPonctuel
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
            context["cts_par_academie"][academie.nom] = 0
            for cts in UtilisationCreditDeTempsSyndicalPonctuel.objects.filter(
                annee=self.params.annee_en_cours,
                syndicat__in=academie.syndicats_membres.all(),
            ):
                context["cts_par_academie"][academie.nom] += cts.etp_utilises

        # TODO
        context["total_etp_non_consommes"] = 1000

        return context
