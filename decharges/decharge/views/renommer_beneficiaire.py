from django.contrib import messages
from django.urls import reverse
from django.views.generic import FormView

from decharges.decharge.forms import RenommerBeneficiaireForm
from decharges.decharge.mixins import CheckConfigurationMixin, FederationRequiredMixin
from decharges.decharge.models import UtilisationTempsDecharge


class RenommerBeneficiaire(CheckConfigurationMixin, FederationRequiredMixin, FormView):
    template_name = "decharge/renommer_beneficiaire.html"
    form_class = RenommerBeneficiaireForm

    def get_success_url(self):
        return reverse("decharge:index")

    def form_valid(self, form):
        nb_updated = UtilisationTempsDecharge.objects.filter(
            prenom=form.cleaned_data["ancien_prenom"],
            nom=form.cleaned_data["ancien_nom"],
            code_etablissement_rne=form.cleaned_data["ancien_rne"],
        ).update(
            prenom=form.cleaned_data["nouveau_prenom"],
            nom=form.cleaned_data["nouveau_nom"],
            code_etablissement_rne=form.cleaned_data["nouveau_rne"],
        )
        if nb_updated > 0:
            messages.success(
                self.request,
                f"{nb_updated} déclarations de temps ont été mis à jour",
            )
        else:
            messages.info(
                self.request,
                "Aucun·e bénéficiaire ne correspondait à vos données, "
                "aucun changement n'a été effectué",
            )
        return super().form_valid(form)
