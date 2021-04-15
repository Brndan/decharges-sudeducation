import re

from django.core.exceptions import ValidationError

CHARSET_REGEX = re.compile("[^a-zàâçéèêëîïôûùüÿñæœ -]", flags=re.IGNORECASE)


def validate_first_name(first_name):
    """
    - Commence par une majuscule
    - pas d'espace au début
    - pas deux espaces consécutifs
    - pas d'espace à la fin
    - une liste de caractères limitée
    :param first_name:
    :raises: a `ValidationError` if the first_name doesn't match the rules
    """
    if first_name[0].upper() != first_name[0]:
        raise ValidationError(
            "Le prénom doit commencer par une majuscule",
        )
    if first_name[0] == " ":
        raise ValidationError(
            "Le prénom ne peut pas commencer par un espace",
        )
    if "  " in first_name:
        raise ValidationError(
            "Le prénom ne doit pas contenir 2 espaces consécutifs",
        )
    if first_name.endswith(" "):
        raise ValidationError(
            "Le prénom ne doit pas se terminer par un espace",
        )
    unknown_chars = CHARSET_REGEX.search(first_name)
    if unknown_chars:
        raise ValidationError(
            f"Des caractères non-autorisés sont présents : {unknown_chars.group(0)}",
        )


def validate_last_name(last_name):
    """
    - tout en majuscule
    - pas d'espace au début
    - pas deux espaces consécutifs
    - pas d'espace à la fin
    - une liste de caractères limitée
    :param last_name:
    :raises: a `ValidationError` if the first_name doesn't match the rules
    """
    if last_name.upper() != last_name:
        raise ValidationError(
            "Le nom doit être en majuscule",
        )
    if last_name[0] == " ":
        raise ValidationError(
            "Le nom ne peut pas commencer par un espace",
        )
    if "  " in last_name:
        raise ValidationError(
            "Le nom ne doit pas contenir 2 espaces consécutifs",
        )
    if last_name.endswith(" "):
        raise ValidationError(
            "Le nom ne doit pas se terminer par un espace",
        )
    unknown_chars = CHARSET_REGEX.search(last_name)
    if unknown_chars:
        raise ValidationError(
            f"Des caractères non-autorisés sont présents : {unknown_chars.group(0)}",
        )
