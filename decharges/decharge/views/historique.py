from django.conf import settings
from django.views.generic import TemplateView

from decharges.decharge.mixins import CheckConfigurationMixin, FederationRequiredMixin
from decharges.decharge.models import UtilisationTempsDecharge
from decharges.decharge.views.utils import aggregation_par_beneficiaire


class HistoriquePage(CheckConfigurationMixin, FederationRequiredMixin, TemplateView):
    template_name = "decharge/historique.html"

    def get_context_data(self, **kwargs):
        annee_max = int(self.request.GET.get("annee", self.params.annee_en_cours))
        context = super().get_context_data(**kwargs)

        annee_min = (
            annee_max
            - settings.MAX_ANNEES_CONSECUTIVES
            * settings.NB_ANNEES_POUR_REINITIALISER_LES_COMPTEURS
        )
        columns = aggregation_par_beneficiaire(
            UtilisationTempsDecharge.objects.filter(
                supprime_a__isnull=True, annee__gte=annee_min, annee__lte=annee_max
            ).order_by("nom")
        )
        row_iterator = list(range(len(columns["noms"])))
        beneficiaires_approchant_les_limites = {}
        for row_number in row_iterator:
            etp_consecutifs = 0
            annees_consecutives = 0
            annees_consecutives_sans_etps = 0
            for etp in columns["etps_par_annee"][row_number].values():
                if etp == 0:
                    annees_consecutives_sans_etps += 1
                    if (
                        annees_consecutives_sans_etps
                        == settings.NB_ANNEES_POUR_REINITIALISER_LES_COMPTEURS
                    ):
                        break
                else:
                    annees_consecutives += 1
                    etp_consecutifs += etp

            nom = columns["noms"][row_number]
            prenom = columns["prenoms"][row_number]
            rne = columns["rnes"][row_number]
            identifiant = f"{prenom} {nom} ({rne})"
            if (
                annees_consecutives >= settings.ALERT_ANNEES_CONSECUTIVES
                or etp_consecutifs >= settings.ALERT_ETP_CONSECUTIFS
            ):
                beneficiaires_approchant_les_limites[identifiant] = {}
            if annees_consecutives >= settings.ALERT_ANNEES_CONSECUTIVES:
                beneficiaires_approchant_les_limites[identifiant][
                    "annees_consecutives"
                ] = annees_consecutives
            if etp_consecutifs >= settings.ALERT_ETP_CONSECUTIFS:
                beneficiaires_approchant_les_limites[identifiant][
                    "etp_consecutifs"
                ] = etp_consecutifs

        context["columns"] = columns
        context["row_iterator"] = row_iterator
        context["annee_en_cours"] = annee_max
        context[
            "beneficiaires_approchant_les_limites"
        ] = beneficiaires_approchant_les_limites

        return context