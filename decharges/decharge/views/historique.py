from datetime import date

import pandas
from django.conf import settings
from django.http import HttpResponse
from django.views import View
from django.views.generic import TemplateView

from decharges.decharge.mixins import CheckConfigurationMixin, FederationRequiredMixin
from decharges.decharge.models import UtilisationTempsDecharge
from decharges.decharge.views.utils import aggregation_par_beneficiaire


def _compute_columns(get_params, annee_en_cours):
    annee_max = int(get_params.get("annee", annee_en_cours))
    annee_min = (
        annee_max
        - settings.MAX_ANNEES_CONSECUTIVES
        * settings.NB_ANNEES_POUR_REINITIALISER_LES_COMPTEURS
    )
    columns = aggregation_par_beneficiaire(
        UtilisationTempsDecharge.objects.filter(
            supprime_a__isnull=True, annee__gte=annee_min, annee__lte=annee_max
        )
        .prefetch_related("corps")
        .order_by("nom", "prenom")
    )
    etps_par_annee = {}
    for ligne_etp in columns["etps_par_annee"]:
        for annee, etp in ligne_etp.items():
            etps_par_annee[annee] = etps_par_annee.get(annee, []) + [etp]
    return annee_max, columns, etps_par_annee


def _extraire_approches_limites(columns):
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
            ] = float(round(etp_consecutifs, 3))

    return beneficiaires_approchant_les_limites, row_iterator


class HistoriquePage(CheckConfigurationMixin, FederationRequiredMixin, TemplateView):
    template_name = "decharge/historique.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        annee_max, columns, etps_par_annee = _compute_columns(
            self.request.GET, self.params.annee_en_cours
        )
        (
            beneficiaires_approchant_les_limites,
            row_iterator,
        ) = _extraire_approches_limites(columns)

        context["columns"] = columns
        context["row_iterator"] = row_iterator
        context["annee_en_cours"] = annee_max
        context[
            "beneficiaires_approchant_les_limites"
        ] = beneficiaires_approchant_les_limites

        return context


class HistoriqueTelecharger(CheckConfigurationMixin, FederationRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        annee_max, columns, etps_par_annee = _compute_columns(
            self.request.GET, self.params.annee_en_cours
        )
        columns_to_give_to_pandas = {
            "Civilité": pandas.Series(columns["m_mmes"], dtype="string"),
            "Prénom": pandas.Series(columns["prenoms"], dtype="string"),
            "Nom": pandas.Series(columns["noms"], dtype="string"),
            "RNE": pandas.Series(columns["rnes"], dtype="string"),
            "Corps": pandas.Series(columns["corps"], dtype="string"),
        }
        columns_to_give_to_pandas.update(
            {
                annee: pandas.Series(etps, dtype="float")
                for annee, etps in etps_par_annee.items()
            }
        )

        data_frame = pandas.DataFrame(columns_to_give_to_pandas)
        response = HttpResponse("", content_type="application/force-download")
        data_frame.to_excel(response, engine="odf", index=False)
        today = date.today()
        response["Content-Disposition"] = (
            "attachment; filename=Historique des décharges "
            f"{annee_max}-{annee_max + 1} - {today}.ods"
        )
        return response


class ApprocheDesReglesTelecharger(
    CheckConfigurationMixin, FederationRequiredMixin, View
):
    def get(self, request, *args, **kwargs):
        annee_max, columns, etps_par_annee = _compute_columns(
            self.request.GET, self.params.annee_en_cours
        )

        beneficiaires_approchant_les_limites, _ = _extraire_approches_limites(columns)

        data_frame = pandas.DataFrame(
            {
                "Identifiant": pandas.Series(
                    beneficiaires_approchant_les_limites.keys(), dtype="string"
                ),
                "Cumul d'ETP": pandas.Series(
                    [
                        limite.get("etp_consecutifs")
                        for limite in beneficiaires_approchant_les_limites.values()
                    ]
                ),
                "Années consecutives": pandas.Series(
                    [
                        limite.get("annees_consecutives")
                        for limite in beneficiaires_approchant_les_limites.values()
                    ]
                ),
            }
        )
        response = HttpResponse("", content_type="application/force-download")
        data_frame.to_excel(response, engine="odf", index=False)
        today = date.today()
        response["Content-Disposition"] = (
            "attachment; filename=Limites décharges "
            f"{annee_max}-{annee_max + 1} - {today}.ods"
        )
        return response
