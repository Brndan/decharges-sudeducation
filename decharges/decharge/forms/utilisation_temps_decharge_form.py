import os

from django import forms
from django.conf import settings

from decharges.decharge.models import UtilisationTempsDecharge
from decharges.decharge.views.utils import calcul_repartition_temps
from decharges.user_manager.models import Syndicat


class UtilisationTempsDechargeForm(forms.ModelForm):
    heures_d_obligation_de_service = forms.ChoiceField(
        label="Heures d'obligations de service", choices=settings.CHOIX_ORS
    )
    heures_de_decharges = forms.IntegerField(
        label="Heures de décharge utilisées", min_value=0, initial=0
    )
    minutes_de_decharges = forms.IntegerField(
        label="Minutes de décharge utilisées",
        min_value=0,
        max_value=59,
        required=False,
        initial=0,
    )

    def __init__(self, *args, **kwargs):
        self.syndicat = kwargs.pop("syndicat")
        self.annee = kwargs.pop("annee")
        self.decharges_editables = kwargs.pop("decharges_editables")
        self.corps_annexe = kwargs.pop("corps_annexe")
        self.federation = kwargs.pop("federation")
        super().__init__(*args, **kwargs)
        self.fields["prenom"].label = "Prénom"
        self.fields["prenom"].help_text = (
            "- Doit commencer par une Majuscule <br>"
            "- Ne doit pas commencer ou finir par un espace <br>"
            "- Ne doit pas contenir 2 espaces consécutifs <br>"
            "- Ne doit pas contenir de caractères spéciaux"
        )
        self.fields["prenom"].widget.attrs["placeholder"] = "ex : Michelle"
        self.fields["nom"].label = "Nom"
        self.fields["nom"].widget.attrs["placeholder"] = "ex : MARTIN"
        self.fields["nom"].help_text = (
            "- Doit être en MAJUSCULE <br>"
            "- Ne doit pas commencer ou finir par un espace <br>"
            "- Ne doit pas contenir 2 espaces consécutifs <br>"
            "- Ne doit pas contenir de caractères spéciaux"
        )
        self.fields[
            "code_etablissement_rne"
        ].help_text = (
            "Le code établissement d'affectation (7 chiffres et une lettre majuscule)"
        )
        self.fields["code_etablissement_rne"].widget.attrs[
            "placeholder"
        ] = "ex: 1234567A"

        if not self.decharges_editables:
            # la fédération peut choisir le syndicat qui utilise la décharge dans le formulaire
            self.fields["syndicat"] = forms.ModelChoiceField(
                label="Syndicat qui utilise ce temps",
                queryset=Syndicat.objects.all().order_by("username"),
                initial=self.syndicat,
            )
            if self.instance.pk:
                self.fields["prenom"].widget.attrs["readonly"] = True
                self.fields["nom"].widget.attrs["readonly"] = True
                self.fields["code_etablissement_rne"].widget.attrs["readonly"] = True
            self.fields["commentaire_de_mise_a_jour"] = forms.CharField(
                label="Pourquoi cette mise à jour en cours d'année ?",
                widget=forms.Textarea(),
                initial=self.instance.commentaire_de_mise_a_jour,
            )

        if self.corps_annexe:
            self.fields["corps"].help_text = (
                f"Voir <a href='{self.corps_annexe.url}' target='_blank'>"
                f"{os.path.basename(self.corps_annexe.name)} "
                f"<span class='fa fa-external-link-alt fa-xs'></span>"
                "</a> (cliquer sur le lien ne quitte pas la page actuelle)"
            )

        if self.federation == self.syndicat:
            self.fields["est_une_decharge_solidaires"] = forms.BooleanField(
                label="Est une décharge solidaires",
                help_text="Cocher cette case uniquement si la décharge vient d'un autre syndicat que SUD éducation",
                initial=self.instance.est_une_decharge_solidaires,
                required=False,
            )

        self.fields["heures_de_decharges"].initial = int(
            self.instance.heures_de_decharges
        )
        self.fields["minutes_de_decharges"].initial = round(
            (
                self.instance.heures_de_decharges
                - self.fields["heures_de_decharges"].initial
            )
            * 60
        )

    def _populate_instance(self):
        if self.decharges_editables:
            self.instance.syndicat = self.syndicat
        else:
            # la fédération peut choisir le syndicat qui utilise la décharge dans le formulaire
            self.instance.syndicat = self.cleaned_data["syndicat"]
            self.instance.commentaire_de_mise_a_jour = self.cleaned_data.get(
                "commentaire_de_mise_a_jour"
            )
        self.instance.annee = self.annee
        self.instance.heures_de_decharges = self.cleaned_data["heures_de_decharges"]
        self.instance.est_une_decharge_solidaires = self.cleaned_data.get(
            "est_une_decharge_solidaires", False
        )
        if self.cleaned_data["minutes_de_decharges"]:
            self.instance.heures_de_decharges += (
                self.cleaned_data["minutes_de_decharges"] / 60
            )

    def validate_unique(self):
        exclude = self._get_validation_exclusions()
        exclude = set(exclude) - {
            "id",
            "annee",
            "syndicat",
            "est_une_decharge_solidaires",
            "nom",
            "prenom",
            "code_etablissement_rne",
        }
        try:
            self.instance.validate_unique(exclude=exclude)
        except forms.ValidationError:
            self._update_errors(
                forms.ValidationError(
                    "Une décharge pour cette ou ce bénéficiaire existe déjà, "
                    "veuillez plutôt la mettre à jour"
                )
            )

    def full_clean(self):
        super().full_clean()
        (_, _, _, _, _, _, temps_restant, _, _,) = calcul_repartition_temps(
            self.annee,
            self.federation,
            self.instance.syndicat,
            excluded_utilisation_temps_de_decharge_pk=self.instance.pk,
        )

        # vérification si la décharge ne fait pas dépasser le quota de décharge du syndicat
        if (
            not self.instance.est_une_decharge_solidaires
            and temps_restant - self.instance.etp_utilises < 0
            and hasattr(self, "cleaned_data")
        ):
            self.add_error(
                None,
                f"Vous dépassez le quota du syndicat, il reste {temps_restant:.3f} ETP "
                f"attribuable et vous essayez d'ajouter {self.instance.etp_utilises:.3f} ETP",
            )

        # vérification si la décharge ne fait pas dépasser le quota de décharge du bénéficiaire

        # 0.5 ETP dans l'année courante ?
        decharges_annee_en_cours = UtilisationTempsDecharge.objects.filter(
            nom=self.instance.nom,
            prenom=self.instance.prenom,
            annee=self.instance.annee,
            code_etablissement_rne=self.instance.code_etablissement_rne,
        ).exclude(pk=self.instance.pk)
        etp_consommes = sum(
            decharge.etp_utilises for decharge in decharges_annee_en_cours
        )
        temps_restant_beneficiaire = settings.MAX_ETP_EN_UNE_ANNEE - etp_consommes
        if temps_restant_beneficiaire < self.instance.etp_utilises:
            self.add_error(
                None,
                "Vous dépassez le quota du bénéficiaire, il lui reste au maximum "
                f"{temps_restant_beneficiaire:.3f} ETP à consommer "
                f"et vous essayez de lui ajouter {self.instance.etp_utilises:.3f} ETP",
            )

        historique_decharges_beneficiaire = (
            UtilisationTempsDecharge.objects.filter(
                nom=self.instance.nom,
                prenom=self.instance.prenom,
                code_etablissement_rne=self.instance.code_etablissement_rne,
            )
            .exclude(pk=self.instance.pk)
            .order_by("-annee")
        )
        etp_consecutifs = 0
        annees_consecutives = 0
        annee_courante = self.instance.annee
        for decharge in historique_decharges_beneficiaire:
            if (
                annee_courante - decharge.annee
                > settings.NB_ANNEES_POUR_REINITIALISER_LES_COMPTEURS
            ):
                break
            l_annee_a_changee = decharge.annee != annee_courante
            annee_courante = decharge.annee
            if l_annee_a_changee:
                annees_consecutives += 1
            etp_consecutifs += decharge.etp_utilises

        # 8 années consécutives ?
        if annees_consecutives >= settings.MAX_ANNEES_CONSECUTIVES:
            self.add_error(
                None,
                f"La ou le bénéficiaire cumule déjà {settings.MAX_ANNEES_CONSECUTIVES} "
                "années consécutives de décharges, il ou elle ne peut donc pas bénéficier de "
                "décharges cette année",
            )

        # 3 ETP consécutifs ?
        if etp_consecutifs + self.instance.etp_utilises >= settings.MAX_ETP_CONSECUTIFS:
            self.add_error(
                None,
                f"La ou le bénéficiaire cumule déjà {etp_consecutifs:.3f}ETP "
                "consécutifs de décharges sur les dernières années (+l'année en cours) et vous"
                f" essayez de rajouter {self.instance.etp_utilises:.3f}ETP",
            )

    def clean(self):
        self._populate_instance()
        cleaned_data = super().clean()
        if cleaned_data.get(
            "est_une_decharge_solidaires"
        ) and self.federation != cleaned_data.get("syndicat", self.syndicat):
            self.add_error(
                "est_une_decharge_solidaires",
                "La décharge ne peut provenir d'un autre syndicat uniquement pour les décharges fédérales",
            )

        return cleaned_data

    class Meta:
        model = UtilisationTempsDecharge
        fields = [
            "civilite",
            "prenom",
            "nom",
            "heures_d_obligation_de_service",
            "corps",
            "code_etablissement_rne",
        ]
