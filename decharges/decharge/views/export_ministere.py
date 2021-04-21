from datetime import date

import pandas
from django.http import HttpResponse
from django.views.generic.base import View

from decharges.decharge.mixins import CheckConfigurationMixin, FederationRequiredMixin
from decharges.decharge.models import UtilisationTempsDecharge
from decharges.decharge.views.utils import aggregation_par_beneficiaire


class ExportMinistere(CheckConfigurationMixin, FederationRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        annee = self.params.annee_en_cours

        columns = aggregation_par_beneficiaire(
            UtilisationTempsDecharge.objects.filter(
                annee=annee, supprime_a__isnull=True
            )
        )

        data_frame = pandas.DataFrame(
            {
                "Code organisation": pandas.Series(
                    columns["code_organisations"], dtype="string"
                ),
                "M. Mme": pandas.Series(columns["m_mmes"], dtype="string"),
                "Prénom": pandas.Series(columns["prenoms"], dtype="string"),
                "Nom": pandas.Series(columns["noms"], dtype="string"),
                "Heures décharges": pandas.Series(
                    columns["heures_decharges"], dtype="int"
                ),
                "Minutes décharges": pandas.Series(
                    columns["minutes_decharges"], dtype="int"
                ),
                "Heures ORS": pandas.Series(columns["heures_ors"], dtype="int"),
                "Minutes ORS": pandas.Series(columns["minutes_ors"], dtype="int"),
                "AIRE": pandas.Series(columns["aires"], dtype="int"),
                "Corps": pandas.Series(columns["corps"], dtype="string"),
                "RNE": pandas.Series(columns["rnes"], dtype="string"),
            }
        )
        response = HttpResponse("", content_type="application/force-download")
        data_frame.to_excel(response, engine="odf", index=False)
        today = date.today()
        response["Content-Disposition"] = (
            "attachment; filename=SUD éducation - déclaration initiale "
            f"{annee}-{annee+1} - {today}.ods"
        )
        return response
