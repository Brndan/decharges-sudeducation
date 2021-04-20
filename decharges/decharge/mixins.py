from django import http
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from decharges.parametre.models import ParametresDApplication
from decharges.user_manager.models import Syndicat


class CheckConfigurationMixin:
    params = None
    federation = None

    def dispatch(self, *args, **kwargs):
        self.params = ParametresDApplication.objects.first()
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
