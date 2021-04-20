from decimal import Decimal

import pandas
from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.utils import timezone

from decharges.user_manager.models import Syndicat


class ImportTempsSyndicatsForm(forms.Form):
    ods_file = forms.FileField(
        validators=[FileExtensionValidator(allowed_extensions=["ods"])],
        label="Feuille de calcul Libreoffice",
        widget=forms.ClearableFileInput(attrs={"accept": ".ods"}),
    )
    annee = forms.IntegerField(
        initial=timezone.now().year,
        help_text="L'année (en septembre) pour laquelle ces temps sont valables",
    )

    def clean_ods_file(self):
        document = pandas.read_excel(self.cleaned_data["ods_file"])
        self.cleaned_data["temps_de_decharge"] = []
        for line, row in document.iterrows():
            syndicat_name = row[0]
            syndicat = Syndicat.objects.filter(username=syndicat_name).first()
            if not syndicat:
                raise ValidationError(
                    f"Syndicat non trouvé en base : {syndicat_name} (ligne {line+2})"
                )
            try:
                syndicat_etp = Decimal(row[1])
            except Exception:
                raise ValidationError(f"ETP invalide : {row[1]} (ligne {line+2})")
            self.cleaned_data["temps_de_decharge"].append((syndicat, syndicat_etp))
