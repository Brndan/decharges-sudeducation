from django import forms
from django.db.models import QuerySet

from decharges.decharge.models import TempsDeDecharge
from decharges.user_manager.models import Syndicat


class TempsDeDechargeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.syndicat = kwargs.pop("syndicat")
        self.annee = kwargs.pop("annee")
        super().__init__(*args, **kwargs)
        self.fields["syndicat_beneficiaire"].queryset = QuerySet()
        if self.syndicat.academie:
            self.fields[
                "syndicat_beneficiaire"
            ].queryset = self.syndicat.academie.syndicats_membres.exclude(
                pk=self.syndicat.pk
            ).order_by(
                "username"
            )
        if self.syndicat.is_federation:
            self.fields[
                "syndicat_beneficiaire"
            ].queryset = Syndicat.objects.all().order_by("username")

    def save(self, commit=True):
        self.instance.syndicat_donateur = self.syndicat
        self.instance.annee = self.annee
        return super().save(commit=commit)

    class Meta:
        model = TempsDeDecharge
        fields = [
            "syndicat_beneficiaire",
            "temps_de_decharge_etp",
        ]
