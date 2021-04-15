import decimal

from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models

from decharges.decharge.validators import validate_first_name, validate_last_name


class TempsDeDecharge(models.Model):
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
    syndicat_donatrice = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Syndicat ayant fait don de temps "
        "(si vide, on considère que cela vient de la fédération)",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="temps_de_decharges_donnes",
    )


class Corps(models.Model):
    code_corps = models.CharField(
        max_length=100,
        unique=True,
        primary_key=True,
        verbose_name="Code corps",
        validators=[
            RegexValidator(
                regex=r"^\d{3}$",
                message="Doit être constitué de 7 lettres majuscules",
                code="invalid_code_corps",
            )
        ],
    )


M = "M."
MME = "MME"

choix_civilite = [
    (M, "M."),
    (MME, "Mme"),
]


class UtilisationTempsDecharge(models.Model):
    civilite = models.CharField(
        verbose_name="Civilité",
        max_length=10,
        choices=choix_civilite,
        default=MME,
    )
    prenom = models.CharField(
        max_length=255, verbose_name="Prénom", validators=[validate_first_name]
    )
    nom = models.CharField(
        max_length=255,
        verbose_name="Nom en MAJUSCULES",
        validators=[validate_last_name],
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
        validators=[
            RegexValidator(
                regex=r"^\d{7}[A-Z]$",
                message="Doit être constitué de 7 chiffres + une lettre majuscule",
                code="invalid_rne",
            )
        ],
    )

    # meta données
    annee = models.IntegerField(
        verbose_name="Année à laquelle le temps de décharge est utilisé",
        default=2021,
    )
    syndicat = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Syndicat qui utilise ce temps",
        on_delete=models.CASCADE,
        related_name="utilisation_temps_de_decharges_par_annee",
    )
    supprime_a = models.DateTimeField(
        verbose_name="La date à laquelle cette débarge a été supprimée",
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
            5,
        )

    class Meta:
        unique_together = ("nom", "prenom", "annee", "syndicat")


class UtilisationCreditDeTempsSyndicalPonctuel(models.Model):
    demi_journees_de_decharges = models.IntegerField(
        verbose_name="Demi-journées de décahrges utilisées",
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
        return round(decimal.Decimal(nb_hours / settings.NB_HOURS_IN_A_YEAR), 5)
