import decimal

from django import forms
from django.core.validators import MinValueValidator
from django.db.models import QuerySet

from decharges.decharge.models import TempsDeDecharge
from decharges.decharge.views.utils import calcul_repartition_temps
from decharges.user_manager.models import Syndicat


class TempsDeDechargeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.syndicat = kwargs.pop("syndicat")
        self.annee = kwargs.pop("annee")
        self.federation = kwargs.pop("federation")
        super().__init__(*args, **kwargs)
        self.fields["syndicat_beneficiaire"].queryset = QuerySet()
        self.fields["temps_de_decharge_etp"].min_value = decimal.Decimal(0)
        self.fields["temps_de_decharge_etp"].validators.append(
            MinValueValidator(decimal.Decimal(0))
        )
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

    def _populate_instance(self):
        self.instance.syndicat_donateur = self.syndicat
        self.instance.annee = self.annee

    def validate_unique(self):
        exclude = self._get_validation_exclusions()
        exclude = set(exclude) - {
            "id",
            "annee",
            "syndicat_donateur",
            "syndicat_beneficiaire",
        }
        try:
            self.instance.validate_unique(exclude=exclude)
        except forms.ValidationError:
            self._update_errors(
                forms.ValidationError(
                    "Un partage de temps pour ce syndicat existe déjà, "
                    "veuillez plutôt le mettre à jour"
                )
            )

    def full_clean(self):
        super().full_clean()
        (_, _, _, _, _, _, temps_restant, _, _,) = calcul_repartition_temps(
            self.annee,
            self.federation,
            self.syndicat,
            excluded_temps_de_decharge_donne_pk=self.instance.pk,
        )

        if temps_restant - self.instance.temps_de_decharge_etp < 0 and hasattr(
            self, "cleaned_data"
        ):
            self.add_error(
                None,
                f"Vous dépassez le quota du syndicat, il reste {temps_restant:.3f} ETP "
                "attribuable et vous essayez d'ajouter "
                f"{self.instance.temps_de_decharge_etp:.3f} ETP",
            )

    def clean(self):
        self._populate_instance()
        return super().clean()

    class Meta:
        model = TempsDeDecharge
        fields = [
            "syndicat_beneficiaire",
            "temps_de_decharge_etp",
        ]


class QuotaETPFederationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.federation = kwargs.pop("federation")
        self.annee = kwargs.pop("annee")
        super().__init__(*args, **kwargs)
        self.fields["temps_de_decharge_etp"].min_value = decimal.Decimal(0)
        self.fields["temps_de_decharge_etp"].validators.append(
            MinValueValidator(decimal.Decimal(0))
        )

    def save(self, commit=True):
        self.instance.syndicat_beneficiaire = self.federation
        self.instance.annee = self.annee
        return super().save(commit=commit)

    class Meta:
        model = TempsDeDecharge
        fields = [
            "temps_de_decharge_etp",
        ]
