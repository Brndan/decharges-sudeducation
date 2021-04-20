from django import forms
from django.conf import settings

from decharges.decharge.models import UtilisationTempsDecharge


class UtilisationTempsDechargeForm(forms.ModelForm):
    heures_d_obligation_de_service = forms.ChoiceField(
        label="Heures d'obligations de service", choices=settings.CHOIX_ORS
    )

    def __init__(self, *args, **kwargs):
        self.syndicat = kwargs.pop("syndicat")
        self.annee = kwargs.pop("annee")
        super().__init__(*args, **kwargs)
        self.fields["prenom"].label = "Prénom (commençant par une majuscule)"
        self.fields["prenom"].widget.attrs["placeholder"] = "ex : Michelle"
        self.fields["nom"].label = "Nom (en MAJUSCULE)"
        self.fields["nom"].widget.attrs["placeholder"] = "ex : MARTIN"
        self.fields["heures_de_decharges"].label = "Heures de décharge utilisées"
        self.fields[
            "code_etablissement_rne"
        ].help_text = (
            "Le code établissement d'affectation (7 chiffres et une lettre majuscule)"
        )
        self.fields["code_etablissement_rne"].widget.attrs[
            "placeholder"
        ] = "ex: 1234567A"

    def save(self, commit=True):
        self.instance.syndicat = self.syndicat
        self.instance.annee = self.annee
        return super().save(commit=commit)

    class Meta:
        model = UtilisationTempsDecharge
        fields = [
            "civilite",
            "prenom",
            "nom",
            "heures_de_decharges",
            "heures_d_obligation_de_service",
            "corps",
            "code_etablissement_rne",
        ]
