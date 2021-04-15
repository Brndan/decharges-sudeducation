from django.contrib import admin

from decharges.parametre.models import ParametresDApplication


class ParametresDApplicationAdmin(admin.ModelAdmin):
    list_display = ["annee_en_cours", "decharges_editables"]


admin.site.register(ParametresDApplication, ParametresDApplicationAdmin)
