from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.urls import reverse
from django.views.generic import CreateView, DeleteView, UpdateView

from decharges.decharge.forms import UtilisationTempsDechargeForm
from decharges.decharge.mixins import CheckConfigurationMixin, CheckTempsEditableMixin
from decharges.decharge.models import UtilisationTempsDecharge


class CreateUtilisationTempsDecharge(
    CheckConfigurationMixin, LoginRequiredMixin, CheckTempsEditableMixin, CreateView
):
    template_name = "decharge/utilisation_temps_decharge_form.html"
    form_class = UtilisationTempsDechargeForm

    def get_success_url(self):
        messages.success(self.request, "Bénéficiaire ajouté·e avec succès !")
        return reverse("decharge:index")

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs["syndicat"] = self.request.user
        form_kwargs["annee"] = self.params.annee_en_cours
        return form_kwargs


class UpdateUtilisationTempsDecharge(
    CheckConfigurationMixin, LoginRequiredMixin, CheckTempsEditableMixin, UpdateView
):
    template_name = "decharge/utilisation_temps_decharge_form.html"
    form_class = UtilisationTempsDechargeForm
    model = UtilisationTempsDecharge
    context_object_name = "utilisation_temps_decharge"

    def get_object(self, queryset=None):
        """vérification que l'utilisateur a bien les permissions pour éditer cet objet"""
        utilisation_temps_decharge = super().get_object(queryset=queryset)
        if (
            utilisation_temps_decharge.syndicat != self.request.user
            and not self.request.user.is_federation
        ):
            raise Http404()
        return utilisation_temps_decharge

    def get_success_url(self):
        messages.success(self.request, "Bénéficiaire mis·e à jour avec succès !")
        return reverse("decharge:index")

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs["syndicat"] = self.object.syndicat
        form_kwargs["annee"] = self.object.annee
        return form_kwargs


class SuppressionUtilisationTempsDecharge(
    CheckConfigurationMixin, LoginRequiredMixin, CheckTempsEditableMixin, DeleteView
):
    template_name = "decharge/suppression_utilisation_temps_decharge_form.html"
    model = UtilisationTempsDecharge
    context_object_name = "utilisation_temps_decharge"

    def get_object(self, queryset=None):
        """vérification que l'utilisateur a bien les permissions pour éditer cet objet"""
        utilisation_temps_decharge = super().get_object(queryset=queryset)
        if (
            utilisation_temps_decharge.syndicat != self.request.user
            and not self.request.user.is_federation
        ):
            raise Http404()
        return utilisation_temps_decharge

    def get_success_url(self):
        messages.success(self.request, "Bénéficiaire retiré·e avec succès !")
        return reverse("decharge:index")
