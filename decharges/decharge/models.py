import datetime
import decimal

from django.conf import settings
from django.db import models

from decharges.decharge.validators import (
    code_corps_validator,
    rne_validator,
    validate_first_name,
    validate_last_name,
)


class TempsDeDecharge(models.Model):
    """
    Temps de décharge attribué à un syndicat en début d'année.

    - Ce temps est exprimé en ETP
    - Il est appliqué sur une année donnée (self.annee) et les calculs se basent sur
      l'année dans `parametre.models.ParametresDApplication` pour filtrer
    - Le syndicat donnateur peut être soit la fédération (c'est le défaut),
      soit un autre syndicat (cas spécifique de don de décharge intra-académie)
    """

    syndicat_beneficiaire = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Syndicat bénéficiaire",
        on_delete=models.CASCADE,
        related_name="temps_de_decharges_par_annee",
    )
    annee = models.IntegerField(
        verbose_name="Année à laquelle le temps de décharge est attribué",
        default=2021,
    )
    temps_de_decharge_etp = models.DecimalField(
        verbose_name="Temps de décharge en ETP",
        default=0,
        decimal_places=5,
        max_digits=8,
    )  # précision max: 999.99999
    syndicat_donateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Syndicat ayant fait don de temps "
        "(si vide, on considère que cela vient de la fédération)",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="temps_de_decharges_donnes",
    )

    def __str__(self):
        return (
            f"{self.temps_de_decharge_etp} ETP à {self.syndicat_beneficiaire.username} "
            f"en {self.annee}"
        )

    class Meta:
        unique_together = ("annee", "syndicat_donateur", "syndicat_beneficiaire")


class Corps(models.Model):
    code_corps = models.CharField(
        max_length=100,
        unique=True,
        primary_key=True,
        verbose_name="Code corps",
        validators=[code_corps_validator],
    )  # example: 553, 615 etc..
    description = models.CharField(
        verbose_name="Description du Corps",
        max_length=255,
        null=True,
        blank=True,
    )

    def __str__(self):
        if self.description:
            return f"{self.code_corps} ({self.description})"
        return self.code_corps

    class Meta:
        verbose_name = "Corps"
        verbose_name_plural = "Corps"
        ordering = ["code_corps"]


M = "M."
MME = "MME"

choix_civilite = [
    (M, "M."),
    (MME, "MME"),
]

CIVILITE_AFFICHEE = {key: value for key, value in choix_civilite}


class UtilisationTempsDecharge(models.Model):
    """
    Utilisation des temps de décharges par les syndiqués

    - cette utilisation est historisé par année
    - des validations sont appliquées sur les champs, cf **validators.py**
    - cette utilisation de temps de décharge peut être exceptionnellement
      modifiée/ajoutée/supprimée au cours de l'année par la fédération. Les champs
        - `self.supprime_a`
        - `self.cree_a`
        - `self.modifie_a`
        - `self.commentaire_de_mise_a_jour`
      permettront à la fédération d'avoir le maximum d'information sur ces mises à jours
    - L'utilisation de temps de décharge peut soit être une décharge locale, soit une décharge
      fédérale et Solidaires. `self.syndicat` permet de différencier les deux cas
    """

    civilite = models.CharField(
        verbose_name="Civilité",
        max_length=10,
        choices=choix_civilite,
        default=MME,
    )
    prenom = models.CharField(
        max_length=255,
        verbose_name="Prénom",
        validators=[validate_first_name],
        db_index=True,
    )
    nom = models.CharField(
        max_length=255,
        verbose_name="Nom en MAJUSCULES",
        validators=[validate_last_name],
        db_index=True,
    )
    heures_de_decharges = models.DecimalField(
        verbose_name="Temps de décharge utilisées en heures",
        default=0,
        decimal_places=5,
        max_digits=8,
    )  # précision max: 999.99999
    heures_d_obligation_de_service = models.IntegerField(
        verbose_name="Heures d'obligations de service",
        default=0,
    )
    corps = models.ForeignKey(
        Corps,
        verbose_name="Corps",
        on_delete=models.SET_NULL,
        null=True,
    )
    code_etablissement_rne = models.CharField(
        max_length=255,
        verbose_name="Code d'établissement (RNE)",
        validators=[rne_validator],
        db_index=True,
    )

    # meta données
    annee = models.IntegerField(
        verbose_name="Année à laquelle le temps de décharge est utilisé",
        default=2021,
        db_index=True,
    )
    date_debut_decharge = models.DateField(
        verbose_name="Date à laquelle la décharge commence",
        null=True,
        blank=True,
    )
    date_fin_decharge = models.DateField(
        verbose_name="Date à laquelle la décharge se termine",
        null=True,
        blank=True,
    )
    syndicat = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Syndicat qui utilise ce temps",
        on_delete=models.CASCADE,
        related_name="utilisation_temps_de_decharges_par_annee",
    )  # si le syndicat est la fédération, c'est donc une décharge fédérale
    supprime_a = models.DateTimeField(
        verbose_name="La date à laquelle cette décharge a été supprimée",
        null=True,
        blank=True,
    )
    cree_a = models.DateTimeField(
        null=True, blank=True, auto_now_add=True, verbose_name="Date de création"
    )
    modifie_a = models.DateTimeField(
        null=True, blank=True, auto_now=True, verbose_name="Date de mise à jour"
    )
    commentaire_de_mise_a_jour = models.TextField(
        null=True,
        blank=True,
        verbose_name="Historique des modifications",
        help_text="Décrivez factuellement la modification apportée",
    )
    est_une_decharge_solidaires = models.BooleanField(
        default=False,
        verbose_name="Est une décharge solidaires",
        help_text="Cocher cette case uniquement si la décharge "
        "vient d'un autre syndicat que SUD éducation",
    )

    # données importées de l'historique
    etp = models.DecimalField(
        verbose_name="ETP consommé",
        help_text="Ne pas utiliser, présent pour des raisons historiques",
        default=0,
        decimal_places=5,
        max_digits=6,
        blank=True,
    )  # max: 9.99999

    @property
    def etp_utilises(self) -> decimal.Decimal:
        if self.heures_de_decharges != 0 and self.heures_d_obligation_de_service != 0:
            # heures_de_decharges only has 5 decimal places, so we round it up to 5 too
            return round(
                decimal.Decimal(
                    self.heures_de_decharges / self.heures_d_obligation_de_service
                )
                * self.etp_prorata,
                settings.PRECISION_ETP,
            )

        # self.etp peut être renseigné dans le cas où l'objet vient de
        # l'import de l'historique des décharges
        return round(self.etp * self.etp_prorata, settings.PRECISION_ETP)

    @property
    def heures_pleines_de_decharges(self) -> int:
        return int(self.heures_de_decharges)

    @property
    def minutes_de_decharges(self) -> int:
        return int(
            round((self.heures_de_decharges - self.heures_pleines_de_decharges) * 60)
        )

    @property
    def etp_prorata(self) -> decimal.Decimal:
        debut_de_lannee = datetime.date(year=self.annee, month=9, day=1)
        fin_de_lannee = datetime.date(year=self.annee + 1, month=8, day=31)
        date_fin_decharge = self.date_fin_decharge or fin_de_lannee
        date_debut_decharge = self.date_debut_decharge or debut_de_lannee
        nb_jours_annee = fin_de_lannee - debut_de_lannee + datetime.timedelta(days=1)
        nb_jours_decharge = (
            date_fin_decharge - date_debut_decharge + datetime.timedelta(days=1)
        )
        return decimal.Decimal(nb_jours_decharge / nb_jours_annee)

    class Meta:
        unique_together = (
            "nom",
            "prenom",
            "annee",
            "code_etablissement_rne",
            "syndicat",
            "est_une_decharge_solidaires",
        )


class UtilisationCreditDeTempsSyndicalPonctuel(models.Model):
    """
    Utilisation des CTS (ou CHS), sur une année donnée, par syndicat
    """

    demi_journees_de_decharges = models.PositiveIntegerField(
        verbose_name="Demi-journées de décharges utilisées",
        default=0,
    )
    annee = models.IntegerField(
        verbose_name="Année à laquelle le temps de décharge est utilisé",
        default=2021,
    )
    syndicat = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Syndicat qui utilise ce temps",
        on_delete=models.CASCADE,
        related_name="utilisation_cts_ponctuels_par_annee",
    )

    class Meta:
        unique_together = ("annee", "syndicat")

    @property
    def etp_utilises(self) -> decimal.Decimal:
        nb_days = self.demi_journees_de_decharges / 2
        nb_hours = nb_days * 7
        return round(
            decimal.Decimal(nb_hours / settings.NB_HOURS_IN_A_YEAR),
            settings.PRECISION_ETP,
        )
