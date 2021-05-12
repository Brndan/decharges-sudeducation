import pandas
from django.contrib import admin

from decharges.decharge.models import Corps, UtilisationTempsDecharge
from decharges.parametre.models import ParametresDApplication


def import_corps(corps_annexe):
    if not corps_annexe:
        return
    document = pandas.read_excel(corps_annexe.read())
    code_corps_to_create = set()
    for line, row in document.iterrows():
        code_corps_to_create.add(str(row[0]).strip().zfill(3))

    existing_code_corps = set(
        Corps.objects.filter(code_corps__in=code_corps_to_create).values_list(
            "code_corps", flat=True
        )
    )
    used_corps_ids = set(
        UtilisationTempsDecharge.objects.all().values_list("corps_id", flat=True)
    )
    Corps.objects.exclude(pk__in=used_corps_ids).exclude(
        code_corps__in=code_corps_to_create
    ).delete()
    Corps.objects.bulk_create(
        [
            Corps(code_corps=code_corps)
            for code_corps in code_corps_to_create - existing_code_corps
        ]
    )


class ParametresDApplicationAdmin(admin.ModelAdmin):
    list_display = ["annee_en_cours", "decharges_editables", "corps_annexe"]

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        import_corps(obj.corps_annexe)


admin.site.register(ParametresDApplication, ParametresDApplicationAdmin)
