from django.contrib import admin

from decharges.decharge.models import (
    Corps,
    TempsDeDecharge,
    UtilisationCreditDeTempsSyndicalPonctuel,
    UtilisationTempsDecharge,
)


class TempsDeDechargeAdmin(admin.ModelAdmin):
    list_display = [
        "nom_syndicat_beneficiaire",
        "temps_de_decharge_etp",
        "nom_syndicat_donateur",
        "annee",
    ]
    search_fields = [
        "syndicat_beneficiaire__username",
        "syndicat_beneficiaire__academie__nom",
    ]
    list_filter = ["annee"]

    @staticmethod
    def nom_syndicat_beneficiaire(obj):
        return obj.syndicat_beneficiaire.username

    @staticmethod
    def nom_syndicat_donateur(obj):
        if obj.syndicat_donateur:
            return obj.syndicat_donateur.username


class CorpsAdmin(admin.ModelAdmin):
    list_display = ["code_corps", "description"]
    search_fields = ["code_corps", "description"]


class UtilisationTempsDechargeAdmin(admin.ModelAdmin):
    list_display = [
        "nom",
        "prenom",
        "etp_utilises",
        "syndicat",
        "corps",
        "code_etablissement_rne",
        "annee",
    ]
    search_fields = [
        "nom",
        "prenom",
        "syndicat__username",
        "syndicat__academie__nom",
        "corps__code_corps",
        "corps__description",
        "code_etablissement_rne",
    ]
    list_filter = ["annee"]


class UtilisationCreditDeTempsSyndicalPonctuelAdmin(admin.ModelAdmin):
    list_display = ["syndicat", "etp_utilises", "demi_journees_de_decharges", "annee"]
    search_fields = ["syndicat__username", "syndicat__academie__nom"]
    list_filter = ["annee"]


admin.site.register(TempsDeDecharge, TempsDeDechargeAdmin)
admin.site.register(Corps, CorpsAdmin)
admin.site.register(UtilisationTempsDecharge, UtilisationTempsDechargeAdmin)
admin.site.register(
    UtilisationCreditDeTempsSyndicalPonctuel,
    UtilisationCreditDeTempsSyndicalPonctuelAdmin,
)
