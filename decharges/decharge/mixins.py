from django import http
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import Http404

from decharges.parametre.models import ParametresDApplication
from decharges.user_manager.models import Syndicat


class CheckConfigurationMixin:
    params = None
    federation = None

    def dispatch(self, *args, **kwargs):
        if not self.params:
            self.params = ParametresDApplication.objects.first()
        if not self.federation:
            self.federation = Syndicat.objects.filter(is_superuser=True).first()
        if not self.params or not self.federation:
            return http.HttpResponseBadRequest(
                "Veillez à ce que les ParametresDApplication "
                "et la fédération soient présents en base de données"
            )
        return super().dispatch(*args, **kwargs)


class FederationRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_federation


class CheckTempsEditableMixin:
    params = None
    federation = None

    def dispatch(self, *args, **kwargs):
        if not self.params:
            self.params = ParametresDApplication.objects.first()  # pragma: no cover
        if not self.federation:
            self.federation = Syndicat.objects.filter(
                is_superuser=True
            ).first()  # pragma: no cover
        if self.request.user != self.federation and not self.params.decharges_editables:
            raise Http404()
        return super().dispatch(*args, **kwargs)
