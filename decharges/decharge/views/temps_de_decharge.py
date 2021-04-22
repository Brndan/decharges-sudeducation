from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.urls import reverse
from django.views.generic import CreateView, DeleteView, UpdateView

from decharges.decharge.forms import QuotaETPFederationForm, TempsDeDechargeForm
from decharges.decharge.mixins import CheckConfigurationMixin, FederationRequiredMixin
from decharges.decharge.models import TempsDeDecharge


class CreateQuotaETPFederation(
    CheckConfigurationMixin, FederationRequiredMixin, CreateView
):
    template_name = "decharge/quota_etp_federation_form.html"
    form_class = QuotaETPFederationForm

    def get_success_url(self):
        messages.success(self.request, "Quota créé avec succès !")
        return reverse("decharge:index")

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs["federation"] = self.request.user
        form_kwargs["annee"] = self.params.annee_en_cours
        return form_kwargs


class UpdateQuotaETPFederation(
    CheckConfigurationMixin, FederationRequiredMixin, UpdateView
):
    template_name = "decharge/quota_etp_federation_form.html"
    form_class = QuotaETPFederationForm
    model = TempsDeDecharge
    context_object_name = "temps_de_decharge"

    def get_success_url(self):
        messages.success(self.request, "Quota mis à jour avec succès !")
        return reverse("decharge:index")

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs["federation"] = self.request.user
        form_kwargs["annee"] = self.object.annee
        return form_kwargs


class CreateTempsDeDecharge(CheckConfigurationMixin, LoginRequiredMixin, CreateView):
    template_name = "decharge/temps_de_decharge_form.html"
    form_class = TempsDeDechargeForm

    def get_success_url(self):
        messages.success(self.request, "Partage de temps bien pris en compte !")
        return reverse("decharge:index")

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs["syndicat"] = self.request.user
        form_kwargs["annee"] = self.params.annee_en_cours
        return form_kwargs


class UpdateTempsDeDecharge(CheckConfigurationMixin, LoginRequiredMixin, UpdateView):
    template_name = "decharge/temps_de_decharge_form.html"
    form_class = TempsDeDechargeForm
    model = TempsDeDecharge
    context_object_name = "temps_de_decharge"

    def get_object(self, queryset=None):
        """vérification que l'utilisateur a bien les permissions pour éditer cet objet"""
        temps_de_decharge = super().get_object(queryset=queryset)
        if (
            temps_de_decharge.syndicat_donateur != self.request.user
            and not self.request.user.is_federation
        ):
            raise Http404()
        return temps_de_decharge

    def get_success_url(self):
        messages.success(self.request, "Partage de temps bien pris en compte !")
        return reverse("decharge:index")

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs["syndicat"] = self.object.syndicat_donateur
        form_kwargs["annee"] = self.object.annee
        return form_kwargs


class SuppressionTempsDeDecharge(
    CheckConfigurationMixin, LoginRequiredMixin, DeleteView
):
    template_name = "decharge/suppression_temps_de_decharge_form.html"
    model = TempsDeDecharge
    context_object_name = "temps_de_decharge"

    def get_object(self, queryset=None):
        """vérification que l'utilisateur a bien les permissions pour éditer cet objet"""
        temps_de_decharge = super().get_object(queryset=queryset)
        if (
            temps_de_decharge.syndicat_donateur != self.request.user
            and not self.request.user.is_federation
        ):
            raise Http404()
        return temps_de_decharge

    def get_success_url(self):
        messages.success(self.request, "Partage de temps supprimé avec succès !")
        return reverse("decharge:index")
