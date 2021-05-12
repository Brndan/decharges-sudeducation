from django import forms

from decharges.decharge.validators import (
    rne_validator,
    validate_first_name,
    validate_last_name,
)


class RenommerBeneficiaireForm(forms.Form):
    ancien_prenom = forms.Field(label="Ancien prénom")
    ancien_nom = forms.Field(label="Ancien nom")
    ancien_rne = forms.Field(label="Ancien RNE")
    nouveau_prenom = forms.Field(
        label="Nouveau prénom", validators=[validate_first_name]
    )
    nouveau_nom = forms.Field(label="Nouveau nom", validators=[validate_last_name])
    nouveau_rne = forms.Field(label="Nouveau RNE", validators=[rne_validator])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["ancien_prenom"].start_fieldset = "Anciennes données"
        self.fields["ancien_rne"].end_fieldset = True
        self.fields["nouveau_prenom"].start_fieldset = "Données mises à jour"
        self.fields["nouveau_rne"].end_fieldset = True

        self.fields["ancien_prenom"].widget.attrs["placeholder"] = "ex : Michelle"
        self.fields["ancien_nom"].widget.attrs["placeholder"] = "ex : MARTIN"
        self.fields["ancien_rne"].widget.attrs["placeholder"] = "ex : 1234567A"
        self.fields["nouveau_prenom"].widget.attrs["placeholder"] = "ex : Michelle"
        self.fields["nouveau_nom"].widget.attrs["placeholder"] = "ex : MARTIN"
        self.fields["nouveau_rne"].widget.attrs["placeholder"] = "ex : 1234567A"

        self.fields["nouveau_prenom"].help_text = (
            "- Doit commencer par une Majuscule <br>"
            "- Ne doit pas commencer ou finir par un espace <br>"
            "- Ne doit pas contenir 2 espaces consécutifs <br>"
            "- Ne doit pas contenir de caractères spéciaux"
        )
        self.fields["nouveau_nom"].help_text = (
            "- Doit être en MAJUSCULE <br>"
            "- Ne doit pas commencer ou finir par un espace <br>"
            "- Ne doit pas contenir 2 espaces consécutifs <br>"
            "- Ne doit pas contenir de caractères spéciaux"
        )
        self.fields[
            "nouveau_rne"
        ].help_text = (
            "Le code établissement d'affectation (7 chiffres et une lettre majuscule)"
        )
