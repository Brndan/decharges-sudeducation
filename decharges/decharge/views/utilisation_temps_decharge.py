from datetime import date

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponse
from django.urls import reverse
from django.views.generic import CreateView, DeleteView, UpdateView

from decharges.decharge.forms import UtilisationTempsDechargeForm
from decharges.decharge.mixins import CheckConfigurationMixin, CheckTempsEditableMixin
from decharges.decharge.models import UtilisationTempsDecharge
from decharges.decharge.views.export_ministere import get_data_frame_ministere
from decharges.user_manager.models import Syndicat


class CreateUtilisationTempsDecharge(
    CheckConfigurationMixin, LoginRequiredMixin, CheckTempsEditableMixin, CreateView
):
    template_name = "decharge/utilisation_temps_decharge_form.html"
    form_class = UtilisationTempsDechargeForm

    def get_success_url(self):
        messages.success(self.request, "Bénéficiaire ajouté·e avec succès !")
        return reverse("decharge:index")

    def form_valid(self, form):
        if self.params.decharges_editables:
            return super().form_valid(form)

        # dans ce cas, la fédération est en train de créer une décharge en cours d'année
        #     on doit donc faire télécharger un fichier ods contenant cet ajout
        annee = self.params.annee_en_cours
        temps_du_beneficiaire = (
            UtilisationTempsDecharge.objects.filter(
                annee=annee,
                nom=form.instance.nom,
                prenom=form.instance.prenom,
                code_etablissement_rne=form.instance.code_etablissement_rne,
                supprime_a__isnull=True,
            )
            .prefetch_related("corps")
            .order_by("nom", "prenom")
        )
        nom_fichier = "ajout"
        if temps_du_beneficiaire.exists():
            nom_fichier = "modification"
        super().form_valid(form)
        response = HttpResponse("", content_type="application/force-download")
        data_frame = get_data_frame_ministere(temps_du_beneficiaire)
        data_frame.to_excel(response, engine="odf", index=False)
        today = date.today()
        response[
            "Content-Disposition"
        ] = f"attachment; filename=SUD éducation - {nom_fichier} - {today}.ods"
        return response

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        default_syndicat = self.request.GET.get("syndicat")
        if default_syndicat:
            default_syndicat = Syndicat.objects.filter(
                username=default_syndicat
            ).first()
        form_kwargs["syndicat"] = default_syndicat or self.request.user
        form_kwargs["annee"] = self.params.annee_en_cours
        form_kwargs["decharges_editables"] = self.params.decharges_editables
        form_kwargs["corps_annexe"] = self.params.corps_annexe
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

    def form_valid(self, form):
        if self.params.decharges_editables:
            return super().form_valid(form)

        # dans ce cas, la fédération est en train de modifier une décharge en cours d'année
        #     on doit donc faire télécharger un fichier ods contenant le nouvel
        annee = self.params.annee_en_cours
        super().form_valid(form)
        response = HttpResponse("", content_type="application/force-download")
        temps_du_beneficiaire = (
            UtilisationTempsDecharge.objects.filter(
                annee=annee,
                nom=form.instance.nom,
                prenom=form.instance.prenom,
                code_etablissement_rne=form.instance.code_etablissement_rne,
                supprime_a__isnull=True,
            )
            .prefetch_related("corps")
            .order_by("nom", "prenom")
        )
        data_frame = get_data_frame_ministere(temps_du_beneficiaire)
        data_frame.to_excel(response, engine="odf", index=False)
        today = date.today()
        response[
            "Content-Disposition"
        ] = f"attachment; filename=SUD éducation - modification - {today}.ods"
        return response

    def get_success_url(self):
        messages.success(self.request, "Bénéficiaire mis·e à jour avec succès !")
        return reverse("decharge:index")

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs["syndicat"] = self.object.syndicat
        form_kwargs["annee"] = self.object.annee
        form_kwargs["decharges_editables"] = self.params.decharges_editables
        form_kwargs["corps_annexe"] = self.params.corps_annexe
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

    def delete(self, request, *args, **kwargs):
        if self.params.decharges_editables:
            return super().delete(request, *args, **kwargs)

        # dans ce cas, la fédération est en train de créer une décharge en cours d'année
        #     on doit donc faire télécharger un fichier ods contenant cet ajout
        self.object = self.get_object()
        annee = self.params.annee_en_cours
        temps_du_beneficiaire_avant_suppression = (
            UtilisationTempsDecharge.objects.filter(
                annee=annee,
                nom=self.object.nom,
                prenom=self.object.prenom,
                code_etablissement_rne=self.object.code_etablissement_rne,
                supprime_a__isnull=True,
            )
            .prefetch_related("corps")
            .order_by("nom", "prenom")
        )
        nom_fichier = "suppression"
        data_frame = get_data_frame_ministere(temps_du_beneficiaire_avant_suppression)
        super().delete(request, *args, **kwargs)
        temps_du_beneficiaire_apres_suppression = (
            UtilisationTempsDecharge.objects.filter(
                annee=annee,
                nom=self.object.nom,
                prenom=self.object.prenom,
                code_etablissement_rne=self.object.code_etablissement_rne,
                supprime_a__isnull=True,
            )
            .prefetch_related("corps")
            .order_by("nom", "prenom")
        )
        response = HttpResponse("", content_type="application/force-download")
        if temps_du_beneficiaire_apres_suppression.exists():
            nom_fichier = "modification"
            data_frame = get_data_frame_ministere(
                temps_du_beneficiaire_apres_suppression
            )

        data_frame.to_excel(response, engine="odf", index=False)
        today = date.today()
        response[
            "Content-Disposition"
        ] = f"attachment; filename=SUD éducation - {nom_fichier} - {today}.ods"
        return response

    def get_success_url(self):
        messages.success(self.request, "Bénéficiaire retiré·e avec succès !")
        return reverse("decharge:index")
