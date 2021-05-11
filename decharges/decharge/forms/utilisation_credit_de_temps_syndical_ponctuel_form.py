from django import forms

from decharges.decharge.models import UtilisationCreditDeTempsSyndicalPonctuel
from decharges.decharge.views.utils import calcul_repartition_temps


class UtilisationCreditDeTempsSyndicalPonctuelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.syndicat = kwargs.pop("syndicat")
        self.annee = kwargs.pop("annee")
        self.federation = kwargs.pop("federation")
        super().__init__(*args, **kwargs)

    def full_clean(self):
        super().full_clean()
        (_, _, _, _, _, _, temps_restant, _, _,) = calcul_repartition_temps(
            self.annee,
            self.federation,
            self.syndicat,
            excluded_utilisation_cts_ponctuel_pk=self.instance.pk,
        )

        if temps_restant - self.instance.etp_utilises < 0 and hasattr(
            self, "cleaned_data"
        ):
            self.add_error(
                None,
                f"Vous dépassez le quota du syndicat, il reste {temps_restant:.3f} ETP "
                f"attribuable et vous essayez d'ajouter {self.instance.etp_utilises:.3f} ETP",
            )

    def save(self, commit=True):
        self.instance.syndicat = self.syndicat
        self.instance.annee = self.annee
        return super().save(commit=commit)

    class Meta:
        model = UtilisationCreditDeTempsSyndicalPonctuel
        fields = [
            "demi_journees_de_decharges",
        ]
