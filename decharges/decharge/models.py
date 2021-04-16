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
    (MME, "Mme"),
]


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
    # TODO: dans le formulaire, faire en sorte de réduire les choix
    #       de heures_d_obligation_de_service à 15, 18, 27, 35, 36, 1607 (configurable)
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
        if self.etp:
            # self.etp peut être renseigné dans le cas où l'objet vient de
            # l'import de l'historique des décharges
            return self.etp
        # heures_de_decharges only has 5 decimal places, so we round it up to 5 too
        return round(
            decimal.Decimal(
                self.heures_de_decharges / self.heures_d_obligation_de_service
            ),
            settings.PRECISION_ETP,
        )

    class Meta:
        unique_together = ("nom", "prenom", "annee", "syndicat")


class UtilisationCreditDeTempsSyndicalPonctuel(models.Model):
    """
    Utilisation des CTS (ou CHS), sur une année donnée, par syndicat
    """

    demi_journees_de_decharges = models.IntegerField(
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
