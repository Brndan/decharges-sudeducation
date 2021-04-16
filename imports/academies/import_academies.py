from decharges.user_manager.models import *

with open("imports/academies.csv") as f:
    academies = f.read()

academies_list = academies.split("\n")

for i, academie in enumerate(academies_list):
    academie_nom, syndicat_nom = academie.split(",")
    academ, _ = Academie.objects.get_or_create(nom=academie_nom)
    syndicat = Syndicat.objects.create(
        academie=academ, username=syndicat_nom, email=f"changeme{i}@example.com"
    )
