from datetime import date

import pandas
from django.http import HttpResponse
from django.views.generic.base import View

from decharges.decharge.mixins import CheckConfigurationMixin, FederationRequiredMixin
from decharges.decharge.models import CIVILITE_AFFICHEE, UtilisationTempsDecharge


class ExportMinistere(CheckConfigurationMixin, FederationRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        annee = self.params.annee_en_cours

        # Pour commencer, on aggrège par bénéficiaire
        beneficiaires = {}

        for utilisation_temps_decharge in UtilisationTempsDecharge.objects.filter(
            annee=annee, supprime_a__isnull=True
        ):
            key = (
                f"{utilisation_temps_decharge.prenom}%"
                f"{utilisation_temps_decharge.nom}%"
                f"{utilisation_temps_decharge.code_etablissement_rne}"
            )
            beneficiaires[key] = beneficiaires.get(key, []) + [
                utilisation_temps_decharge
            ]

        code_organisations = []
        m_mmes = []
        prenoms = []
        noms = []
        heures_decharges = []
        minutes_decharges = []
        heures_ors = []
        minutes_ors = []
        aires = []
        corps = []
        rnes = []
        for temps_de_decharges_par_beneficiare in beneficiaires.values():
            total_heures_decharges = 0
            for (
                temps_de_decharge
            ) in temps_de_decharges_par_beneficiare:  # type: UtilisationTempsDecharge
                total_heures_decharges += temps_de_decharge.heures_de_decharges
            code_organisations.append("S01")  # le `Code organisation` est fixe
            m_mmes.append(
                CIVILITE_AFFICHEE[temps_de_decharges_par_beneficiare[0].civilite]
            )
            prenoms.append(temps_de_decharges_par_beneficiare[0].prenom)
            noms.append(temps_de_decharges_par_beneficiare[0].nom)
            heures_decharges.append(int(total_heures_decharges))
            minutes_decharges.append(
                int((total_heures_decharges - int(total_heures_decharges)) * 60)
            )
            heures_ors.append(
                temps_de_decharges_par_beneficiare[0].heures_d_obligation_de_service
            )
            minutes_ors.append(0)  # aujourd'hui les `Heures ORS` sont entiers
            aires.append(2)  # le `AIRE` est fixe
            corps.append(temps_de_decharges_par_beneficiare[0].corps.code_corps)
            rnes.append(temps_de_decharges_par_beneficiare[0].code_etablissement_rne)

        data_frame = pandas.DataFrame(
            {
                "Code organisation": pandas.Series(code_organisations, dtype="string"),
                "M. Mme": pandas.Series(m_mmes, dtype="string"),
                "Prénom": pandas.Series(prenoms, dtype="string"),
                "Nom": pandas.Series(noms, dtype="string"),
                "Heures décharges": pandas.Series(heures_decharges, dtype="int"),
                "Minutes décharges": pandas.Series(minutes_decharges, dtype="int"),
                "Heures ORS": pandas.Series(heures_ors, dtype="int"),
                "Minutes ORS": pandas.Series(minutes_ors, dtype="int"),
                "AIRE": pandas.Series(aires, dtype="int"),
                "Corps": pandas.Series(corps, dtype="string"),
                "RNE": pandas.Series(rnes, dtype="string"),
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
