from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models


class Academie(models.Model):
    nom = models.CharField(verbose_name="Nom de l'académie", max_length=255)


class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of username.
    """

    def create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError("The Email must be set")  # pragma: no cover
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")  # pragma: no cover
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(
                "Superuser must have is_superuser=True."
            )  # pragma: no cover
        return self.create_user(email, password, **extra_fields)


class Syndicat(AbstractUser):
    username = models.CharField(
        "Nom d'utilisateur", max_length=150, null=True, blank=True
    )
    email = models.EmailField("Email principal", unique=True, db_index=True)
    academie = models.ForeignKey(
        Academie,
        null=True,  # la fédération n'a pas d'académie liée
        blank=True,
        verbose_name="Académie dont le syndicat fait partie",
        on_delete=models.SET_NULL,
        related_name="syndicats_membres",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]
    objects = CustomUserManager()
