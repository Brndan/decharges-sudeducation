from django.core.validators import FileExtensionValidator
from django.db import models


class ParametresDApplication(models.Model):
    """
    Les paramètres de l'application.
    Cet objet ne doit avoir qu'une et une seule instance en base de données.

    C'est grâce à cette instance que le filtrage par année est fait, par exemple pour
    connaitre combien d'ETP un syndicat consomme en décharges.
    """

    annee_en_cours = models.IntegerField(
        verbose_name="Année (en septembre) utilisée pour l'application",
        default=2021,
    )
    decharges_editables = models.BooleanField(
        default=True,
        verbose_name="Les syndicats peuvent-ils accéder à l'édition des décharges ?",
    )
    corps_annexe = models.FileField(
        upload_to="uploads",
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=["ods"])],
    )

    def __str__(self):
        return "Paramètres de l'application"
