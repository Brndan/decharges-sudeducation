from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.urls import reverse
from django.views.generic import CreateView, UpdateView

from decharges.decharge.forms import UtilisationCreditDeTempsSyndicalPonctuelForm
from decharges.decharge.mixins import CheckConfigurationMixin
from decharges.decharge.models import UtilisationCreditDeTempsSyndicalPonctuel


class CTSCreate(CheckConfigurationMixin, LoginRequiredMixin, CreateView):
    template_name = "decharge/cts_form.html"
    form_class = UtilisationCreditDeTempsSyndicalPonctuelForm

    def get_success_url(self):
        messages.success(self.request, "CTS enregistré avec succès !")
        return reverse("decharge:index")

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs["syndicat"] = self.request.user
        form_kwargs["annee"] = self.params.annee_en_cours
        return form_kwargs


class CTSUpdate(CheckConfigurationMixin, LoginRequiredMixin, UpdateView):
    template_name = "decharge/cts_form.html"
    form_class = UtilisationCreditDeTempsSyndicalPonctuelForm
    model = UtilisationCreditDeTempsSyndicalPonctuel
    context_object_name = "cts"

    def get_object(self, queryset=None):
        """vérification que l'utilisateur a bien les permissions pour éditer cet objet"""
        cts = super().get_object(queryset=queryset)
        if cts.syndicat != self.request.user and not self.request.user.is_federation:
            raise Http404()
        return cts

    def get_success_url(self):
        messages.success(self.request, "CTS enregistré avec succès !")
        return reverse("decharge:index")

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs["syndicat"] = self.object.syndicat
        form_kwargs["annee"] = self.object.annee
        return form_kwargs
