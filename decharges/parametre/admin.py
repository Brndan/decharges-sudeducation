from django.contrib import admin

from decharges.parametre.models import ParametresDApplication


class ParametresDApplicationAdmin(admin.ModelAdmin):
    list_display = ["annee_en_cours", "decharges_editables", "corps_annexe"]

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False


admin.site.register(ParametresDApplication, ParametresDApplicationAdmin)
