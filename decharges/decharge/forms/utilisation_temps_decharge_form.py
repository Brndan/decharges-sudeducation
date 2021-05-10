import os

from django import forms
from django.conf import settings

from decharges.decharge.models import UtilisationTempsDecharge
from decharges.user_manager.models import Syndicat


class UtilisationTempsDechargeForm(forms.ModelForm):
    heures_d_obligation_de_service = forms.ChoiceField(
        label="Heures d'obligations de service", choices=settings.CHOIX_ORS
    )
    heures_de_decharges = forms.IntegerField(
        label="Heures de décharge utilisées", min_value=0, initial=0
    )
    minutes_de_decharges = forms.IntegerField(
        label="Minutes de décharge utilisées",
        min_value=0,
        max_value=59,
        required=False,
        initial=0,
    )

    def __init__(self, *args, **kwargs):
        self.syndicat = kwargs.pop("syndicat")
        self.annee = kwargs.pop("annee")
        self.decharges_editables = kwargs.pop("decharges_editables")
        self.corps_annexe = kwargs.pop("corps_annexe")
        super().__init__(*args, **kwargs)
        self.fields["prenom"].label = "Prénom"
        self.fields["prenom"].help_text = (
            "- Doit commencer par une Majuscule <br>"
            "- Ne doit pas commencer ou finir par un espace <br>"
            "- Ne doit pas contenir 2 espaces consécutifs <br>"
            "- Ne doit pas contenir de caractères spéciaux"
        )
        self.fields["prenom"].widget.attrs["placeholder"] = "ex : Michelle"
        self.fields["nom"].label = "Nom"
        self.fields["nom"].widget.attrs["placeholder"] = "ex : MARTIN"
        self.fields["nom"].help_text = (
            "- Doit être en MAJUSCULE <br>"
            "- Ne doit pas commencer ou finir par un espace <br>"
            "- Ne doit pas contenir 2 espaces consécutifs <br>"
            "- Ne doit pas contenir de caractères spéciaux"
        )
        self.fields[
            "code_etablissement_rne"
        ].help_text = (
            "Le code établissement d'affectation (7 chiffres et une lettre majuscule)"
        )
        self.fields["code_etablissement_rne"].widget.attrs[
            "placeholder"
        ] = "ex: 1234567A"

        if not self.decharges_editables:
            # la fédération peut choisir le syndicat qui utilise la décharge dans le formulaire
            self.fields["syndicat"] = forms.ModelChoiceField(
                label="Syndicat qui utilise ce temps",
                queryset=Syndicat.objects.all().order_by("username"),
                initial=self.syndicat,
            )
            if self.instance.pk:
                self.fields["prenom"].widget.attrs["readonly"] = True
                self.fields["nom"].widget.attrs["readonly"] = True
                self.fields["code_etablissement_rne"].widget.attrs["readonly"] = True
            self.fields["commentaire_de_mise_a_jour"] = forms.CharField(
                label="Pourquoi cette mise à jour en cours d'année ?",
                widget=forms.Textarea(),
                initial=self.instance.commentaire_de_mise_a_jour,
            )

        if self.corps_annexe:
            self.fields["corps"].help_text = (
                f"Voir <a href='{self.corps_annexe.url}' target='_blank'>"
                f"{os.path.basename(self.corps_annexe.name)} "
                f"<span class='fa fa-external-link-alt fa-xs'></span>"
                f"</a> "
            )

        self.fields["heures_de_decharges"].initial = int(
            self.instance.heures_de_decharges
        )
        self.fields["minutes_de_decharges"].initial = round(
            (
                self.instance.heures_de_decharges
                - self.fields["heures_de_decharges"].initial
            )
            * 60
        )

    def save(self, commit=True):
        if self.decharges_editables:
            self.instance.syndicat = self.syndicat
        else:
            # la fédération peut choisir le syndicat qui utilise la décharge dans le formulaire
            self.instance.syndicat = self.cleaned_data["syndicat"]
            self.instance.commentaire_de_mise_a_jour = self.cleaned_data[
                "commentaire_de_mise_a_jour"
            ]
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
