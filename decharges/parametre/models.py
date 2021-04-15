from django.conf import settings
from django.db import models


class ParametresDApplication(models.Model):
    annee_en_cours = models.IntegerField(
        verbose_name="Année (en septembre) utilisée pour l'application",
        default=2021,
    )
    decharges_editables = models.BooleanField(
        default=True,
        verbose_name="Les syndicats peuvent-elles accéder à l'édition des décharges ?",
    )
