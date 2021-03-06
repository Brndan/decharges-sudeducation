from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from decharges.user_manager.models import Academie, Syndicat


class AcademieAdmin(admin.ModelAdmin):
    list_display = ["nom"]
    search_fields = ["nom"]


class SyndicatAdmin(UserAdmin):
    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        self.fieldsets[0][1]["fields"] = ("username", "password", "academie")
        self.list_display = ["username", "email", "academie", "is_staff"]
        self.search_fields = ("username", "email", "academie__nom")


admin.site.register(Syndicat, SyndicatAdmin)
admin.site.register(Academie, AcademieAdmin)
