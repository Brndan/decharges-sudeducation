from django.contrib import admin

from decharges.decharge.models import (
    TempsDeDecharge,
    Corps,
    UtilisationTempsDecharge,
    UtilisationCreditDeTempsSyndicalPonctuel,
)


class TempsDeDechargeAdmin(admin.ModelAdmin):
    list_display = [
        "username_syndicat_beneficiaire",
        "temps_de_decharge_etp",
        "username_syndicat_donateur",
        "annee",
    ]
    search_fields = ["syndicat_beneficiaire__username"]
    list_filter = ["annee"]

    @staticmethod
    def username_syndicat_beneficiaire(obj):
        return obj.syndicat_beneficiaire.username

    @staticmethod
    def username_syndicat_donateur(obj):
        if obj.syndicat_donateur:
            return obj.syndicat_donateur.username


class CorpsAdmin(admin.ModelAdmin):
    list_display = ["code_corps"]
    search_fields = ["code_corps"]


admin.site.register(TempsDeDecharge, TempsDeDechargeAdmin)
admin.site.register(Corps, CorpsAdmin)
admin.site.register(UtilisationTempsDecharge)
admin.site.register(UtilisationCreditDeTempsSyndicalPonctuel)
