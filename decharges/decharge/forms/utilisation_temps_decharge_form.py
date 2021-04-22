from django import forms
from django.conf import settings

from decharges.decharge.models import UtilisationTempsDecharge


class UtilisationTempsDechargeForm(forms.ModelForm):
    heures_d_obligation_de_service = forms.ChoiceField(
        label="Heures d'obligations de service", choices=settings.CHOIX_ORS
    )
    heures_de_decharges = forms.IntegerField(
        label="Heures de décharge utilisées", min_value=0, initial=0
    )
    minutes_de_decharges = forms.IntegerField(
        label="Minutes de décharge utilisées", min_value=0, required=False, initial=0
    )

    def __init__(self, *args, **kwargs):
        self.syndicat = kwargs.pop("syndicat")
        self.annee = kwargs.pop("annee")
        super().__init__(*args, **kwargs)
        self.fields["prenom"].label = "Prénom (commençant par une majuscule)"
        self.fields["prenom"].widget.attrs["placeholder"] = "ex : Michelle"
        self.fields["nom"].label = "Nom (en MAJUSCULE)"
        self.fields["nom"].widget.attrs["placeholder"] = "ex : MARTIN"
        self.fields[
            "code_etablissement_rne"
        ].help_text = (
            "Le code établissement d'affectation (7 chiffres et une lettre majuscule)"
        )
        self.fields["code_etablissement_rne"].widget.attrs[
            "placeholder"
        ] = "ex: 1234567A"

        if self.instance:
            self.fields["heures_de_decharges"].initial = int(
                self.instance.heures_de_decharges
            )
            self.fields["minutes_de_decharges"].initial = int(
                (
                    self.instance.heures_de_decharges
                    - self.fields["heures_de_decharges"].initial
                )
                * 60
            )

    def save(self, commit=True):
        self.instance.syndicat = self.syndicat
        self.instance.annee = self.annee
        self.instance.heures_de_decharges = self.cleaned_data["heures_de_decharges"]
        if self.cleaned_data["minutes_de_decharges"]:
            self.instance.heures_de_decharges += (
                self.cleaned_data["minutes_de_decharges"] / 60
            )
        return super().save(commit=commit)

    class Meta:
        model = UtilisationTempsDecharge
        fields = [
            "civilite",
            "prenom",
            "nom",
            "heures_d_obligation_de_service",
            "corps",
            "code_etablissement_rne",
        ]
