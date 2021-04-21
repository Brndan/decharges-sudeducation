from django import forms

from decharges.decharge.models import UtilisationCreditDeTempsSyndicalPonctuel


class UtilisationCreditDeTempsSyndicalPonctuelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.syndicat = kwargs.pop("syndicat")
        self.annee = kwargs.pop("annee")
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        self.instance.syndicat = self.syndicat
        self.instance.annee = self.annee
        return super().save(commit=commit)

    class Meta:
        model = UtilisationCreditDeTempsSyndicalPonctuel
        fields = [
            "demi_journees_de_decharges",
        ]
