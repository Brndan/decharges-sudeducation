from django.contrib import messages
from django.db.models import Q
from django.urls import reverse
from django.views.generic import FormView

from decharges.decharge.forms.import_temps_syndicats_form import (
    ImportTempsSyndicatsForm,
)
from decharges.decharge.mixins import CheckConfigurationMixin, FederationRequiredMixin
from decharges.decharge.models import TempsDeDecharge


class ImportTempsSyndicats(CheckConfigurationMixin, FederationRequiredMixin, FormView):
    template_name = "decharge/import_temps_syndicats.html"
    form_class = ImportTempsSyndicatsForm

    def get_success_url(self):
        return reverse("decharge:index")

    def form_valid(self, form):
        federation = self.request.user
        updated = 0
        created = 0
        for syndicat, etp in form.cleaned_data["temps_de_decharge"]:
            temps_de_decharge_existant = TempsDeDecharge.objects.filter(
                Q(syndicat_donateur__isnull=True) | Q(syndicat_donateur=federation),
                annee=form.cleaned_data["annee"],
                syndicat_beneficiaire=syndicat,
            )
            if temps_de_decharge_existant:
                temps_de_decharge_existant.update(temps_de_decharge_etp=etp)
                updated += 1
            else:
                TempsDeDecharge.objects.create(
                    syndicat_donateur=federation,
                    annee=form.cleaned_data["annee"],
                    syndicat_beneficiaire=syndicat,
                )
                created += 1

        message = "Import terminé avec succès."
        if created > 0:
            message += f" {created} temps créés."
        if updated > 0:
            message += f" {updated} temps mis à jour."
        messages.success(self.request, message)

        return super().form_valid(form)
